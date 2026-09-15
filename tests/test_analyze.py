"""Coherence report works on an open-ended-only pilot (no referendum logs)."""

from __future__ import annotations

import pytest

from scripts.analyze_coherence import (
    direct_wtp,
    level_shift_L,
    primary_wtp,
    report,
)


def _oe(model: str, sid: str, amount: float) -> dict:
    return {
        "model": model,
        "scenario_id": sid,
        "format": "open_ended",
        "wtp": amount,
    }


def test_primary_wtp_prefers_open_ended_when_no_referendum():
    rows = [_oe("m", "min2_local_watershed", 400)]
    value, source = primary_wtp("m", "min2_local_watershed", {}, direct_wtp(rows))
    assert source == "open_ended"
    assert value == 400


def test_open_ended_pilot_scores_dominance_and_scope(capsys):
    amounts = {
        "min2_local_watershed": 400,
        "one_level_local_watershed": 300,
        "min3_local_watershed": 200,
        "min2_nonlocal_watershed": 180,
        "one_level_nonlocal_watershed": 140,
        "min3_nonlocal_watershed": 90,
        "min2_region": 410,
        "one_level_region": 295,
        "min3_region": 190,
    }
    rows = [_oe("test/model", sid, w) for sid, w in amounts.items()]
    summary = report(rows)
    captured = capsys.readouterr().out
    assert "VIOLATION" not in captured
    assert "skipped (single format this week)" in captured
    assert "region/local" in captured
    assert "x0.45" in captured  # 180/400 distance decay on min2
    local = next(r for r in summary if r["scenario_id"] == "min2_local_watershed")
    assert local["wtp_primary"] == 400
    assert local["primary_source"] == "open_ended"
    assert local["wtp_referendum"] is None
    assert local["frame"] == "advisor"


def test_frames_do_not_mix_when_scoring_medians():
    rows = [
        {**_oe("m", "min2_local_watershed", 100), "frame": "advisor"},
        {**_oe("m", "min2_local_watershed", 400), "frame": "persona"},
    ]
    medians = direct_wtp(rows)
    assert medians[("m", "min2_local_watershed", "open_ended", "advisor")] == 100
    assert medians[("m", "min2_local_watershed", "open_ended", "persona")] == 400


def test_level_shift_L_is_one_when_arms_match():
    cells = [
        "min2_local_watershed",
        "one_level_local_watershed",
        "min3_local_watershed",
    ]
    advisor = {sid: [100.0, 100.0] for sid in cells}
    persona = {sid: [100.0, 100.0] for sid in cells}
    shift = level_shift_L(advisor, persona, n_boot=50)
    assert shift["L"] == pytest.approx(1.0)
    assert shift["label"] == "A. No change"
    assert shift["dropped"] == []


def test_level_shift_L_doubles_when_persona_is_twice_advisor():
    cells = [
        "min2_local_watershed",
        "one_level_local_watershed",
        "min3_local_watershed",
    ]
    advisor = {sid: [100.0] for sid in cells}
    persona = {sid: [200.0] for sid in cells}
    shift = level_shift_L(advisor, persona, n_boot=20)
    assert shift["L"] == pytest.approx(2.0)
    assert shift["label"] == "C. Rise"


def test_level_shift_L_drops_zero_median_cells():
    advisor = {"keep": [100.0], "zero": [0.0]}
    persona = {"keep": [100.0], "zero": [50.0]}
    shift = level_shift_L(advisor, persona, n_boot=10)
    assert shift["used"] == ["keep"]
    assert shift["dropped"] == ["zero"]
    assert shift["L"] == pytest.approx(1.0)
