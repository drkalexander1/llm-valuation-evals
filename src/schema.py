"""Scenario schema, level-distribution arithmetic, and response parsing.

Labels, change rules, and region copy live in data/instrument.yaml. Displayed
averages are computed from baseline shares plus the change apply map -- they
are not independently settable.

The six quality levels are the survey's own labels. The underlying construct is
the EPA Biological Condition Gradient, but the instrument deliberately withheld
that terminology from respondents (SI S2) and so do we: the acronym must never
reach a model, both for fidelity and because naming it invites retrieval of the
published framework instead of reasoning about the scenario.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator, model_validator

from src import DEFAULT_BENCHMARKS_PATH, DEFAULT_INSTRUMENT_PATH, DEFAULT_SCENARIOS_PATH

Format = Literal["referendum", "open_ended", "interval"]


def _int_keys(value: dict) -> dict[int, object]:
    return {int(k): v for k, v in value.items()}


class LevelDistribution(BaseModel):
    """Share of a policy region's waters at each quality level; shares sum to 1."""

    shares: dict[int, float]

    @field_validator("shares", mode="before")
    @classmethod
    def _int_levels(cls, v: dict) -> dict:
        return _int_keys(v)

    @field_validator("shares")
    @classmethod
    def _check(cls, v: dict[int, float]) -> dict[int, float]:
        if not v:
            raise ValueError("shares must be non-empty")
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

    def apply(self, change: str) -> "LevelDistribution":
        out: dict[int, float] = {}
        for level, share in self.shares.items():
            dest = apply_change_to_level(level, change)
            out[dest] = out.get(dest, 0.0) + share
        return LevelDistribution(shares=out)

    def is_degenerate_for(self, change: str) -> bool:
        """True when the change leaves the region unaltered.

        The survey dropped such proposals as meaningless (SI S2): a region
        entirely at Level 3 has no 'minimum Level 3' policy to vote on.
        """
        return self.apply(change).shares == self.shares


class ChangeSpec(BaseModel):
    description: str
    apply: dict[int, int]
    notes: str | None = None

    @field_validator("apply", mode="before")
    @classmethod
    def _int_map(cls, v: dict) -> dict[int, int]:
        return {int(k): int(dest) for k, dest in v.items()}


class RegionSpec(BaseModel):
    description: str
    includes_home: bool


class TaxWindow(BaseModel):
    years: int
    start: int
    end: int


class Household(BaseModel):
    income: int
    size: int = 4
    description: str = "This is a {size}-person household with an annual income of {income}."

    def rendered_description(self) -> str:
        return self.description.format(
            income=f"${self.income:,}",
            size=self.size,
        )


class Instrument(BaseModel):
    """The expert-facing stated-preference instrument."""

    basin: str
    levels: dict[int, str]
    changes: dict[str, ChangeSpec]
    regions: dict[str, RegionSpec]
    household: Household
    tax: TaxWindow
    bids: list[int]
    baseline: LevelDistribution

    @field_validator("levels", mode="before")
    @classmethod
    def _int_levels(cls, v: dict) -> dict[int, str]:
        return {int(k): str(label) for k, label in v.items()}

    @model_validator(mode="after")
    def _consistent(self) -> "Instrument":
        declared = set(self.levels)
        for level in self.baseline.shares:
            if level not in declared:
                raise ValueError(
                    f"baseline share at level {level} is not a declared level "
                    f"{sorted(declared)}"
                )
        for name, spec in self.changes.items():
            if set(spec.apply) != declared:
                raise ValueError(
                    f"{name}: apply must map every declared level "
                    f"{sorted(declared)}, got {sorted(spec.apply)}"
                )
            unknown = [dest for dest in spec.apply.values() if dest not in declared]
            if unknown:
                raise ValueError(f"{name}: apply targets unknown levels {unknown}")
        return self

    def fill(self, text: str) -> str:
        """Substitute instrument fields into prompt templates."""
        income = f"${self.household.income:,}"
        return text.format(
            years=self.tax.years,
            start=self.tax.start,
            end=self.tax.end,
            basin=self.basin,
            income=income,
            size=self.household.size,
            household=self.household.rendered_description(),
        )


def load_instrument(path: Path | None = None) -> Instrument:
    return _load_instrument(str((path or DEFAULT_INSTRUMENT_PATH).resolve()))


@lru_cache(maxsize=None)
def _load_instrument(resolved: str) -> Instrument:
    payload = yaml.safe_load(Path(resolved).read_text(encoding="utf-8"))
    return Instrument.model_validate(payload)


def fill_instrument_placeholders(text: str, instrument: Instrument | None = None) -> str:
    return (instrument or load_instrument()).fill(text)


def apply_change_to_level(
    level: int, change: str, instrument: Instrument | None = None
) -> int:
    inst = instrument or load_instrument()
    spec = inst.changes.get(change)
    if spec is None:
        raise ValueError(f"unknown change type {change!r}")
    if level not in spec.apply:
        raise ValueError(f"change {change!r} has no mapping for level {level}")
    return spec.apply[level]


