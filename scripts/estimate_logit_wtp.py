"""Parametric referendum WTP: the Hanemann (1984) linear logit, per model, cell and income.

P(yes | bid) = 1 / (1 + exp(-(a - b * bid)))  =>  mean = median WTP = a / b.

Fitted by Firth's (1993) penalized likelihood rather than plain maximum likelihood.
Many cells go from all-yes to all-no between two adjacent bids (perfect
separation), where the ML estimate does not exist; Firth's estimate is finite and
close to ML elsewhere. Standard error by the delta method on (a, b).

A cell gets an estimate only if the price slope b is positive at the 5% level
(b / se(b) > 1.96); a flat curve has no recoverable WTP. Estimates above the $3,000
top bid are extrapolations and are flagged. Also reports the area under the
yes-share curve (src/wtp.py), which is bounded by the top bid.

Usage:
    python scripts/estimate_logit_wtp.py --draws results/referendum_draws.csv --csv results/logit_wtp.csv
    python scripts/estimate_logit_wtp.py --csv results/logit_wtp.csv   # from local logs
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze_coherence import collect  # noqa: E402
from src import wtp  # noqa: E402

# The Saturday run is the $75,000 watershed arm; the income dirs name their income.
LOG_DIRS = {
    "logs/referendum": 75000,
    "logs/income/35000": 35000,
    "logs/income/75000": 75000,
    "logs/income/200000": 200000,
}
TOP_BID = 3000


def firth_logit(shares: dict[int, tuple[int, int]], max_iter: int = 200):
    """Firth-penalized fit of P(yes) = logistic(a + c * bid) on grouped data.

    Bid is scaled to thousands inside the fit for conditioning. Returns
    (a, c, cov) on the dollar scale, or None if there is no variation at all.
    """
    x = np.array(sorted(shares), dtype=float)
    yes = np.array([shares[int(k)][0] for k in x], dtype=float)
    n = np.array([shares[int(k)][1] for k in x], dtype=float)
    if len(x) < 2:
        return None
    X = np.column_stack([np.ones_like(x), x / 1000.0])
    beta = np.zeros(2)
    for _ in range(max_iter):
        p = 1.0 / (1.0 + np.exp(-(X @ beta)))
        w = n * p * (1 - p)
        info = X.T @ (X * w[:, None])
        inv = np.linalg.inv(info)
        h = w * np.einsum("ij,jk,ik->i", X, inv, X)  # hat diagonals
        score = X.T @ (yes - n * p + h * (0.5 - p))
        step = inv @ score
        step *= min(1.0, 5.0 / max(np.max(np.abs(step)), 1e-12))  # damp early steps
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    p = 1.0 / (1.0 + np.exp(-(X @ beta)))
    info = X.T @ (X * (n * p * (1 - p))[:, None])
    cov_k = np.linalg.inv(info)
    scale = np.diag([1.0, 1.0 / 1000.0])
    return float(beta[0]), float(beta[1] / 1000.0), scale @ cov_k @ scale


def fit_with_se(shares: dict[int, tuple[int, int]]) -> tuple[float, float, float] | None:
    """Return (wtp, se, slope_b) for P(yes) = logistic(a - b * bid), or None."""
    fit = firth_logit(shares)
    if fit is None:
        return None
    a, c, cov = fit  # logistic(a + c * bid), so b = -c
    b = -c
    if b <= 0 or b / np.sqrt(cov[1, 1]) <= 1.96:
        return None  # no significant price response: flat curve
    est = a / b  # = -a / c
    grad = np.array([-1.0 / c, a / c**2])  # d(-a/c)/d(a, c)
    var = float(grad @ cov @ grad)
    se = float(np.sqrt(var)) if var > 0 and np.isfinite(var) else float("nan")
    return float(est), se, float(b)


def counts_from_draws(path: Path) -> dict[str, dict[str, list[int]]]:
    """Same shape as the cache: 'model|income|scenario' -> {bid: [yes, n]}."""
    grouped: dict[str, tuple[list[int], list[bool | None]]] = defaultdict(lambda: ([], []))
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            bids, votes = grouped[f"{row['model']}|{row['income']}|{row['scenario_id']}"]
            bids.append(int(row["bid"]))
            votes.append(None if row["vote"] == "" else row["vote"] == "1")
    return {k: {str(b): list(yn) for b, yn in wtp.yes_shares(*v).items()}
            for k, v in grouped.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--counts", type=Path, default=Path("results/referendum_counts.json"),
                    help="cache of yes/n per bid; rebuilt from logs if missing")
    ap.add_argument("--draws", type=Path,
                    help="public draw-level CSV (results/referendum_draws.csv); "
                         "fits from it instead of the logs or the cache")
    args = ap.parse_args()

    if args.draws:
        counts = counts_from_draws(args.draws)
    elif args.counts.exists():
        counts = json.loads(args.counts.read_text())
    else:
        grouped: dict[str, tuple[list[int], list[bool | None]]] = defaultdict(lambda: ([], []))
        for d, income in LOG_DIRS.items():
            for row in collect(Path(d)):
                if row.get("format") != "referendum":
                    continue
                bids, votes = grouped[f"{row['model']}|{income}|{row['scenario_id']}"]
                bids.append(int(row["bid"]))
                votes.append(row.get("vote"))
        counts = {k: {str(b): list(yn) for b, yn in wtp.yes_shares(*v).items()}
                  for k, v in grouped.items()}
        args.counts.write_text(json.dumps(counts, indent=0))

    out = []
    for key in sorted(counts, key=lambda k: (k.split("|")[0], int(k.split("|")[1]), k.split("|")[2])):
        model, income, sid = key.split("|")
        income = int(income)
        shares = {int(b): tuple(yn) for b, yn in counts[key].items()}
        fit = fit_with_se(shares)
        out.append({
            "model": model, "income": income, "scenario_id": sid,
            "n": sum(k for _, k in shares.values()),
            "logit_wtp": round(fit[0]) if fit else None,
            "se": round(fit[1]) if fit and np.isfinite(fit[1]) else None,
            "slope_per_1000": round(fit[2] * 1000, 3) if fit else None,
            "beyond_ladder": bool(fit and fit[0] > TOP_BID),
            "turnbull_area": round(wtp.turnbull_mean(shares)),
        })
    for r in out:
        print(r)
    if args.csv:
        with args.csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)


if __name__ == "__main__":
    main()
