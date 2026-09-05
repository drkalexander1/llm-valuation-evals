"""Direct-elicitation arms -- open-ended and interval.

Same nine scenarios as the referendum arm, no bid. Asks the amount directly
rather than recovering it from a vote curve. Comparing the three formats within
a model and scenario is a ground-truth-free consistency check: humans give
format-dependent answers, which is half of why stated preference is contested,
and whether a model does is answerable without any human number.

The interval format reuses the p10/p50/p90 elicitation from the anchoring and
meta-consistency rounds, so widths are comparable to that work.

Run:
    inspect eval src/tasks/direct_wtp.py --model anthropic/claude-sonnet-4-5
    inspect eval src/tasks/direct_wtp.py --model anthropic/claude-haiku-4-5 -T fmt=interval
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

from src.inspect_util import load_prompt
from src.scenarios import render_scenario_prompt
from src.schema import load_scenarios, parse_dollars, parse_interval

FORMATS = ("open_ended", "interval")


def _dataset(fmt: str, with_levels: bool) -> MemoryDataset:
    samples: list[Sample] = []
    for scenario in load_scenarios():
        samples.append(
            Sample(
                input=render_scenario_prompt(
                    scenario, None, fmt, with_levels=with_levels
                ),
                target="",
                metadata={
                    "scenario_id": scenario.id,
                    "change": scenario.change,
                    "locality": scenario.locality,
                    "spatial_unit": scenario.spatial_unit,
                    "avg_before": round(scenario.baseline.average, 4),
                    "avg_after": round(scenario.improved.average, 4),
                    "home_level": scenario.home_level,
                    "home_level_after": scenario.home_level_after,
                    "with_levels": with_levels,
                    "format": fmt,
                },
            )
        )
    return MemoryDataset(samples)


@scorer(metrics=[mean(), stderr()])
def amount_parsed(fmt: str):
    """Parse rate. The amount itself rides in metadata for offline analysis."""

    async def score(state: TaskState, target: Target) -> Score:
        text = state.output.completion or ""
        meta: dict = {**(state.metadata or {}), "raw": text.strip()}
        if fmt == "interval":
            parsed = parse_interval(text)
            ok = parsed is not None
            if ok:
                p10, p50, p90 = parsed
                meta |= {"p10": p10, "p50": p50, "p90": p90, "wtp": p50}
                # Relative width, comparable to the meta-consistency round.
                meta["rel_width"] = (p90 - p10) / p50 if p50 else float("nan")
        else:
            value = parse_dollars(text)
            ok = value is not None
            if ok:
                meta["wtp"] = value
        return Score(
            value=1.0 if ok else 0.0,
            answer=str(meta.get("wtp", "unparsed")),
            metadata=meta,
        )

    return score


@task
def direct_wtp(
    fmt: str = "open_ended",
    with_levels: bool = True,
    temperature: float | None = 1.0,
) -> Task:
    if fmt not in FORMATS:
        raise ValueError(f"fmt must be one of {FORMATS}, got {fmt!r}")
    return Task(
        dataset=_dataset(fmt, with_levels),
        solver=[system_message(load_prompt("system_advisor.txt")), generate()],
        scorer=amount_parsed(fmt),
        config=GenerateConfig(temperature=temperature)
        if temperature is not None
        else GenerateConfig(),
    )
