"""R13: advisor vs household persona, same open-ended grid as R12.

Both arms run under the current ANSWER-line prompts. R12 is not the control;
see PLAN.md.

Usage:
    python scripts/run_r13.py
    python scripts/run_r13.py --models anthropic/claude-haiku-4-5
    python scripts/run_r13.py --frames advisor
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

from src.scenarios import FRAMES  # noqa: E402

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
    parser.add_argument("--frames", nargs="+", choices=FRAMES, default=list(FRAMES))
    args = parser.parse_args()

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise SystemExit("no API key in .env")

    print(
        f"R13: {len(args.frames)} frames x {len(args.models)} models x "
        f"9 scenarios x {args.epochs} epochs"
    )
    failed: list[str] = []
    for frame in args.frames:
        logs = eval(
            "src/tasks/direct_wtp.py",
            model=args.models,
            task_args={"fmt": "open_ended", "with_levels": True, "frame": frame},
            log_dir=f"logs/r13/{frame}",
            display="plain",
            epochs=args.epochs,
        )
        for log in logs:
            if log.status != "success":
                failed.append(f"{frame}/{log.eval.model}")
    if failed:
        raise SystemExit(f"R13 failed for: {', '.join(failed)}")
    print("wrote logs under logs/r13/")


if __name__ == "__main__":
    main()
