"""Compute the coherence endpoints from Inspect eval logs.

UNVERIFIED AGAINST REAL LOGS -- written before the first run, so the log-reading
half is the part most likely to need fixing. The arithmetic below is covered by
tests; the extraction is not.

Usage:
    python scripts/analyze_coherence.py logs/
    python scripts/analyze_coherence.py logs/ --csv results/coherence.csv
    python scripts/analyze_coherence.py logs/r13 --csv results/r13.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import wtp  # noqa: E402
from src.schema import load_benchmarks, load_scenarios, parse_dollars  # noqa: E402

CHANGES = ("min2", "one_level", "min3")
PARSE_GATE = 0.80
L_LOW, L_HIGH = 0.75, 1.33
N_BOOT = 2000
BOOT_SEED = 13  # fixed so the intervals in RESULTS.md reproduce


def _frame_of(row: dict) -> str:
    return str(row.get("frame") or "advisor")


def _median(values: list[float]) -> float:
    values = sorted(values)
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


def open_ended_draws(
    rows: list[dict], model: str, frame: str
) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if (
            row["model"] == model
            and _frame_of(row) == frame
            and row.get("format") == "open_ended"
            and row.get("wtp") is not None
        ):
            grouped[str(row["scenario_id"])].append(float(row["wtp"]))
    return grouped


def parse_counts(
    rows: list[dict], model: str, frame: str, fmt: str = "open_ended"
) -> tuple[int, int]:
    subset = [
        r
        for r in rows
        if r["model"] == model
        and _frame_of(r) == frame
        and r.get("format") == fmt
    ]
    parsed = sum(1 for r in subset if r.get("wtp") is not None)
    return parsed, len(subset)


def level_shift_L(
    advisor: dict[str, list[float]],
    persona: dict[str, list[float]],
    *,
    n_boot: int = N_BOOT,
    rng: random.Random | None = None,
) -> dict:
    """Geometric-mean persona/advisor ratio over cells, plus a bootstrap CI."""
    cells = sorted(set(advisor) & set(persona))
    used: list[str] = []
    dropped: list[str] = []
    logs: list[float] = []
    for sid in cells:
        a_med = _median(advisor[sid])
        p_med = _median(persona[sid])
        if a_med == 0 or p_med == 0:
            dropped.append(sid)
            continue
        used.append(sid)
        logs.append(math.log(p_med / a_med))
    empty = {
        "L": None,
        "lo": None,
        "hi": None,
        "used": used,
        "dropped": dropped,
        "label": None,
    }
    if not used:
        return empty
    L = math.exp(sum(logs) / len(logs))
    rng = rng or random.Random(BOOT_SEED)
    boots: list[float] = []
    for _ in range(n_boot):
        br: list[float] = []
        skip = False
        for sid in used:
            a_s = [rng.choice(advisor[sid]) for _ in advisor[sid]]
            p_s = [rng.choice(persona[sid]) for _ in persona[sid]]
            am, pm = _median(a_s), _median(p_s)
            if am == 0 or pm == 0:
                skip = True
                break
            br.append(math.log(pm / am))
        if not skip and br:
            boots.append(math.exp(sum(br) / len(br)))
    boots.sort()
    if boots:
        lo = boots[int(0.025 * (len(boots) - 1))]
        hi = boots[int(0.975 * (len(boots) - 1))]
    else:
        lo = hi = None
    if L < L_LOW:
        label = "B. Drop"
    elif L > L_HIGH:
        label = "C. Rise"
    else:
        label = "A. No change"
    return {
        "L": L,
        "lo": lo,
        "hi": hi,
        "used": used,
        "dropped": dropped,
        "label": label,
    }


def collect(log_dir: Path) -> list[dict]:
    """Flatten every sample in every log into one row per generation."""
    rows: list[dict] = []
    for info in list_eval_logs(str(log_dir)):
        log = read_eval_log(info)
        if log.status != "success" or not log.samples:
            print(f"  skipping {info.name}: status={log.status}", file=sys.stderr)
            continue
        model = log.eval.model
        for sample in log.samples:
            for score in (sample.scores or {}).values():
                meta = score.metadata or {}
                if "scenario_id" not in meta:
                    continue
                row = {"model": model, **meta}
                # Re-parse open-ended from raw so last-dollar scoring applies to
                # already-scored logs (Sonnet wrote an essay; first $ was income).
                if row.get("format") == "open_ended" and row.get("raw"):
                    reparsed = parse_dollars(str(row["raw"]))
                    if reparsed is not None:
                        row["wtp_first_pass"] = row.get("wtp")
                        row["wtp"] = reparsed
                rows.append(row)
    return rows


def referendum_wtp(rows: list[dict]) -> dict[tuple[str, str], wtp.WTPEstimate]:
    grouped: dict[tuple[str, str], tuple[list[int], list[bool | None]]] = defaultdict(
        lambda: ([], [])
    )
    for row in rows:
        if row.get("format") != "referendum":
            continue
        bids, votes = grouped[(row["model"], row["scenario_id"])]
        bids.append(int(row["bid"]))
        votes.append(row.get("vote"))
    return {key: wtp.estimate(b, v) for key, (b, v) in grouped.items()}


def direct_wtp(rows: list[dict]) -> dict[tuple[str, str, str, str], float]:
    """(model, scenario, format, frame) -> median of parsed amounts."""
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        fmt = row.get("format")
        if fmt in ("open_ended", "interval") and row.get("wtp") is not None:
            grouped[(row["model"], row["scenario_id"], fmt, _frame_of(row))].append(
                float(row["wtp"])
            )
    return {key: _median(values) for key, values in grouped.items()}


def primary_wtp(
    model: str,
    sid: str,
    ref: dict[tuple[str, str], wtp.WTPEstimate],
    direct: dict[tuple[str, str, str, str], float],
    frame: str = "advisor",
) -> tuple[float | None, str | None]:
    """Prefer referendum, then open-ended, then interval. This week's pilot is OE."""
    est = ref.get((model, sid))
    if est is not None and est.preferred is not None:
        return est.preferred, "referendum"
    for fmt in ("open_ended", "interval"):
        value = direct.get((model, sid, fmt, frame))
        if value is not None:
            return value, fmt
    if est is not None and est.censored:
        return None, "censored"
    return None, None


