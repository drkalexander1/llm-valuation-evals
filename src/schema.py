"""Scenario schema, level-distribution arithmetic, and response parsing.

The six quality levels are the survey's own labels. The underlying construct is
the EPA Biological Condition Gradient, but the instrument deliberately withheld
that terminology from respondents (SI S2) and so do we: the acronym must never
reach a model, both for fidelity and because naming it invites retrieval of the
published framework instead of reasoning about the scenario.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator

from src import DEFAULT_BENCHMARKS_PATH, DEFAULT_SCENARIOS_PATH

ChangeType = Literal["one_level", "min2", "min3", "l3_to_l2"]
Locality = Literal["local", "nonlocal", "region"]
Format = Literal["referendum", "open_ended", "interval"]

LEVEL_LABELS: dict[int, str] = {
    1: "Level 1 - Natural State",
    2: "Level 2 - Close to Natural State",
    3: "Level 3 - Some Changes Noticeable",
    4: "Level 4 - Many Changes Noticeable",
    5: "Level 5 - Major Degradation",
    6: "Level 6 - Extreme Degradation",
}

# Verbatim from the instrument where observed; reconstructed where marked.
CHANGE_DESCRIPTIONS: dict[ChangeType, str] = {
    # Observed on a voting screen (sd01 p.42).
    "one_level": "All areas within region improve by one level",
    # Observed in Figure S3 for a baseline whose only sub-Level-2 areas were at
    # Level 3. Generalized here; confirm against a min-2 screen with a mixed
    # baseline before treating as verbatim.
    "min2": "All areas currently below Level 2 improved to Level 2",
    # RECONSTRUCTED -- not observed on any screen. Confirm with the authors.
    "min3": "All areas currently below Level 3 improved to Level 3",
    # RECONSTRUCTED -- Table 1 lists this scenario but Table 2 reports no WTP
    # for it, so it has no benchmark and is not in the default cell set.
    "l3_to_l2": "All Level 3 areas improved to Level 2",
}


class LevelDistribution(BaseModel):
    """Share of a policy region's waters at each quality level; shares sum to 1."""

    shares: dict[int, float]

    @field_validator("shares")
    @classmethod
    def _check(cls, v: dict[int, float]) -> dict[int, float]:
        if not v:
            raise ValueError("shares must be non-empty")
        if any(k not in LEVEL_LABELS for k in v):
            raise ValueError(f"levels must be within {sorted(LEVEL_LABELS)}")
        if any(s < 0 for s in v.values()):
            raise ValueError("shares must be non-negative")
        total = sum(v.values())
        if total <= 0:
            raise ValueError("shares must sum to a positive value")
        # Published figures are rounded and need not sum to exactly 1.
        return {k: s / total for k, s in v.items()}

    @property
    def average(self) -> float:
        return sum(level * share for level, share in self.shares.items())

    def apply(self, change: ChangeType) -> "LevelDistribution":
        out: dict[int, float] = {}
        for level, share in self.shares.items():
            out[apply_change_to_level(level, change)] = (
                out.get(apply_change_to_level(level, change), 0.0) + share
            )
        return LevelDistribution(shares=out)

    def is_degenerate_for(self, change: ChangeType) -> bool:
        """True when the change leaves the region unaltered.

        The survey dropped such proposals as meaningless (SI S2): a region
        entirely at Level 3 has no 'minimum Level 3' policy to vote on.
        """
        return self.apply(change).shares == self.shares


def apply_change_to_level(level: int, change: ChangeType) -> int:
    if change == "one_level":
        return max(1, level - 1)
    if change == "min2":
        return min(level, 2)
    if change == "min3":
        return min(level, 3)
    if change == "l3_to_l2":
        return 2 if level == 3 else level
    raise ValueError(f"unknown change type {change!r}")


def dominates(a: ChangeType, b: ChangeType, baseline: LevelDistribution) -> bool:
    """True when policy `a` leaves every water body at least as good as `b`.

    Used for the nested-dominance check. min2 dominates min3 for any baseline
    containing waters below Level 2, because a Level-2 floor delivers everything
    a Level-3 floor delivers and strictly more.
    """
    return all(
        apply_change_to_level(level, a) <= apply_change_to_level(level, b)
        for level in baseline.shares
    )


