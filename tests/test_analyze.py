"""Coherence report works on an open-ended-only pilot (no referendum logs)."""

from __future__ import annotations

from scripts.analyze_coherence import direct_wtp, primary_wtp, report


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
