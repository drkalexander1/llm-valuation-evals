"""Export the referendum votes from the Inspect logs to two public CSVs.

The logs themselves are gitignored (about 100 MB). These two files carry what a
reader needs to check a cell or refit the logit without them:

    results/referendum_draws.csv      one row per generation: the parsed vote
    results/referendum_yes_share.csv  one row per model, income and cell: yes / n
                                      at each of the ten bids

Covers the Saturday watershed run ($75,000) and the income and basin runs
($35,000, $75,000 basin, $200,000), the same logs as estimate_logit_wtp.py.

Usage:
    python scripts/export_referendum_draws.py
    python scripts/export_referendum_draws.py --root /path/to/checkout/with/logs
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from estimate_logit_wtp import LOG_DIRS  # noqa: E402

DRAW_FIELDS = [
    "model", "income", "scenario_id", "change", "locality", "spatial_unit",
    "bid", "replicate", "vote", "run_date", "source_log",
]


def draws(root: Path) -> list[dict]:
    rows: list[dict] = []
    for d, income in LOG_DIRS.items():
        for info in list_eval_logs(str(root / d)):
            log = read_eval_log(info)
            if log.status != "success" or not log.samples:
                print(f"  skipping {info.name}: status={log.status}", file=sys.stderr)
                continue
            for sample in log.samples:
                for score in (sample.scores or {}).values():
                    meta = score.metadata or {}
                    if meta.get("format") != "referendum":
                        continue
                    vote = meta.get("vote")
                    rows.append({
                        "model": log.eval.model,
                        "income": income,
                        "scenario_id": meta["scenario_id"],
                        "change": meta.get("change"),
                        "locality": meta.get("locality"),
                        "spatial_unit": meta.get("spatial_unit"),
                        "bid": int(meta["bid"]),
                        "replicate": sample.epoch,
                        "vote": "" if vote is None else int(bool(vote)),
                        "run_date": str(log.eval.created)[:10],
                        "source_log": f"{d}/{Path(info.name).name}",
                    })
    rows.sort(key=lambda r: (r["model"], r["income"], r["scenario_id"], r["bid"], r["replicate"]))
    return rows


def yes_share_table(rows: list[dict]) -> tuple[list[str], list[dict]]:
    """Wide table: yes_<bid> and n_<bid> per model, income and cell. n counts parsed votes."""
    bids = sorted({r["bid"] for r in rows})
    cells: dict[tuple, dict[int, list[int]]] = defaultdict(lambda: {b: [0, 0] for b in bids})
    for r in rows:
        if r["vote"] == "":
            continue
        tally = cells[(r["model"], r["income"], r["scenario_id"])][r["bid"]]
        tally[0] += r["vote"]
        tally[1] += 1
    fields = ["model", "income", "scenario_id"]
    for b in bids:
        fields += [f"yes_{b}", f"n_{b}"]
    out = []
    for (model, income, sid), tallies in sorted(cells.items()):
        row = {"model": model, "income": income, "scenario_id": sid}
        for b in bids:
            row[f"yes_{b}"], row[f"n_{b}"] = tallies[b]
        out.append(row)
    return fields, out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."), help="directory that contains logs/")
    ap.add_argument("--draws", type=Path, default=Path("results/referendum_draws.csv"))
    ap.add_argument("--yes-share", type=Path, default=Path("results/referendum_yes_share.csv"))
    args = ap.parse_args()

    rows = draws(args.root)
    with args.draws.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=DRAW_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    fields, table = yes_share_table(rows)
    with args.yes_share.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(table)
    unparsed = sum(r["vote"] == "" for r in rows)
    print(f"{len(rows)} draws ({unparsed} unparsed) -> {args.draws}")
    print(f"{len(table)} cells -> {args.yes_share}")


if __name__ == "__main__":
    main()
