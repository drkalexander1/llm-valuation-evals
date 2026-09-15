"""Direct-elicitation arms -- open-ended and interval.

Same nine scenarios as the referendum arm, no bid. Asks the amount directly
rather than recovering it from a vote curve. Comparing the three formats within
a model and scenario is a ground-truth-free consistency check: humans give
format-dependent answers, which is half of why stated preference is contested,
and whether a model does is answerable without any human number.

The interval format reuses the p10/p50/p90 elicitation from the anchoring and
meta-consistency rounds, so widths are comparable to that work.

R12 was open-ended under the advisor frame (`python scripts/run_pilot.py`).
R13 reruns advisor and persona together (`python scripts/run_r13.py`).
Interval is still held.

Run:
    inspect eval src/tasks/direct_wtp.py --model anthropic/claude-sonnet-4-5 --epochs 10
    inspect eval src/tasks/direct_wtp.py --model anthropic/claude-haiku-4-5 -T frame=persona
    inspect eval src/tasks/direct_wtp.py --model anthropic/claude-haiku-4-5 -T fmt=interval
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

from src.inspect_util import load_prompt
from src.scenarios import FRAMES, SYSTEM_PROMPTS, render_scenario_prompt
from src.schema import load_scenarios, parse_dollars, parse_interval

FORMATS = ("open_ended", "interval")


def _dataset(fmt: str, with_levels: bool, frame: str) -> MemoryDataset:
    samples: list[Sample] = []
    for scenario in load_scenarios():
        samples.append(
            Sample(
                input=render_scenario_prompt(
                    scenario, None, fmt, with_levels=with_levels, frame=frame
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
                    "frame": frame,
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
    frame: str = "advisor",
) -> Task:
    if fmt not in FORMATS:
        raise ValueError(f"fmt must be one of {FORMATS}, got {fmt!r}")
    if frame not in FRAMES:
        raise ValueError(f"frame must be one of {FRAMES}, got {frame!r}")
    if frame == "persona" and fmt != "open_ended":
        raise ValueError("persona frame is only defined for open-ended")
    return Task(
        dataset=_dataset(fmt, with_levels, frame),
        solver=[system_message(load_prompt(SYSTEM_PROMPTS[frame])), generate()],
        scorer=amount_parsed(fmt),
        config=GenerateConfig(temperature=temperature)
        if temperature is not None
        else GenerateConfig(),
    )
