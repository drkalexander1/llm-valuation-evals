# LLM valuation evaluations

When a language model is handed a real environmental valuation instrument, do
the numbers it produces cohere with each other?

This administers the stated-preference referendum from Vossler, Dolph, Finlay,
Keiser, Kling & Phaneuf (2023), *Valuing improvements in the ecological integrity
of local and regional waters using the biological condition gradient*,
[PNAS 120(18) e2120251119](https://doi.org/10.1073/pnas.2120251119), to frontier
models — using the survey's own wording, its own six-level quality scale, and its
own published bid ladder.

Built on [Inspect AI](https://inspect.aisi.org.uk/), alongside
[`llm-anchoring-evals`](https://github.com/drkalexander1/llm-anchoring-evals)
and the rest of the weekly evaluation program.

**Status: this week's pilot is the open-ended arm** (9 scenarios × 10 epochs).
Referendum and interval are built and held for next week. Design is in
[`PLAN.md`](PLAN.md); the prediction must be committed before any generations.

## The question, and what it is not

The obvious framing is silicon sampling — treat the model as a stand-in for a
population, treat the human responses as an answer key, and score the gap. This
evaluation deliberately does not do that.

The model is not a sample of anybody. It is being handed a valuation task, so
there is no fact about what the right answer is and its dollar figure is neither
right nor wrong. What *is* checkable is whether its answers cohere:

- **Scope** — does willingness to pay respond to how much the policy actually
  improves?
- **Distance** — does it fall off for a watershed that does not contain the
  user's home?
- **Spatial scale** — does it scale with the size of the policy region?
- **Format** — does the same value survive being asked three different ways?

None of those need a human number. The published human estimates come in
afterwards as a separate comparison, not as a target.

**One consequence is worth stating plainly.** Because the model is asked to
advise rather than to be a respondent, the coherence checks are normative rather
than descriptive. A person whose valuations violate scope has cognitive limits,
which is an interesting fact about people. An assistant that recommends paying
*less* for a policy delivering strictly more has made an error, and there is no
preference story available to excuse it.

## The sharpest test

A minimum-Level-2 floor delivers everything a minimum-Level-3 floor delivers and
strictly more. So `WTP(min2) >= WTP(min3)` is required — no human baseline, no
assumption about the baseline mix, no appeal to anyone's values. The scenarios
are constructed so this pair is never degenerate (`test_min2_dominates_min3`,
`test_no_scenario_is_degenerate`).

## Design at a glance

Nine scenarios: three policy types (one-level improvement, minimum Level 2,
minimum Level 3) crossed with three spatial units (local watershed, non-local
watershed, full study region). Every one has a published human mean and standard
error from Table 2. Five bids from a thinned Table 1 ladder. Three elicitation
formats. Four models.

| | local watershed | non-local watershed | study region |
|---|---|---|---|
| One-level improvement | $316 (13) | $165 (11) | $300 (12) |
| Minimum Level 2 | $492 (21) | $225 (15) | $463 (18) |
| Minimum Level 3 | $217 (10) | $95 (9) | $207 (9) |

*Human mean household WTP, 2021 dollars per year over five years, SE in
parentheses. Vossler et al. Table 2, Model 1.*

The human data shows three things worth trying to reproduce: the scope ordering
holds in all six of Table 2's columns; WTP is flat from the watershed level up
(316 → 302 → 300) but not below it (152 → 316); and local runs about twice
non-local.

## A rule that must not break

The survey never showed respondents the words "Biological Condition Gradient"
(SI S2) — the six levels appeared only as "Level 1 – Natural State" through
"Level 6 – Extreme Degradation". Keeping the acronym out of prompts is both
faithful to the instrument and necessary confound control: naming the published
framework invites a model to retrieve it instead of reasoning about the scenario
in front of it. `test_bcg_terminology_never_reaches_a_model` enforces this
across every scenario, format, and context setting.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # add API keys

# This week — open-ended pilot
python scripts/run_pilot.py
python scripts/analyze_coherence.py logs/pilot --csv results/coherence.csv

# Next week — referendum and interval (already wired)
inspect eval src/tasks/referendum.py --model anthropic/claude-sonnet-4-5 --epochs 10
inspect eval src/tasks/direct_wtp.py --model anthropic/claude-sonnet-4-5 --epochs 10 -T fmt=interval
```

Context depth is a task parameter, not a fixed choice: `-T with_levels=false`
drops the level definitions. Human respondents spent roughly thirty minutes
learning the scale with graphics and comprehension checks, so neither setting
reproduces their condition and running both is the honest version.

Reasoning models that reject an explicit temperature need `-T temperature=null`.

```bash
pytest -q      # no API key needed
```

## Layout

```
data/instrument.yaml        levels, change rules, region copy, bids, baseline
data/scenarios.yaml         nine-cell experimental grid
data/human_benchmarks.yaml  Table 2 estimates with standard errors
prompts/                    verbatim instrument text
src/schema.py               level arithmetic, dominance, response parsing
src/scenarios.py            renders the policy-summary table
src/wtp.py                  WTP recovery from the vote curve
src/tasks/                  Inspect tasks
scripts/analyze_coherence.py
```

## Credit

The survey instrument, the six-level scale, and every human estimate are the
work of Vossler, Dolph, Finlay, Keiser, Kling and Phaneuf. This repository only
points a different kind of respondent at their design.
