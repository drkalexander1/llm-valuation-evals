"""Refusal / parse smoke -- 20 predeclared prompts, one epoch.

Covers all three formats, the nested-dominance pair, and local / nonlocal /
region. Not a WTP estimate. Temperature 0: this is a parse check, not a
population stand-in.

Run:
    python scripts/run_smoke.py
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

from src.inspect_util import load_prompt
from src.scenarios import FRAMES, SYSTEM_PROMPTS, render_scenario_prompt
from src.schema import load_scenarios, parse_dollars, parse_interval, parse_vote

# 8 referendum + 6 open-ended + 6 interval.
SMOKE: list[tuple[str, str, int | None]] = [
    ("min2_local_watershed", "referendum", 20),
    ("min2_local_watershed", "referendum", 500),
    ("min3_local_watershed", "referendum", 20),
    ("min3_local_watershed", "referendum", 500),
    ("one_level_local_watershed", "referendum", 100),
    ("one_level_nonlocal_watershed", "referendum", 250),
    ("min2_region", "referendum", 750),
    ("min3_nonlocal_watershed", "referendum", 100),
    ("min2_local_watershed", "open_ended", None),
    ("min3_local_watershed", "open_ended", None),
    ("one_level_local_watershed", "open_ended", None),
    ("min2_nonlocal_watershed", "open_ended", None),
    ("one_level_region", "open_ended", None),
    ("min3_region", "open_ended", None),
    ("min2_local_watershed", "interval", None),
    ("min3_local_watershed", "interval", None),
    ("one_level_local_watershed", "interval", None),
    ("one_level_nonlocal_watershed", "interval", None),
    ("min2_region", "interval", None),
    ("min3_region", "interval", None),
]


def _dataset(frame: str) -> MemoryDataset:
    if frame not in FRAMES:
        raise ValueError(f"frame must be one of {FRAMES}, got {frame!r}")
    items = (
        [item for item in SMOKE if item[1] == "open_ended"]
        if frame == "persona"
        else SMOKE
    )
    scenarios = {s.id: s for s in load_scenarios()}
    samples: list[Sample] = []
    for scenario_id, fmt, bid in items:
        scenario = scenarios[scenario_id]
        samples.append(
            Sample(
                id=f"{scenario_id}/{fmt}/{bid if bid is not None else 'na'}",
                input=render_scenario_prompt(
                    scenario, bid, fmt, with_levels=True, frame=frame
                ),
                target="",
                metadata={
                    "scenario_id": scenario_id,
                    "change": scenario.change,
                    "locality": scenario.locality,
                    "bid": bid,
                    "format": fmt,
                    "frame": frame,
                },
            )
        )
    return MemoryDataset(samples)


@scorer(metrics=[mean(), stderr()])
def smoke_parsed():
    """Parse rate across all three formats."""

    async def score(state: TaskState, target: Target) -> Score:
        text = state.output.completion or ""
        fmt = (state.metadata or {}).get("format")
        meta: dict = {**(state.metadata or {}), "raw": text.strip()}
        if fmt == "referendum":
            vote = parse_vote(text)
            ok = vote is not None
            meta["vote"] = vote
            answer = "yes" if vote else ("no" if vote is False else "unparsed")
        elif fmt == "interval":
            parsed = parse_interval(text)
            ok = parsed is not None
            if ok:
                p10, p50, p90 = parsed
                meta |= {"p10": p10, "p50": p50, "p90": p90, "wtp": p50}
            answer = str(meta.get("wtp", "unparsed"))
        else:
            value = parse_dollars(text)
            ok = value is not None
            if ok:
                meta["wtp"] = value
            answer = str(meta.get("wtp", "unparsed"))
        return Score(value=1.0 if ok else 0.0, answer=answer, metadata=meta)

    return score


@task
def smoke(frame: str = "advisor") -> Task:
    return Task(
        dataset=_dataset(frame),
        solver=[system_message(load_prompt(SYSTEM_PROMPTS[frame])), generate()],
        scorer=smoke_parsed(),
        config=GenerateConfig(temperature=0.0),
    )
