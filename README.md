# LLM valuation evaluations

When a language model is handed a real environmental valuation instrument, do
the numbers it produces cohere with each other?

This repository gives frontier language models the stated-preference
referendum from Vossler et al. (2023, *PNAS*), using the survey's own wording,
its own six-level quality scale and its own bid ladder. It then checks whether
the votes behave as a valuation should. It is the code and data behind:

> Daniel Robert Kling Alexander and Catherine Louise Kling (2026).
> *Validity Without Ground Truth: What Stated-Preference Economics Offers the
> Evaluation of Language Models.* arXiv:2610.10506.
> [https://arxiv.org/abs/2610.10506](https://arxiv.org/abs/2610.10506)

Built on [Inspect AI](https://inspect.aisi.org.uk/).

## Reproduce Table A1

No API key and no model calls are needed. The votes are in the repo.

```bash
pip install -r requirements.txt
python scripts/estimate_logit_wtp.py --draws results/referendum_draws.csv --csv results/logit_wtp.csv
```

Table A1 is the `income == 75000` rows of `results/logit_wtp.csv`. `logit_wtp`
is α/β from a Firth-penalized logit of the vote on the tax and `se` is its
delta-method standard error. A blank estimate means the price coefficient is not
significantly positive, and `beyond_ladder` marks an estimate above the $3,000
top bid. The $35,000 and $200,000 rows are the same fit at the other two
incomes.

The data files:

| File | One row per | What it holds |
|---|---|---|
| [`results/referendum_draws.csv`](results/referendum_draws.csv) | model response | model, income, scenario, bid, replicate, parsed vote (1/0, blank if unparsed), run date, source log |
| [`results/referendum_yes_share.csv`](results/referendum_yes_share.csv) | model × income × cell | yes votes and parsed votes at each of the ten bids |
| [`results/referendum_prompt_example.txt`](results/referendum_prompt_example.txt) | cell | the full prompt as a model saw it, at a $250 bid |

Both CSVs are exported from the Inspect logs (about 100 MB, not in the repo) by
`scripts/export_referendum_draws.py`. Two model names, `claude-sonnet-5` and
`gpt-5.6-terra`, were undated aliases when the runs were made, so a rerun today
may reach a different snapshot. See [`PLAN.md`](PLAN.md).

## The question, and what it is not

The obvious framing is silicon sampling: treat the model as a stand-in for a
population, treat the human responses as an answer key, and score the gap. This
evaluation deliberately does not do that.

The model is not a sample of anybody. It is asked to advise a household on a
valuation task, so its dollar figure is neither right nor wrong. What *is*
checkable is whether its answers cohere:

- **Scope.** Does willingness to pay respond to how much the policy improves?
- **Distance.** Does it fall off for a watershed that does not contain the
  household's home?
- **Spatial scale.** Does it hold up when the policy covers the whole region?
- **Income.** Does it rise with household income?

None of those need a human number. The published human estimates come in
afterwards as a separate comparison, not as a target.

Because the model is asked to advise rather than to be a respondent, these
checks are normative rather than descriptive. A person whose valuations violate
scope has cognitive limits, which is an interesting fact about people. An
assistant that recommends paying *less* for a policy that delivers strictly more
has made an error, and no preference story excuses it.

## The sharpest test

A minimum-Level-2 floor delivers everything a minimum-Level-3 floor delivers and
strictly more. So `WTP(min2) >= WTP(min3)` is required, with no human baseline,
no assumption about the baseline mix and no appeal to anyone's values. The
scenarios are constructed so this pair is never degenerate
(`test_min2_dominates_min3`, `test_no_scenario_is_degenerate`).

## Design

Nine scenarios: three policy types (one-level improvement, minimum Level 2,
minimum Level 3) crossed with three spatial units (local watershed, non-local
watershed, full study region). Each is put to six models as a yes/no referendum
at ten bids from $20 to $3,000 a year, ten draws per bid, at household incomes
of $35,000, $75,000 and $200,000. That gives 100 votes per model, cell and
income.

Every cell has a published human mean from Vossler et al. Table 2:

| | local watershed | non-local watershed | study region |
|---|---|---|---|
| One-level improvement | $316 (13) | $165 (11) | $300 (12) |
| Minimum Level 2 | $492 (21) | $225 (15) | $463 (18) |
| Minimum Level 3 | $217 (10) | $95 (9) | $207 (9) |

*Human mean household WTP, 2021 dollars per year over five years, SE in
parentheses. Vossler et al. Table 2, Model 1.*

Earlier rounds asked the same nine cells for an open-ended dollar amount, with
the model as an advisor and as a household member. Those rounds, the referendum
and the income-and-basin round are written up in [`RESULTS.md`](RESULTS.md),
newest first. Where a round had a prediction, it was frozen in [`PLAN.md`](PLAN.md)
before any generations.

## A rule that must not break

The survey never showed respondents the words "Biological Condition Gradient"
(SI S2). The six levels appeared only as "Level 1 – Natural State" through
"Level 6 – Extreme Degradation". Keeping the name out of prompts is faithful to
the instrument and is also confound control, because naming the published
framework invites a model to recall the study instead of reasoning about the
scenario in front of it. `test_bcg_terminology_never_reaches_a_model` enforces
this across every scenario, format and context setting.

## The source study

- **Paper:** Vossler, Dolph, Finlay, Keiser, Kling & Phaneuf (2023), *Valuing
  improvements in the ecological integrity of local and regional waters using
  the biological condition gradient*,
  [PNAS 120(18) e2120251119](https://doi.org/10.1073/pnas.2120251119).
  Free full text: [PMC10160978](https://pmc.ncbi.nlm.nih.gov/articles/PMC10160978/).
- **The survey as administered:** supplementary file `pnas.2120251119.sd01.pdf`
  on the paper page, with every screen respondents saw, including the referendum
  wording and the policy-summary table this repo reproduces.
- **SI appendix:** `pnas.2120251119.sapp.pdf`, with the experimental design, the
  mixed logit specifications and Tables S1–S7.

## Running new evaluations

```bash
pip install -r requirements.txt
cp .env.example .env   # add API keys

# Referendum: the six watershed cells at $75,000
python scripts/run_referendum.py
# Income and basin: all nine cells at two more incomes, and the region at $75,000
python scripts/run_referendum.py --study-region --income 35000 200000
python scripts/run_referendum.py --only-study-region --income 75000

# Rebuild the public CSVs and the fit from the new logs
python scripts/export_referendum_draws.py
python scripts/estimate_logit_wtp.py --draws results/referendum_draws.csv --csv results/logit_wtp.csv

# Earlier open-ended rounds (R12, R13)
python scripts/run_pilot.py
python scripts/run_r13.py
python scripts/analyze_coherence.py logs/r13 --csv results/r13.csv

# See any prompt without calling a model
python scripts/preview_prompt.py min2_local_watershed --bid 250

pytest -q      # no API key needed
```

When calling a task directly with `inspect eval src/tasks/...`,
`-T with_levels=false` drops the level definitions. Human respondents spent
roughly thirty minutes learning the scale, with graphics and comprehension
checks, so neither setting reproduces their condition. Reasoning models that
reject an explicit temperature need `-T temperature=null`.

## Layout

```
data/instrument.yaml        levels, change rules, region copy, bids, baseline
data/scenarios.yaml         nine-cell experimental grid
data/human_benchmarks.yaml  Table 2 estimates with standard errors
prompts/                    verbatim instrument text
src/schema.py               level arithmetic, dominance, response parsing
src/scenarios.py            renders the policy-summary table
src/wtp.py                  yes-share curves and WTP from the vote curve
src/tasks/                  Inspect tasks
scripts/                    run, export, fit and audit scripts
results/                    public data and tables (see above)
tests/                      instrument and analysis tests
PLAN.md                     frozen predictions, round by round
RESULTS.md                  round-by-round notes, newest first
docs/notes/                 working memos, kept for the record
```

## Credit

The survey instrument, the six-level scale, and every human estimate are the
work of Vossler, Dolph, Finlay, Keiser, Kling and Phaneuf. This repository only
points a different kind of respondent at their design.

## Tools used

AI coding assistants drafted code and text under the authors' direction.

- **Cursor** (commits carry `Co-authored-by: Cursor`) helped revise the
  evaluation harness (`src/`), the pilot and referendum runners, and some
  analysis checks, and helped record the Saturday referendum and the income
  and basin referendum.
- **Claude (Anthropic), via Claude Code,** helped write the initial harness,
  later analysis scripts, the R13 run record and its check against the raw
  logs, and drafts of `PLAN.md`, `RESULTS.md`, and the working paper. Those
  commits carry `Co-Authored-By: Claude Opus 5` or `Claude Opus 5.5`. The
  assistant was Claude Opus. The Claude models under evaluation are Haiku
  and Sonnet.

The authors set the design, formulated and froze the predictions, and are
responsible for every result reported here. The R13 prediction and the income
and basin prediction were committed before those generations. The open-ended
pilot prediction was left unfilled, and the Saturday referendum was recorded
as exploratory.
