"""Audit the R13 logs independently of analyze_coherence.py and results/r13.csv.

Added 2026-09-15, after the run. Nothing here is predeclared -- it checks the
pipeline and says how firm each frozen call is, it does not re-score them.

Reports:
1. Parse rate, the model id the API actually returned, and how much text came
   before the ANSWER line -- per model x arm, with R12 alongside for comparison.
2. Per-cell medians recomputed from raw answers, diffed against results/r13.csv.
3. How often each coherence call would flip if the ten draws in a cell were
   resampled: P(nonlocal median > local median) and P(min3 median > min2
   median).
4. Where resampled L lands relative to the frozen 0.75-1.33 band.

Usage:
    python scripts/audit_r13.py
"""

from __future__ import annotations

import csv
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

REPO = Path(__file__).resolve().parents[1]
SEED = 13
N_BOOT = 2000
L_LOW, L_HIGH = 0.75, 1.33
CHANGES = ("one_level", "min2", "min3")
SPATIAL = ("local_watershed", "nonlocal_watershed", "region")


def _num(a) -> float | None:
    try:
        return float(a)
    except (TypeError, ValueError):
        return None


def load(arm: str, pattern: str) -> list[dict]:
    rows = []
    for p in sorted(REPO.glob(pattern)):
        log = read_eval_log(str(p))
        for s in log.samples or []:
            text = s.output.completion if s.output else ""
            answer = None
            for sc in (s.scores or {}).values():
                answer = sc.answer
            rows.append(
                {
                    "arm": arm,
                    "model": log.eval.model.split("/")[-1],
                    "returned": s.output.model if s.output else None,
                    "sid": (s.metadata or {}).get("scenario_id"),
                    "text": text or "",
                    "wtp": _num(answer),
                }
            )
    return rows


def pre_answer_chars(text: str) -> int:
    i = text.rfind("ANSWER:")
    return len((text[:i] if i >= 0 else text).strip())


def main() -> None:
    rows = load("advisor", "logs/r13/advisor/*.eval")
    rows += load("persona", "logs/r13/persona/*.eval")
    rows += load("r12", "logs/pilot/*.eval")

    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["arm"])].append(r)

    print("1. Parse rate, returned model, reasoning length, top chip")
    for (model, arm), rs in sorted(by.items()):
        vals = [r["wtp"] for r in rs if r["wtp"] is not None]
        ids = ",".join(sorted({str(r["returned"]) for r in rs}))
        pre = statistics.median(pre_answer_chars(r["text"]) for r in rs)
        chip, n_chip = Counter(vals).most_common(1)[0]
        print(
            f"  {model:18} {arm:8} parsed {len(vals)}/{len(rs)}  {ids:28} "
            f"pre-ANSWER median {pre:5.0f} chars  top chip ${chip:.0f} x{n_chip}"
        )

    cells: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        if r["arm"] != "r12" and r["wtp"] is not None:
            cells[(r["model"], r["arm"], r["sid"])].append(r["wtp"])

    print("\n2. Medians recomputed from logs vs results/r13.csv")
    mismatches = 0
    with open(REPO / "results" / "r13.csv", newline="") as f:
        for row in csv.DictReader(f):
            key = (row["model"].split("/")[-1], row["frame"], row["scenario_id"])
            mine = statistics.median(cells[key]) if key in cells else None
            if mine is None or abs(mine - float(row["wtp_open_ended"])) > 1e-6:
                mismatches += 1
                print(f"  MISMATCH {key}: logs {mine} vs csv {row['wtp_open_ended']}")
    print(f"  {mismatches} mismatches across {len(cells)} cells")

    rng = random.Random(SEED)

    def boot_median(xs: list[float]) -> float:
        return statistics.median(rng.choices(xs, k=len(xs)))

    def p_greater(a: list[float], b: list[float]) -> float:
        return sum(boot_median(a) > boot_median(b) for _ in range(N_BOOT)) / N_BOOT

    models = sorted({k[0] for k in cells})
    print(
        "\n3. P(violation) under resampling of draws within cell "
        "(* = the observed median call is a violation)"
    )
    for model in models:
        for arm in ("advisor", "persona"):
            dist = []
            for c in CHANGES:
                local = cells[(model, arm, f"{c}_local_watershed")]
                far = cells[(model, arm, f"{c}_nonlocal_watershed")]
                star = "*" if statistics.median(far) > statistics.median(local) else ""
                dist.append(f"{c} {p_greater(far, local):.2f}{star}")
            nest = []
            for sp in SPATIAL:
                m2 = cells[(model, arm, f"min2_{sp}")]
                m3 = cells[(model, arm, f"min3_{sp}")]
                star = "*" if statistics.median(m3) > statistics.median(m2) else ""
                nest.append(f"{sp.split('_')[0]} {p_greater(m3, m2):.2f}{star}")
            print(
                f"  {model:18} {arm:8} distance: {', '.join(dist):38} "
                f"nest: {', '.join(nest)}"
            )

    print("\n4. Share of resampled L in each frozen band")
    for model in models:
        sids = sorted(k[2] for k in cells if k[0] == model and k[1] == "advisor")
        Ls = []
        for _ in range(N_BOOT):
            logs = [
                math.log(
                    boot_median(cells[(model, "persona", s)])
                    / boot_median(cells[(model, "advisor", s)])
                )
                for s in sids
            ]
            Ls.append(math.exp(sum(logs) / len(logs)))
        drop = sum(x < L_LOW for x in Ls) / N_BOOT
        rise = sum(x > L_HIGH for x in Ls) / N_BOOT
        print(
            f"  {model:18} drop {drop:.2f}   no change {1 - drop - rise:.2f}   "
            f"rise {rise:.2f}"
        )


if __name__ == "__main__":
    main()
