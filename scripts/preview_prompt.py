"""Print the system + user message a model would see for one scenario.

Edit data/instrument.yaml, then rerun this to see the exact table and
wording before sitting down with the instrument's authors.

Usage:
    python scripts/preview_prompt.py min2_local_watershed
    python scripts/preview_prompt.py min2_local_watershed --bid 350
    python scripts/preview_prompt.py one_level_region --fmt open_ended --no-levels
    python scripts/preview_prompt.py min2_local_watershed --fmt open_ended --frame persona
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.inspect_util import load_prompt  # noqa: E402
from src.scenarios import FRAMES, SYSTEM_PROMPTS, render_scenario_prompt  # noqa: E402
from src.schema import load_scenarios  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario_id")
    parser.add_argument(
        "--fmt",
        choices=("referendum", "open_ended", "interval"),
        default="referendum",
    )
    parser.add_argument("--bid", type=int, default=None)
    parser.add_argument(
        "--no-levels",
        action="store_true",
        help="omit the six-level definitions (with_levels=false)",
    )
    parser.add_argument(
        "--frame",
        choices=FRAMES,
        default="advisor",
        help="advisor (default) or household-member persona (open-ended only)",
    )
    args = parser.parse_args()

    scenarios = {s.id: s for s in load_scenarios()}
    scenario = scenarios.get(args.scenario_id)
    if scenario is None:
        known = ", ".join(sorted(scenarios))
        raise SystemExit(f"unknown scenario {args.scenario_id!r}; known: {known}")

    bid = args.bid
    if args.fmt == "referendum" and bid is None:
        bid = 350

    user = render_scenario_prompt(
        scenario,
        bid,
        args.fmt,
        with_levels=not args.no_levels,
        frame=args.frame,
    )
    print("=== SYSTEM ===")
    print(load_prompt(SYSTEM_PROMPTS[args.frame]).rstrip())
    print()
    print("=== USER ===")
    print(user.rstrip())


if __name__ == "__main__":
    main()
