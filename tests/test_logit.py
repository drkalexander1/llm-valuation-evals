from __future__ import annotations

from pathlib import Path

from scripts.estimate_logit_wtp import counts_from_draws

HEADER = "model,income,scenario_id,change,locality,spatial_unit,bid,replicate,vote,run_date,source_log\n"


def test_counts_from_draws_tallies_parsed_votes_and_skips_blanks(tmp_path: Path):
    path = tmp_path / "draws.csv"
    path.write_text(
        HEADER
        + "m,75000,s,one_level,local,watershed,20,1,1,2026-09-20,x\n"
        + "m,75000,s,one_level,local,watershed,20,2,0,2026-09-20,x\n"
        + "m,75000,s,one_level,local,watershed,20,3,,2026-09-20,x\n"
        + "m,75000,s,one_level,local,watershed,500,1,0,2026-09-20,x\n"
        + "m,35000,s,one_level,local,watershed,20,1,1,2026-09-28,x\n"
    )
    assert counts_from_draws(path) == {
        "m|75000|s": {"20": [1, 2], "500": [0, 1]},
        "m|35000|s": {"20": [1, 1]},
    }


def test_public_draws_cover_every_cell():
    path = Path(__file__).resolve().parents[1] / "results" / "referendum_draws.csv"
    counts = counts_from_draws(path)
    assert len(counts) == 162  # 6 models x (9 cells x 3 incomes)
    assert all(len(bids) == 10 for bids in counts.values())
