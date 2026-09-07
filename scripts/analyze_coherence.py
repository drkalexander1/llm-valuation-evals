"""Compute the coherence endpoints from Inspect eval logs.

UNVERIFIED AGAINST REAL LOGS -- written before the first run, so the log-reading
half is the part most likely to need fixing. The arithmetic below is covered by
tests; the extraction is not.

Usage:
    python scripts/analyze_coherence.py logs/
    python scripts/analyze_coherence.py logs/ --csv results/coherence.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import wtp  # noqa: E402
from src.schema import load_benchmarks, load_scenarios, parse_dollars  # noqa: E402

CHANGES = ("min2", "one_level", "min3")


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


def direct_wtp(rows: list[dict]) -> dict[tuple[str, str, str], float]:
    """(model, scenario, format) -> median of parsed amounts."""
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        fmt = row.get("format")
        if fmt in ("open_ended", "interval") and row.get("wtp") is not None:
            grouped[(row["model"], row["scenario_id"], fmt)].append(float(row["wtp"]))
    out: dict[tuple[str, str, str], float] = {}
    for key, values in grouped.items():
        values.sort()
        mid = len(values) // 2
        out[key] = (
            values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2
        )
    return out


def primary_wtp(
    model: str,
    sid: str,
    ref: dict[tuple[str, str], wtp.WTPEstimate],
    direct: dict[tuple[str, str, str], float],
) -> tuple[float | None, str | None]:
    """Prefer referendum, then open-ended, then interval. This week's pilot is OE."""
    est = ref.get((model, sid))
    if est is not None and est.preferred is not None:
        return est.preferred, "referendum"
    for fmt in ("open_ended", "interval"):
        value = direct.get((model, sid, fmt))
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
    for model in models:
        print(f"\n=== {model} ===")

        # --- criterion: level comparison against published means ------------ #
        print("\n  scenario                        model    human (SE)   ratio  source")
        for sid in scenarios:
            value, source = primary_wtp(model, sid, ref, direct)
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
                    "scenario_id": sid,
                    "wtp_primary": value,
                    "primary_source": source,
                    "wtp_referendum": est.preferred if est else None,
                    "wtp_turnbull": est.turnbull_mean if est else None,
                    "wtp_open_ended": direct.get((model, sid, "open_ended")),
                    "wtp_interval_p50": direct.get((model, sid, "interval")),
                    "human_mean": b.mean,
                    "human_stderr": b.stderr,
                    "censored": est.censored if est else None,
                }
            )

        def _val(sid: str) -> float | None:
            return primary_wtp(model, sid, ref, direct)[0]

        # --- nested dominance ------------------------------------------------ #
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

        # --- scope ordering -------------------------------------------------- #
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

        # --- spatial scale --------------------------------------------------- #
        print("\n  spatial scale (local watershed vs study region):")
        for change in CHANGES:
            local, region = _val(f"{change}_local_watershed"), _val(f"{change}_region")
            if local is None or region is None:
                print(f"    {change:<24} insufficient data")
                continue
            ratio = region / local if local else float("nan")
            print(f"    {change:<24} {local:6.0f} vs {region:6.0f}  region/local x{ratio:.2f}")

        # --- distance decay -------------------------------------------------- #
        print("\n  distance decay (nonlocal / local at the watershed):")
        for change in CHANGES:
            local, non = _val(f"{change}_local_watershed"), _val(f"{change}_nonlocal_watershed")
            if local is None or non is None:
                print(f"    {change:<24} insufficient data")
                continue
            ratio = non / local if local else float("nan")
            print(f"    {change:<24} {non:6.0f} / {local:6.0f}  x{ratio:.2f}")

        # --- format invariance ------------------------------------------------ #
        print("\n  format invariance (referendum / open-ended / interval p50):")
        printed = False
        for sid in scenarios:
            est = ref.get((model, sid))
            trio = [
                est.preferred if est else None,
                direct.get((model, sid, "open_ended")),
                direct.get((model, sid, "interval")),
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
