"""Run the 20-prompt parse smoke. Picks Haiku if an Anthropic key is set, else GPT-4o mini.

Usage:
    python scripts/run_smoke.py
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from inspect_ai import eval  # noqa: E402


def _model() -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic/claude-haiku-4-5"
    if os.getenv("OPENAI_API_KEY"):
        return "openai/gpt-4o-mini"
    raise SystemExit("no API key in .env (need ANTHROPIC_API_KEY or OPENAI_API_KEY)")


def main() -> None:
    model = _model()
    print(f"smoke model: {model}")
    logs = eval(
        "src/tasks/smoke.py",
        model=model,
        log_dir="logs/smoke",
        display="plain",
        epochs=1,
    )
    log = logs[0]
    print(f"status: {log.status}")
    if log.status != "success":
        err = getattr(log, "error", None)
        raise SystemExit(f"smoke failed: {err}")

    by_fmt: Counter[str] = Counter()
    ok_fmt: Counter[str] = Counter()
    rows: list[str] = []
    for sample in log.samples or []:
        for score in (sample.scores or {}).values():
            meta = score.metadata or {}
            fmt = meta.get("format", "?")
            by_fmt[fmt] += 1
            parsed = score.value == 1.0
            if parsed:
                ok_fmt[fmt] += 1
            sid = meta.get("scenario_id", sample.id)
            bid = meta.get("bid")
            label = f"{sid} {fmt}" + (f" ${bid}" if bid is not None else "")
            rows.append(f"  {'ok' if parsed else 'FAIL':<4} {label:<48} {score.answer}")

    total = sum(by_fmt.values())
    parsed = sum(ok_fmt.values())
    print(f"\nparse {parsed}/{total}")
    for fmt in ("referendum", "open_ended", "interval"):
        print(f"  {fmt:<12} {ok_fmt[fmt]}/{by_fmt[fmt]}")
    print()
    print("\n".join(rows))
    if parsed < total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
