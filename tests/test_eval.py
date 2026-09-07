"""Design invariants. The arithmetic here was derived by hand -- test it."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src import wtp
from src.scenarios import render_policy_table, render_scenario_prompt
from src.inspect_util import load_prompt
from src.schema import (
    LevelDistribution,
    answer_line,
    dominates,
    load_benchmarks,
    load_bids,
    load_instrument,
    load_scenarios,
    parse_dollars,
    parse_interval,
    parse_vote,
)

SCENARIOS = {s.id: s for s in load_scenarios()}


# --------------------------------------------------------------------------- #
# The rule that must never break
# --------------------------------------------------------------------------- #
def test_bcg_terminology_never_reaches_a_model():
    """The instrument withheld the acronym from respondents (SI S2).

    Keeping it out is both fidelity and confound control: naming the published
    framework invites retrieval of it instead of reasoning about the scenario.
    """
    banned = ("bcg", "biological condition gradient")
    for scenario in SCENARIOS.values():
        for fmt, bid in (("referendum", 100), ("open_ended", None), ("interval", None)):
            for with_levels in (True, False):
                text = render_scenario_prompt(
                    scenario, bid, fmt, with_levels=with_levels
                ).lower()
                for token in banned:
                    assert token not in text, f"{scenario.id}/{fmt}: leaked {token!r}"
    system = load_prompt("system_advisor.txt").lower()
    for token in banned:
        assert token not in system, f"system prompt leaked {token!r}"


# --------------------------------------------------------------------------- #
# Level arithmetic
# --------------------------------------------------------------------------- #
def test_baseline_average_matches_figure_s2():
    baseline = SCENARIOS["one_level_local_watershed"].baseline
    # Published figure says 3.52 over shares summing to 99.49; normalizing to 1
    # moves it to 3.54. Both are the same distribution.
    assert baseline.average == pytest.approx(3.54, abs=0.01)


@pytest.mark.parametrize(
    ("scenario_id", "expected"),
    [
        ("one_level_local_watershed", 2.54),
        ("min2_local_watershed", 2.00),
        ("min3_local_watershed", 2.96),
    ],
)
def test_improved_averages(scenario_id: str, expected: float):
    assert SCENARIOS[scenario_id].improved.average == pytest.approx(expected, abs=0.01)


def test_one_level_shifts_average_by_exactly_one():
    """True only while no water sits at Level 1, which is so for this baseline."""
    scenario = SCENARIOS["one_level_region"]
    assert scenario.baseline.average - scenario.improved.average == pytest.approx(1.0)


def test_scope_ordering_matches_human_direction():
    """min2 delivers the best average, min3 the worst -- the ordering humans paid.

    Human WTP at the local watershed ran 492 / 316 / 217 for min2 / one_level /
    min3. This checks our constructed baseline reproduces that same ordering in
    achieved quality, so the scope test is not fighting the scenario design.
    Note the ordering is baseline-dependent: for a heavily degraded region,
    min3 can beat a one-level improvement.
    """
    avg = {c: SCENARIOS[f"{c}_local_watershed"].improved.average for c in ("min2", "one_level", "min3")}
    assert avg["min2"] < avg["one_level"] < avg["min3"]

    bench = load_benchmarks()
    assert (
        bench["min2_local_watershed"].mean
        > bench["one_level_local_watershed"].mean
        > bench["min3_local_watershed"].mean
    )


def test_min2_dominates_min3():
    """The sharpest single test in the design depends on this holding."""
    baseline = SCENARIOS["min2_local_watershed"].baseline
    assert dominates("min2", "min3", baseline)
    assert not dominates("min3", "min2", baseline)


def test_no_scenario_is_degenerate():
    for scenario in SCENARIOS.values():
        assert not scenario.baseline.is_degenerate_for(scenario.change), scenario.id


def test_degenerate_case_is_detected():
    """A region entirely at Level 3 has no meaningful minimum-Level-3 policy."""
    flat = LevelDistribution(shares={3: 1.0})
    assert flat.is_degenerate_for("min3")
    assert not flat.is_degenerate_for("min2")


def test_home_level_is_computed_not_assumed():
    """Figure S3 shows a Level 4 home untouched by a policy that only moved
    Level 3 areas -- so the home row must follow the change rule."""
    assert SCENARIOS["min3_local_watershed"].home_level_after == 3
    assert SCENARIOS["min2_local_watershed"].home_level_after == 2
    assert SCENARIOS["one_level_local_watershed"].home_level_after == 3

    from src.schema import apply_change_to_level

    assert apply_change_to_level(4, "l3_to_l2") == 4


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def test_nonlocal_table_omits_the_home_row():
    """Structural difference between arms, not a blank cell (sd01 p.41)."""
    local = render_policy_table(SCENARIOS["one_level_local_watershed"], 100)
    nonlocal_ = render_policy_table(SCENARIOS["one_level_nonlocal_watershed"], 100)
    assert "Water quality near your home" in local
    assert "Water quality near your home" not in nonlocal_
    assert "does not include your home" in nonlocal_


def test_direct_formats_drop_the_tax_row():
    text = render_scenario_prompt(SCENARIOS["min2_region"], None, "open_ended")
    assert "Increase in taxes" not in text
    assert "Policy Summary" in text


def test_referendum_includes_the_bid():
    text = render_scenario_prompt(SCENARIOS["min2_region"], 350, "referendum")
    assert "$350" in text
    assert "Advisory Referendum" in text


def test_displayed_averages_are_derived():
    """The table prints computed averages; there is no stored display override."""
    scenario = SCENARIOS["min2_local_watershed"]
    derived = scenario.baseline.apply(scenario.change)
    assert scenario.improved.average == pytest.approx(derived.average)
    table = render_policy_table(scenario, 100)
    assert f"{scenario.baseline.average:.2f}" in table
    assert f"{scenario.improved.average:.2f}" in table


def test_change_line_comes_from_instrument():
    inst = load_instrument()
    table = render_policy_table(SCENARIOS["min2_local_watershed"], 100)
    assert inst.changes["min2"].description in table


def test_scenario_description_overrides_change_line():
    base = SCENARIOS["min2_local_watershed"]
    overridden = base.model_copy(update={"description": "A custom change line"})
    table = render_policy_table(overridden, 100)
    assert "A custom change line" in table
    assert load_instrument().changes["min2"].description not in table


def test_prompts_fill_instrument_placeholders():
    inst = load_instrument()
    preamble = load_prompt("scenario_preamble.txt")
    assert str(inst.tax.start) in preamble
    assert str(inst.tax.end) in preamble
    assert str(inst.tax.years) in preamble
    assert "{end}" not in preamble
    assert inst.basin in load_prompt("system_advisor.txt")
    assert inst.household.rendered_description() in load_prompt("system_advisor.txt")
    assert f"next {inst.tax.years} years" in load_prompt("open_ended.txt")


def test_household_income_appears_in_the_scenario():
    inst = load_instrument()
    assert inst.household.income == 100000
    assert inst.household.size == 4
    table = render_policy_table(SCENARIOS["min2_local_watershed"], 100)
    assert inst.household.rendered_description() in table
    assert "$100,000" in table
    assert "4-person" in table
    assert "earner" not in table.lower()


def test_bids_are_the_thinned_ladder():
    bids = load_bids()
    assert bids == [20, 100, 250, 500, 750]
    assert bids[0] == 20 and bids[-1] == 750


def test_every_scenario_has_a_benchmark():
    bench = load_benchmarks()
    assert set(bench) == set(SCENARIOS)


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Yes", True),
        ("No", False),
        ('I vote "Yes" (for the proposed policy)', True),
        ("The cost is high, so no.", False),
        ("It is not obvious, but on balance: Yes", True),
        ("I cannot advise on this.", None),
    ],
)
def test_parse_vote(text: str, expected: bool | None):
    assert parse_vote(text) is expected


def test_parse_dollars_prefers_the_dollar_sign():
    assert parse_dollars("$250") == 250
    assert parse_dollars("about $1,250 per year") == 1250
    assert parse_dollars("no number here") is None


def test_parse_dollars_takes_the_verdict_not_household_income():
    essay = (
        "This is a 4-person household with an annual income of $100,000.\n"
        "A reasonable maximum is about 1% of income.\n"
        "$1,000"
    )
    assert parse_dollars(essay) == 1000


# --------------------------------------------------------------------------- #
# Income-echo regression -- the bug that silently voided a model in the
# 2026-09-06 pilot. Sonnet 4.5 ignored "no other text" in 87 of 90 samples,
# reasoned aloud, and restated the stated household income before answering.
# The first-dollar parser returned $100,000 for all nine of its cells, and the
# parse rate read 100% because it had parsed *something*. Synthetic cases are
# not enough here -- the failure was in how a real model actually writes.
# --------------------------------------------------------------------------- #
FIXTURE = Path(__file__).parent / "fixtures" / "sonnet_income_echo.json"


def _income_echo_cases() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


def test_income_echo_real_transcripts():
    """Verbatim pilot completions must parse to the verdict, not the income.

    These predate the ANSWER-line format, so they exercise the fallback path --
    which is what a non-compliant reply still lands on.
    """
    cases = _income_echo_cases()
    assert len(cases) >= 5
    for case in cases:
        assert "100,000" in case["completion"] or "100k" in case["completion"].lower()
        assert parse_dollars(case["completion"]) == case["expected"]


def test_answer_line_beats_everything_before_it():
    """The extraction contract: reasoning is never scanned for the answer."""
    reply = (
        "The household earns $100,000 and a common heuristic is 1% of income,\n"
        "which would be $1,000. That feels high for a non-local watershed.\n"
        "ANSWER: $250"
    )
    assert parse_dollars(reply) == 250
    assert answer_line(reply) == "$250"
    assert answer_line("no marker here") is None
    assert parse_vote("Costs are high, so no.\nANSWER: Yes") is True
    assert parse_interval("Maybe $900.\nANSWER: $100, $250, $600") == (100, 250, 600)


@pytest.mark.xfail(
    reason="bare-number fallback fires on the final line; '5 years' parses as $5",
    strict=True,
)
def test_trailing_prose_without_a_dollar_sign_does_not_swallow_a_stray_number():
    """Same failure class as the income echo, different source.

    When the final line carries no '$', the fallback takes the last bare number
    on it -- so a completion closing "paid annually over 5 years" returns 5.0.
    It did not fire in the pilot because Sonnet always ended on a bare amount,
    but it is latent. The fix would be to restrict the bare-number fallback to
    the full-text pass and let a '$'-free final line fall through.
    """
    assert (
        parse_dollars("I would advise $250 per year.\nPaid annually over 5 years.")
        == 250
    )


def test_parse_interval():
    assert parse_interval("$100\n$250\n$600") == (100, 250, 600)
    assert parse_interval("$600\n$250\n$100") is None  # not ascending
    assert parse_interval("$100") is None


# --------------------------------------------------------------------------- #
# WTP recovery
# --------------------------------------------------------------------------- #
def test_turnbull_recovers_a_step_threshold():
    """Deterministic yes-iff-cheap responses should integrate to the threshold."""
    # Fixed dense ladder so this does not track the instrument cost trim.
    bids = [20, 50, 75, 100, 150, 200, 250, 350, 500, 750]
    votes = [b <= 250 for b in bids]
    est = wtp.estimate(bids, votes)
    assert est.turnbull_mean == pytest.approx(250, abs=60)
    assert not est.censored


def test_logit_recovers_a_noisy_threshold():
    bids = []
    votes = []
    for bid in [20, 50, 75, 100, 150, 200, 250, 350, 500, 750]:
        for i in range(20):
            bids.append(bid)
            # Smooth-ish acceptance curve centred near $250.
            votes.append(i < round(20 / (1 + pow(2.718, (bid - 250) / 60.0))))
    est = wtp.estimate(bids, votes)
    assert est.logit_median == pytest.approx(250, abs=40)
    assert est.logit_slope is not None and est.logit_slope < 0


def test_always_yes_is_reported_as_censored_not_extrapolated():
    bids = load_bids()
    est = wtp.estimate(bids, [True] * len(bids))
    assert est.censored
    assert est.logit_median is None
    assert est.preferred is None


def test_unparsed_votes_are_dropped_not_counted():
    bids = [100, 100, 250]
    est = wtp.estimate(bids, [True, None, False])
    assert est.n == 2
