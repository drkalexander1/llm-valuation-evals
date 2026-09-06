"""Render a Scenario into the instrument's policy-summary table and prompts.

Layout follows Figure S3 (local variant, four rows) and the non-local voting
screen at sd01 p.41 (three rows -- the "near your home" row is absent, not
blank). That structural difference between arms is part of the treatment.

Region copy, level labels, change lines, and the tax window come from
data/instrument.yaml. Averages on the table are computed, never stored.
"""

from __future__ import annotations

from src.inspect_util import load_prompt
from src.schema import Scenario, load_instrument

_LABEL_W = 42
_COL_W = 22


def _row(label: str, current: str, proposed: str) -> str:
    return f"{label:<{_LABEL_W}}| {current:<{_COL_W}} | {proposed}"


def render_policy_table(scenario: Scenario, bid: int) -> str:
    inst = load_instrument()
    labels = inst.levels
    lines = [
        "Policy Summary",
        "",
        f"Description of policy region: {inst.regions[scenario.locality].description}",
        f"Size of policy region: {scenario.area_sq_miles:,} square miles.",
        inst.household.rendered_description(),
        "",
        _row("", "No policy", "Proposed policy"),
        _row("", "(current conditions)", "(improved conditions)"),
        "-" * _LABEL_W + "+" + "-" * (_COL_W + 2) + "+" + "-" * (_COL_W + 2),
        _row("Description of change", "None", scenario.change_description),
    ]

    if scenario.includes_home and scenario.home_level is not None:
        lines.append(
            _row(
                "Water quality near your home",
                labels[scenario.home_level],
                labels[scenario.home_level_after],
            )
        )

    lines += [
        _row(
            "Water quality throughout region (average)",
            f"{scenario.baseline.average:.2f}",
            f"{scenario.improved.average:.2f}",
        ),
        _row("Increase in taxes to your household", "None", f"${bid}"),
        _row(f"(per year, for the next {inst.tax.years} years)", "", ""),
    ]
    return "\n".join(line.rstrip() for line in lines)


def render_levels_block() -> str:
    """The quality levels, as introduced in Part 2 of the survey."""
    labels = load_instrument().levels
    count = {6: "six"}.get(len(labels), str(len(labels)))
    header = (
        f"Surface waterbodies can be divided into {count} categories based on how a "
        "stream, river, or lake differs from its natural state:"
    )
    return header + "\n\n" + "\n".join(labels[i] for i in sorted(labels))


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
