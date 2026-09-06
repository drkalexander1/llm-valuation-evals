"""This week's open-ended pilot: 9 scenarios x 10 epochs x the four planned models.

Usage:
    python scripts/run_pilot.py
    python scripts/run_pilot.py --models anthropic/claude-haiku-4-5
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

MODELS = (
    "anthropic/claude-sonnet-4-5",
    "anthropic/claude-haiku-4-5",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=list(MODELS))
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise SystemExit("no API key in .env")

    print(
        f"open-ended pilot: {len(args.models)} models x 9 scenarios x "
        f"{args.epochs} epochs"
    )
    logs = eval(
        "src/tasks/direct_wtp.py",
        model=args.models,
        task_args={"fmt": "open_ended", "with_levels": True},
        log_dir="logs/pilot",
        display="plain",
        epochs=args.epochs,
    )
    failed = [log for log in logs if log.status != "success"]
    if failed:
        names = ", ".join(log.eval.model for log in failed)
        raise SystemExit(f"pilot failed for: {names}")
    print(f"wrote {len(logs)} logs under logs/pilot/")


if __name__ == "__main__":
    main()
