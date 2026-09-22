"""Saturday referendum: 6 cells x 10 stretched bids x 10 epochs.

Advisor frame, $75,000 household, study-region column dropped. Sonnet's GPT
peer is gpt-5.6-terra (mid tier; Sol/Opus and Astra/Fable sit above).

Usage:
    python scripts/run_referendum.py
    python scripts/run_referendum.py --models anthropic/claude-sonnet-4-5 openai/gpt-5.6-terra
    python scripts/run_referendum.py --models anthropic/claude-sonnet-5
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
    args = parser.parse_args()

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise SystemExit("no API key in .env")

    n_cells = 6
    n_bids = 10
    print(
        f"referendum: {len(args.models)} models x {n_cells} cells x "
        f"{n_bids} bids x {args.epochs} epochs "
        f"({len(args.models) * n_cells * n_bids * args.epochs} generations)"
    )

    failed: list[str] = []
    by_temp: dict[float | None, list[str]] = {}
    for model in args.models:
        by_temp.setdefault(temp_for(model), []).append(model)

    for temperature, models in by_temp.items():
        logs = eval(
            "src/tasks/referendum.py",
            model=models,
            task_args={
                "with_levels": True,
                "drop_study_region": True,
                "temperature": temperature,
            },
            log_dir="logs/referendum",
            display="plain",
            epochs=args.epochs,
        )
        for log in logs:
            if log.status != "success":
                failed.append(log.eval.model)
    if failed:
        raise SystemExit(f"referendum failed for: {', '.join(failed)}")
    print("wrote logs under logs/referendum/")


if __name__ == "__main__":
    main()
