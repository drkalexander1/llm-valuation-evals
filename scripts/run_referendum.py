"""Saturday referendum: 6 cells x 10 stretched bids x 10 epochs.

Advisor frame, $75,000 household, study-region column dropped. Sonnet's GPT
peer is gpt-5.6-terra (mid tier; Sol/Opus and Astra/Fable sit above).

Usage:
    python scripts/run_referendum.py
    python scripts/run_referendum.py --models anthropic/claude-sonnet-4-5 openai/gpt-5.6-terra
    python scripts/run_referendum.py --models anthropic/claude-sonnet-5
    python scripts/run_referendum.py --income 35000 200000
    python scripts/run_referendum.py --study-region --income 35000 200000
    python scripts/run_referendum.py --only-study-region --income 75000
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from inspect_ai import eval  # noqa: E402

from src.inspect_util import temp_for  # noqa: E402

MODELS = (
    "anthropic/claude-sonnet-4-5",
    "anthropic/claude-sonnet-5",
    "anthropic/claude-haiku-4-5",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-5.6-terra",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=list(MODELS))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument(
        "--income",
        type=int,
        nargs="+",
        default=None,
        help="household incomes to run, each as its own condition. "
        "Omit to use the instrument file ($75,000) and logs/referendum.",
    )
    parser.add_argument(
        "--study-region",
        action="store_true",
        help="keep the 425,000-square-mile study region (9 cells). "
        "Default is the Saturday cut: local and non-local watershed only.",
    )
    parser.add_argument(
        "--only-study-region",
        action="store_true",
        help="run only the three basin cells. Skips the watersheds already "
        "collected at $75,000.",
    )
    args = parser.parse_args()
    if args.study_region and args.only_study_region:
        raise SystemExit("pass only one of --study-region and --only-study-region")

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise SystemExit("no API key in .env")

    if args.only_study_region:
        n_cells = 3
    elif args.study_region:
        n_cells = 9
    else:
        n_cells = 6
    n_bids = 10
    incomes = args.income or [None]
    per_income = len(args.models) * n_cells * n_bids * args.epochs
    print(
        f"referendum: {len(incomes)} income(s) x {len(args.models)} models x "
        f"{n_cells} cells x {n_bids} bids x {args.epochs} epochs "
        f"({per_income * len(incomes)} generations)"
    )

    failed: list[str] = []
    by_temp: dict[float | None, list[str]] = {}
    for model in args.models:
        by_temp.setdefault(temp_for(model), []).append(model)

    for income in incomes:
        if income is None and not args.study_region:
            log_dir = "logs/referendum"
        else:
            shown = 75000 if income is None else income
            log_dir = f"logs/income/{shown}"
        label = "instrument default" if income is None else f"${income:,}"
        print(f"income {label} -> {log_dir}")
        for temperature, models in by_temp.items():
            task_args: dict = {
                "with_levels": True,
                "drop_study_region": not (args.study_region or args.only_study_region),
                "only_study_region": args.only_study_region,
                "temperature": temperature,
            }
            if income is not None:
                task_args["income"] = income
            logs = eval(
                "src/tasks/referendum.py",
                model=models,
                task_args=task_args,
                log_dir=log_dir,
                display="plain",
                epochs=args.epochs,
            )
            for log in logs:
                if log.status != "success":
                    failed.append(f"{log.eval.model} @ {label}")
    if failed:
        raise SystemExit(f"referendum failed for: {', '.join(failed)}")
    print("wrote logs under logs/referendum/ or logs/income/")


if __name__ == "__main__":
    main()
