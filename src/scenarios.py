"""Render a Scenario into the instrument's policy-summary table and prompts.

Layout follows Figure S3 (local variant, four rows) and the non-local voting
screen at sd01 p.41 (three rows -- the "near your home" row is absent, not
blank). That structural difference between arms is part of the treatment.
"""

from __future__ import annotations

from src.inspect_util import load_prompt
from src.schema import (
    CHANGE_DESCRIPTIONS,
    LEVEL_LABELS,
    Scenario,
)

REGION_DESCRIPTIONS: dict[str, str] = {
    "local": "Your local watershed.",
    "nonlocal": "A non-local watershed, which does not include your home.",
    "region": (
        "The full study region: the Upper Mississippi, Ohio, and Tennessee "
        "River Basins."
    ),
}

_LABEL_W = 42
_COL_W = 22


def _row(label: str, current: str, proposed: str) -> str:
    return f"{label:<{_LABEL_W}}| {current:<{_COL_W}} | {proposed}"


def render_policy_table(scenario: Scenario, bid: int) -> str:
    lines = [
        "Policy Summary",
        "",
        f"Description of policy region: {REGION_DESCRIPTIONS[scenario.locality]}",
        f"Size of policy region: {scenario.area_sq_miles:,} square miles.",
        "",
        _row("", "No policy", "Proposed policy"),
        _row("", "(current conditions)", "(improved conditions)"),
        "-" * _LABEL_W + "+" + "-" * (_COL_W + 2) + "+" + "-" * (_COL_W + 2),
        _row("Description of change", "None", CHANGE_DESCRIPTIONS[scenario.change]),
    ]

    if scenario.includes_home and scenario.home_level is not None:
        lines.append(
            _row(
                "Water quality near your home",
                LEVEL_LABELS[scenario.home_level],
                LEVEL_LABELS[scenario.home_level_after],
            )
        )

    lines += [
        _row(
            "Water quality throughout region (average)",
            f"{scenario.baseline.average:.2f}",
            f"{scenario.improved.average:.2f}",
        ),
        _row("Increase in taxes to your household", "None", f"${bid}"),
        _row("(per year, for the next 5 years)", "", ""),
    ]
    return "\n".join(line.rstrip() for line in lines)


def render_levels_block() -> str:
    """The six quality levels, as introduced in Part 2 of the survey."""
    header = (
        "Surface waterbodies can be divided into six categories based on how a "
        "stream, river, or lake differs from its natural state:"
    )
    return header + "\n\n" + "\n".join(LEVEL_LABELS[i] for i in sorted(LEVEL_LABELS))


def render_scenario_prompt(
    scenario: Scenario,
    bid: int | None,
    fmt: str,
    *,
    with_levels: bool = True,
) -> str:
    """Assemble preamble + policy table + the elicitation question.

    `with_levels` toggles context depth: including the level definitions is the
    minimal stand-in for Part 2 of the survey, which taught respondents the
    scale over roughly thirty minutes with graphics and comprehension checks.
    Running both settings is the honest version -- context depth is a treatment,
    not a nuisance parameter.
    """
    parts: list[str] = []
    if with_levels:
        parts.append(render_levels_block())
    parts.append(load_prompt("scenario_preamble.txt").strip())
    parts.append(render_policy_table(scenario, bid if bid is not None else 0))

    if fmt == "referendum":
        if bid is None:
            raise ValueError("referendum format requires a bid")
        question = load_prompt("referendum.txt")
    elif fmt == "open_ended":
        # The tax row is meaningless without a bid; drop the table's cost line.
        parts[-1] = "\n".join(
            ln
            for ln in parts[-1].splitlines()
            if not ln.startswith(("Increase in taxes", "(per year"))
        )
        question = load_prompt("open_ended.txt")
    elif fmt == "interval":
        parts[-1] = "\n".join(
            ln
            for ln in parts[-1].splitlines()
            if not ln.startswith(("Increase in taxes", "(per year"))
        )
        question = load_prompt("interval.txt")
    else:
        raise ValueError(f"unknown format {fmt!r}")

    parts.append(question.strip())
    return "\n\n".join(parts)
