"""Shared paths and package markers."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROMPTS_DIR = ROOT / "prompts"
DEFAULT_SCENARIOS_PATH = DATA_DIR / "scenarios.yaml"
DEFAULT_BENCHMARKS_PATH = DATA_DIR / "human_benchmarks.yaml"