def dominates(a: str, b: str, baseline: LevelDistribution) -> bool:
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
    change: str
    locality: str
    spatial_unit: str
    area_sq_miles: int
    baseline: LevelDistribution
    home_level: int | None = None
    notes: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def _against_instrument(self) -> "Scenario":
        inst = load_instrument()
        if self.change not in inst.changes:
            raise ValueError(
                f"unknown change {self.change!r}; known: {sorted(inst.changes)}"
            )
        if self.locality not in inst.regions:
            raise ValueError(
                f"unknown locality {self.locality!r}; known: {sorted(inst.regions)}"
            )
        if self.home_level is not None and self.home_level not in inst.levels:
            raise ValueError(
                f"home_level must be within {sorted(inst.levels)}"
            )
        return self

    @property
    def change_description(self) -> str:
        if self.description is not None:
            return self.description
        return load_instrument().changes[self.change].description

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
        return load_instrument().regions[self.locality].includes_home


class Benchmark(BaseModel):
    """A published mean WTP with its standard error (Table 2, Model 1)."""

    scenario_id: str
    mean: float
    stderr: float
    source: str = "Vossler et al. 2023 PNAS Table 2 (Model 1)"


def load_scenarios(path: Path | None = None) -> list[Scenario]:
    inst = load_instrument()
    payload = yaml.safe_load((path or DEFAULT_SCENARIOS_PATH).read_text(encoding="utf-8"))
    rows: list[Scenario] = []
    for row in payload["scenarios"]:
        row = dict(row)
        if "baseline" not in row:
            row["baseline"] = inst.baseline
        rows.append(Scenario.model_validate(row))
    return rows


def load_benchmarks(path: Path | None = None) -> dict[str, Benchmark]:
    payload = yaml.safe_load((path or DEFAULT_BENCHMARKS_PATH).read_text(encoding="utf-8"))
    rows = [Benchmark.model_validate(r) for r in payload["benchmarks"]]
    return {b.scenario_id: b for b in rows}


def load_bids(path: Path | None = None) -> list[int]:
    return list(load_instrument(path).bids)


# --------------------------------------------------------------------------- #
# Response parsing
# --------------------------------------------------------------------------- #
_NUMBER_RE = re.compile(r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")

_YES_RE = re.compile(r"\bvote\s*[\"']?\s*yes|\byes\b", re.IGNORECASE)
_NO_RE = re.compile(r"\bvote\s*[\"']?\s*no|\bno\b", re.IGNORECASE)

_ANSWER_RE = re.compile(r"^\s*\**\s*ANSWER\s*\**\s*:\s*(.+?)\s*\**\s*$", re.IGNORECASE)


def answer_line(text: str) -> str | None:
    """Content after the last 'ANSWER:' marker, or None if the model omitted it.

    The prompts let a model reason and then require a delimited final line. That
    is the whole extraction contract: everything before the marker is reasoning
    and must not be scanned for numbers.

    The 2026-09-06 pilot is why. Sonnet 4.5 reasoned aloud in 87 of 90 samples
    and restated the stated household income on the way; a parser scanning free
    text returned $100,000 for all nine of its cells while the parse rate read
    100%. Suppressing reasoning is not the fix either -- it worked on three
    models and failed on one, which meant the run compared a reasoning model
    against three one-shot models. Letting every model reason and delimiting the
    answer removes both problems at once.
    """
    found: str | None = None
    for line in text.splitlines():
        match = _ANSWER_RE.match(line.strip())
        if match:
            found = match.group(1).strip()
    return found


def parse_vote(text: str) -> bool | None:
    """Parse a referendum vote. None when the model did not commit.

    Prefers the delimited ANSWER line; falls back to the final non-empty line
    for replies that ignored the format, since an early 'no' inside reasoning
    should not outrank the verdict.
    """
    marked = answer_line(text)
    if marked is not None:
        text = marked
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
    """Parse a single dollar amount.

    Prefers the delimited ANSWER line. Failing that, last '$' on the final
    non-empty line, then the last '$' in the full text -- a best-effort fallback
    for replies that ignored the format, not the intended path.
    """
    marked = answer_line(text)
    if marked is not None:
        text = marked

    def _from(chunk: str) -> float | None:
        cleaned = chunk.replace(",", "")
        dollars = list(re.finditer(r"\$\s*(\d+(?:\.\d+)?)", cleaned))
        if dollars:
            return float(dollars[-1].group(1))
        match = list(_NUMBER_RE.finditer(cleaned))
        return float(match[-1].group(0).replace(",", "")) if match else None

    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if lines:
        last_line = _from(lines[-1])
        if last_line is not None:
            return last_line
    return _from(text)


def parse_interval(text: str) -> tuple[float, float, float] | None:
    """Parse p10/p50/p90 as three ascending numbers.

    Reads the delimited ANSWER line when present, so figures mentioned while
    reasoning cannot be mistaken for the interval.
    """
    marked = answer_line(text)
    if marked is not None:
        text = marked
    nums = [float(m.group(0).replace(",", "")) for m in _NUMBER_RE.finditer(text)]
    if len(nums) < 3:
        return None
    p10, p50, p90 = nums[0], nums[1], nums[2]
    if not (p10 <= p50 <= p90):
        return None
    return p10, p50, p90
