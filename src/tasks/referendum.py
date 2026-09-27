"""Referendum arm -- the human-matched elicitation.

Each sample presents one scenario at one bid from the published ladder and asks
for a Yes/No recommendation. WTP is recovered offline from the response curve
(`src.wtp`), the same way the original study recovers it from human votes.

The model is never given a persona. It advises a user who faces the referendum;
the "water quality near your home" row is a stated parameter of the choice
problem, not a claim about the model. That choice is what makes the coherence
checks normative -- an assistant recommending less for a strictly dominant
policy has made an error, not expressed a preference.

Run:
    inspect eval src/tasks/referendum.py --model anthropic/claude-sonnet-4-5
    inspect eval src/tasks/referendum.py --model openai/gpt-4o -T with_levels=false
    inspect eval src/tasks/referendum.py --model openai/o3 -T temperature=null
"""

from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import GenerateConfig
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

from src.inspect_util import load_prompt
from src.scenarios import render_scenario_prompt
from src.schema import load_bids, load_instrument, load_scenarios, parse_vote


def _dataset(
    with_levels: bool,
    drop_study_region: bool,
    income: int | None,
    only_study_region: bool = False,
) -> MemoryDataset:
    if drop_study_region and only_study_region:
        raise ValueError("drop_study_region and only_study_region cannot both be set")
    scenarios = load_scenarios()
    if drop_study_region:
        scenarios = [s for s in scenarios if s.spatial_unit != "study_region"]
    elif only_study_region:
        scenarios = [s for s in scenarios if s.spatial_unit == "study_region"]
    inst = load_instrument()
    if income is not None:
        inst = inst.at_income(income)
    shown_income = inst.household.income
    bids = load_bids()
    samples: list[Sample] = []
    for scenario in scenarios:
        if scenario.baseline.is_degenerate_for(scenario.change):
            raise ValueError(
                f"{scenario.id}: change leaves the baseline unaltered; the survey "
                "dropped such proposals as meaningless (SI S2)"
            )
        for bid in bids:
            samples.append(
                Sample(
                    input=render_scenario_prompt(
                        scenario,
                        bid,
                        "referendum",
                        with_levels=with_levels,
                        instrument=inst,
                    ),
                    target="",
                    metadata={
                        "scenario_id": scenario.id,
                        "change": scenario.change,
                        "locality": scenario.locality,
                        "spatial_unit": scenario.spatial_unit,
                        "bid": bid,
                        "avg_before": round(scenario.baseline.average, 4),
                        "avg_after": round(scenario.improved.average, 4),
                        "home_level": scenario.home_level,
                        "home_level_after": scenario.home_level_after,
                        "with_levels": with_levels,
                        "format": "referendum",
                        "income": shown_income,
                    },
                )
            )
    return MemoryDataset(samples)


@scorer(metrics=[mean(), stderr()])
def vote_parsed():
    """Scores parse success, not correctness -- there is no correct vote.

    The vote itself rides in metadata for offline curve fitting. Value is the
    parse rate, which is the thing that can actually fail.
    """

    async def score(state: TaskState, target: Target) -> Score:
        text = state.output.completion or ""
        vote = parse_vote(text)
        return Score(
            value=1.0 if vote is not None else 0.0,
            answer="yes" if vote else ("no" if vote is False else "unparsed"),
            metadata={**(state.metadata or {}), "vote": vote, "raw": text.strip()},
        )

    return score


@task
def referendum(
    with_levels: bool = True,
    temperature: float | None = 1.0,
    drop_study_region: bool = False,
    income: int | None = None,
    only_study_region: bool = False,
) -> Task:
    """Referendum arm.

    Args:
        with_levels: include the six-level definitions before the scenario. The
            minimal stand-in for Part 2 of the survey, which taught respondents
            the scale with graphics and comprehension checks. Context depth is a
            treatment; run both settings if there is budget.
        temperature: repeats at temperature 1 stand in for the population
            heterogeneity that gives a human sample its WTP distribution. Pass
            null for reasoning models that reject the parameter.
        drop_study_region: if true, keep only the six local/non-local watershed
            cells (Saturday 2026-09-19 cut).
        income: household income printed in the prompt. None uses the instrument
            file (currently $75,000). Pass another value to vary income without
            editing that file.
        only_study_region: if true, keep only the three basin cells. Used to add
            the study region at $75,000 without repeating Saturday's watersheds.
    """
    inst = load_instrument()
    if income is not None:
        inst = inst.at_income(income)
    return Task(
        dataset=_dataset(
            with_levels, drop_study_region, income, only_study_region
        ),
        solver=[system_message(load_prompt("system_advisor.txt", inst)), generate()],
        scorer=vote_parsed(),
        config=GenerateConfig(temperature=temperature)
        if temperature is not None
        else GenerateConfig(),
    )