def report(rows: list[dict]) -> list[dict]:
    scenarios = {s.id: s for s in load_scenarios()}
    bench = load_benchmarks()
    ref = referendum_wtp(rows)
    direct = direct_wtp(rows)
    models = sorted({r["model"] for r in rows})
    units = sorted({s.spatial_unit + "|" + s.locality for s in scenarios.values()})

    out: list[dict] = []
    outcomes: dict[str, str] = {}
    for model in models:
        frames = sorted({_frame_of(r) for r in rows if r["model"] == model})
        multi = len(frames) > 1
        for frame in frames:
            header = f"{model} / {frame}" if multi else model
            print(f"\n=== {header} ===")

            # --- criterion: level comparison against published means -------- #
            print("\n  scenario                        model    human (SE)   ratio  source")
            for sid in scenarios:
                value, source = primary_wtp(model, sid, ref, direct, frame)
                est = ref.get((model, sid))
                b = bench[sid]
                if value is not None:
                    shown = f"{value:8.0f}"
                    ratio = f"{value / b.mean:6.2f}"
                elif source == "censored":
                    shown, ratio = "  censored", "     -"
                else:
                    shown, ratio = "         -", "     -"
                src = source or "-"
                print(f"  {sid:<30} {shown}  {b.mean:5.0f} ({b.stderr:2.0f}) {ratio}  {src}")
                out.append(
                    {
                        "model": model,
                        "frame": frame,
                        "scenario_id": sid,
                        "wtp_primary": value,
                        "primary_source": source,
                        "wtp_referendum": est.preferred if est else None,
                        "wtp_turnbull": est.turnbull_mean if est else None,
                        "wtp_open_ended": direct.get((model, sid, "open_ended", frame)),
                        "wtp_interval_p50": direct.get((model, sid, "interval", frame)),
                        "human_mean": b.mean,
                        "human_stderr": b.stderr,
                        "censored": est.censored if est else None,
                    }
                )

            def _val(sid: str) -> float | None:
                return primary_wtp(model, sid, ref, direct, frame)[0]

            # --- nested dominance ------------------------------------------ #
            print("\n  nested dominance (min2 must be >= min3):")
            for key in units:
                unit, locality = key.split("|")
                suffix = _suffix(unit, locality)
                a, b_ = _val(f"min2{suffix}"), _val(f"min3{suffix}")
                if a is None or b_ is None:
                    print(f"    {suffix.lstrip('_'):<24} insufficient data")
                    continue
                ok = a >= b_
                print(
                    f"    {suffix.lstrip('_'):<24} {a:6.0f} vs {b_:6.0f}"
                    f"  {'ok' if ok else 'VIOLATION'}"
                )

            # --- scope ordering -------------------------------------------- #
            print("\n  scope ordering (min2 > one_level > min3):")
            for key in units:
                unit, locality = key.split("|")
                suffix = _suffix(unit, locality)
                values = [_val(f"{c}{suffix}") for c in CHANGES]
                if any(v is None for v in values):
                    print(f"    {suffix.lstrip('_'):<24} insufficient data")
                    continue
                ok = values[0] > values[1] > values[2]
                rendered = " > ".join(f"{v:.0f}" for v in values)
                print(f"    {suffix.lstrip('_'):<24} {rendered}  {'ok' if ok else 'VIOLATION'}")

            # --- spatial scale --------------------------------------------- #
            print("\n  spatial scale (local watershed vs study region):")
            for change in CHANGES:
                local, region = _val(f"{change}_local_watershed"), _val(f"{change}_region")
                if local is None or region is None:
                    print(f"    {change:<24} insufficient data")
                    continue
                ratio = region / local if local else float("nan")
                print(f"    {change:<24} {local:6.0f} vs {region:6.0f}  region/local x{ratio:.2f}")

            # --- distance decay -------------------------------------------- #
            print("\n  distance decay (nonlocal / local at the watershed):")
            for change in CHANGES:
                local, non = _val(f"{change}_local_watershed"), _val(
                    f"{change}_nonlocal_watershed"
                )
                if local is None or non is None:
                    print(f"    {change:<24} insufficient data")
                    continue
                ratio = non / local if local else float("nan")
                print(f"    {change:<24} {non:6.0f} / {local:6.0f}  x{ratio:.2f}")

            # --- format invariance ----------------------------------------- #
            print("\n  format invariance (referendum / open-ended / interval p50):")
            printed = False
            for sid in scenarios:
                est = ref.get((model, sid))
                trio = [
                    est.preferred if est else None,
                    direct.get((model, sid, "open_ended", frame)),
                    direct.get((model, sid, "interval", frame)),
                ]
                known = [v for v in trio if v is not None]
                if len(known) < 2:
                    continue
                printed = True
                rendered = " / ".join("-" if v is None else f"{v:.0f}" for v in trio)
                spread = (max(known) / min(known)) if min(known) > 0 else float("nan")
                print(f"    {sid:<30} {rendered:<24} spread x{spread:.2f}")
            if not printed:
                print("    skipped (single format this week)")

        if {"advisor", "persona"} <= set(frames):
            parsed, total = parse_counts(rows, model, "persona")
            rate = parsed / total if total else 0.0
            print(f"\n  persona parse {parsed}/{total}")
            if rate < PARSE_GATE:
                print("  L not scored: persona parse rate below 80%")
                continue
            shift = level_shift_L(
                open_ended_draws(rows, model, "advisor"),
                open_ended_draws(rows, model, "persona"),
            )
            if shift["L"] is None:
                print("  L not scored: no usable cells")
                continue
            lo = "-" if shift["lo"] is None else f"{shift['lo']:.3f}"
            hi = "-" if shift["hi"] is None else f"{shift['hi']:.3f}"
            print(
                f"  L = {shift['L']:.3f}  (95% boot {lo}–{hi})  {shift['label']}"
            )
            if shift["dropped"]:
                print(f"  dropped zero-median cells: {', '.join(shift['dropped'])}")
            outcomes[model] = shift["label"]

    if outcomes:
        counts = Counter(outcomes.values())
        top, n = counts.most_common(1)[0]
        print()
        if n >= 3:
            print(f"headline: {top} ({n} of {len(outcomes)} models)")
        else:
            print(f"headline: mixed ({', '.join(f'{m}: {o}' for m, o in outcomes.items())})")

    return out


def _suffix(unit: str, locality: str) -> str:
    if unit == "study_region":
        return "_region"
    return f"_{locality}_{unit}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_dir", type=Path)
    parser.add_argument("--csv", type=Path, default=None)
    args = parser.parse_args()

    rows = collect(args.log_dir)
    if not rows:
        raise SystemExit(f"no scored samples found in {args.log_dir}")
    print(f"collected {len(rows)} generations")

    summary = report(rows)

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(summary[0]))
            writer.writeheader()
            writer.writerows(summary)
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()