class Scenario(BaseModel):
    id: str
    change: ChangeType
    locality: Locality
    spatial_unit: str
    area_sq_miles: int
    baseline: LevelDistribution
    home_level: int | None = None
    notes: str | None = None

    @field_validator("home_level")
    @classmethod
    def _home(cls, v: int | None) -> int | None:
        if v is not None and v not in LEVEL_LABELS:
            raise ValueError(f"home_level must be within {sorted(LEVEL_LABELS)}")
        return v

    @property
    def improved(self) -> LevelDistribution:
        return self.baseline.apply(self.change)

    @property
    def home_level_after(self) -> int | None:
        """Home quality after the policy.

        Not always changed: Figure S3 shows a home at Level 4 unaffected by a
        policy that only touched Level 3 areas. Compute it, never assume it.
        """
        if self.home_level is None:
            return None
        return apply_change_to_level(self.home_level, self.change)

    @property
    def includes_home(self) -> bool:
        return self.locality in ("local", "region")


class Benchmark(BaseModel):
    """A published mean WTP with its standard error (Table 2, Model 1)."""

    scenario_id: str
    mean: float
    stderr: float
    source: str = "Vossler et al. 2023 PNAS Table 2 (Model 1)"


def load_scenarios(path: Path | None = None) -> list[Scenario]:
    payload = yaml.safe_load((path or DEFAULT_SCENARIOS_PATH).read_text(encoding="utf-8"))
    return [Scenario.model_validate(row) for row in payload["scenarios"]]


def load_benchmarks(path: Path | None = None) -> dict[str, Benchmark]:
    payload = yaml.safe_load((path or DEFAULT_BENCHMARKS_PATH).read_text(encoding="utf-8"))
    rows = [Benchmark.model_validate(r) for r in payload["benchmarks"]]
    return {b.scenario_id: b for b in rows}


def load_bids(path: Path | None = None) -> list[int]:
    payload = yaml.safe_load((path or DEFAULT_SCENARIOS_PATH).read_text(encoding="utf-8"))
    return [int(b) for b in payload["bids"]]


# --------------------------------------------------------------------------- #
# Response parsing
# --------------------------------------------------------------------------- #
_NUMBER_RE = re.compile(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")

_YES_RE = re.compile(r"\bvote\s*[\"']?\s*yes|\byes\b", re.IGNORECASE)
_NO_RE = re.compile(r"\bvote\s*[\"']?\s*no|\bno\b", re.IGNORECASE)


def parse_vote(text: str) -> bool | None:
    """Parse a referendum vote. None when the model did not commit.

    Checks the final non-empty line first: models often reason first and answer
    last, and an early 'no' inside the reasoning should not outrank the verdict.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    for candidate in ([lines[-1]] if lines else []) + [text]:
        yes = _YES_RE.search(candidate)
        no = _NO_RE.search(candidate)
        if yes and not no:
            return True
        if no and not yes:
            return False
        if yes and no:
            return yes.start() < no.start()
    return None


def parse_dollars(text: str) -> float | None:
    """Parse a single dollar amount, preferring one prefixed with '$'."""
    cleaned = text.replace(",", "")
    dollar = re.search(r"\$\s*(\d+(?:\.\d+)?)", cleaned)
    if dollar:
        return float(dollar.group(1))
    match = _NUMBER_RE.search(cleaned)
    return float(match.group(0).replace(",", "")) if match else None


def parse_interval(text: str) -> tuple[float, float, float] | None:
    """Parse p10/p50/p90 as three ascending numbers."""
    nums = [float(m.group(0).replace(",", "")) for m in _NUMBER_RE.finditer(text)]
    if len(nums) < 3:
        return None
    p10, p50, p90 = nums[0], nums[1], nums[2]
    if not (p10 <= p50 <= p90):
        return None
    return p10, p50, p90
