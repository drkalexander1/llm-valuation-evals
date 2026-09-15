# Predeclared plan — water quality valuation pilot

## Goal

Test whether a language model handed a real stated-preference instrument
produces willingness-to-pay figures that cohere with each other, and separately
how those figures compare to the human sample the instrument was built for.

Not a silicon-sampling study. The human estimates are a comparison, not a target
— see README. The design consequence is that the primary endpoints need no
human number at all.

## This week's pilot — open-ended only

Referendum and interval stay in the repo for next week (thinned ladder and
p10/p50/p90 are recorded, not dropped). This week's writeup uses the open-ended
arm: one dollar amount per scenario, no vote curve, no format comparison.

- **Models:** Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, GPT-4o mini
- **Scenarios:** 9 — {one-level improvement, minimum Level 2, minimum Level 3}
  × {local watershed, non-local watershed, study region}
- **Format:** open-ended
- **Repeats:** 10 epochs
- **Temperature:** 1.0
- **Context depth:** `with_levels=true`
- **Status:** exploratory pilot, not a powered model comparison

Held for next week: referendum on the thinned Table 1 ladder ($20 / 100 / 250 /
500 / 750), interval elicitation, format invariance, `with_levels=false`.

## Baseline construction

Baseline level distribution is held fixed across spatial units, using the
study-region distribution from SI Figure S2 (Level 2 4.36%, Level 3 41.63%,
Level 4 48.97%, Level 5 4.53%). The real survey drew a respondent-specific
baseline from their own watershed. Holding it fixed isolates the two things
Table 2's columns vary — policy area size, and whether the area contains the
user's home — at the cost of departing from the numbers any one respondent saw.

Achieved averages under this baseline: minimum Level 2 → 2.00, one-level
improvement → 2.54, minimum Level 3 → 2.96. That ordering matches the direction
of the human WTP ordering, so the scope test is not fighting the scenario
design. **This is baseline-dependent:** for a heavily degraded region a
minimum-Level-3 floor can deliver a better average than a one-level improvement,
and the ordering flips. Recorded because it is easy to mistake for a general
property.

## Cost

```
This week (open-ended): 9 scenarios x 10 epochs  =   90 / model
4 models                                         =  360 generations

Next week (held):
Referendum : 9 scenarios x 5 bids x 10 epochs    =  450 / model
Interval   : 9 scenarios x 10 epochs             =   90 / model
```

Single generation per sample. Trim order if needed: epochs 10 → 5, then drop the
study-region column, then drop a model.

## Endpoints

### Primary — no human number required

1. **Nested dominance.** `WTP(min2) >= WTP(min3)` within model and spatial unit.
   A strict superset of improvements, so a violation is an error rather than a
   preference. This is the sharpest single test in the design.
2. **Scope ordering.** min2 > one-level > min3, checked independently in each
   spatial unit.
3. **Spatial-scale response.** Local watershed vs. study region, holding the
   change type fixed.
4. **Distance decay.** Non-local / local ratio at the watershed.
5. **Format invariance.** Deferred — needs the referendum and interval arms.

### Secondary — against the human sample

6. Per-scenario level comparison against the nine published means. Report the
   ratio and whether the model's figure sits inside the published interval,
   noting that the published values are mixed-logit population parameters and
   the model's is a recommendation — unlike objects, deliberately compared.
7. Whether the three human patterns reproduce: scope ordering in every column,
   flatness from the watershed up, roughly 2:1 local to non-local.

### Reporting rules

- This week's figure is the median of the ten open-ended amounts per cell.
- Parse rate is an endpoint, not a diagnostic. A refusal-heavy model is a result.
- Referendum reporting rules (Turnbull + logit; censor at $750) apply when that
  arm is run, not this week.

## Prediction — FREEZE BEFORE RUNNING

> **TODO (Daniel):** write the prediction here and commit it before any
> generations run, per R10 practice. With nine benchmarks and six replications
> of the scope ordering available, this design is unusually easy to read
> retrospectively.
>
> At minimum, commit to a direction on:
> - whether the models scale WTP with policy area where the humans were flat
> - whether any model violates nested dominance
> - whether recovered levels land above or below the human means
> Format invariance is next week.

## Pre-run checks

- [x] Refusal smoke test — 20/20 parsed on Haiku (8 referendum + 6 open-ended
      + 6 interval). Referendum was already all-yes through $750; interval p50
      stuck at $280. Open-ended moved with distance.
- [ ] Confirm the `min3` and `l3_to_l2` change-description strings against the
      questionnaire or with the authors; both are reconstructed, not observed
- [ ] Eyeball Table 1 in the paper against the spatial units used here
- [ ] `pytest -q` clean
- [ ] Prediction committed

## Deviations from the human administration

1. Graphics replaced by text. Respondents saw illustrated appearance, use, and
   biodiversity panels per level; models get the labels.
2. Maps replaced by a text description of the policy region.
3. Repeats at temperature 1 substituting for population heterogeneity. Humans
   vary because they are different people. This is the most attackable
   assumption in the design and is not defended, only stated.
4. No respondent. The model advises on a stated scenario rather than answering
   as a household with a real zip code. Deliberate — it is what makes the
   coherence checks normative.
5. Baseline distribution held fixed across spatial units rather than drawn from
   the user's own watershed.
6. Published WTP are mixed-logit estimates (Model 1, 500 Halton draws,
   delta-method SEs), not raw response means.

---

# R13 — advisor vs household persona (frozen 2026-09-14)

## Question

Is the advisor framing producing R12's levels? R12 put the model in the
advisor's chair on purpose (Deviation 4). R13 tests that choice: same questions,
asked of a model speaking as a member of the household.

## Design

- **Arms:** advisor (`system_advisor.txt` + `open_ended.txt`) vs persona
  (`system_persona.txt` + `open_ended_persona.txt`), run together.
- **Why advisor is rerun rather than taken from R12:** R12 ran under the
  pre-`eba168b` prompts ("Reply with exactly one dollar amount in the form $N. No
  other text." / "Do not add caveats"). The current prompts allow reasoning and
  require an `ANSWER:` line — so three of the four models have never reasoned in
  this eval. R12 is not the control; the concurrent advisor arm is. Advisor
  rerun vs R12 is reported descriptively (the effect of allowing reasoning), with
  no prediction.
- **Held from R12:** 4 models, 9 scenarios, open-ended, 10 epochs, T = 1,
  `with_levels=true`, Fig. S2 baseline. Referendum and interval still deferred.
- **Cost:** 2 arms x 90 x 4 models = 720 generations.
- **Persona changes the speaker and nothing else.** Same household facts (4
  people, $100,000, basin). No name, demographics, or politics.
- **The manipulation bundles two things:** speaker (they -> I) and mood (what a
  household *should* do -> what I *would* do). Bundled on purpose to keep this
  light. If the level moves, unbundling them is the follow-up.
- **Note on referent.** The instrument's own wording is second person — "Increase
  in taxes to your household", "Water quality near your home", "Your local
  watershed" — while the advisor prompt speaks of "the user". The advisor arm
  therefore has a mixed referent for "you"; the persona arm is the one where the
  verbatim instrument reads consistently. Relevant if the level moves.

## Primary endpoint — level shift

Per model: **L = geometric mean over the 9 cells of (persona median / advisor
median).**

| Outcome | Rule |
|---|---|
| A. No change | 0.75 <= L <= 1.33 |
| B. Drop | L < 0.75 |
| C. Rise | L > 1.33 |

Why these bounds. Symmetric in log space (a factor of 4/3 either way).
Averaging nine cells means a single cell jumping a whole chip ($500 -> $1,000
for mini) moves L by at most ~8% (2^(1/9)), so one lumpy cell cannot trip the
band. Tighter than 1.5 because of Haiku: on R12's table the models sit above
the human means by roughly 1.4x (Haiku), 2.0x (Sonnet), 2.5x (GPT-4o), 3.8x
(mini) — geometric mean over the nine cells. Haiku moving all the way to the
human levels is L ~ 0.72, which a 0.67 band would have scored as no change.
(Those ratios are from R12's prompts; the advisor rerun may move them.)

- **Uncertainty:** bootstrap 95% interval on L (resample draws within cell,
  2,000 reps), reported beside the point estimate. The point estimate decides.
- **Headline:** an outcome is the headline if at least 3 of 4 models land in
  it; otherwise the result is *mixed* and reported per model.
- **Parse gate:** a model whose persona parse rate is below 80% is not scored on
  L. Its refusal rate is the result for that model.
- **Zeros:** a cell with a $0 median in either arm is dropped from L and
  reported. (R12 had none.)

## Interpretation, fixed in advance

- **A. No change (expected).** The advisor frame is not what produced R12's
  levels. The design choice stands; persona is closed for this instrument.
- **B. Drop.** Framing moves the level. For every model this is toward the
  human means, since all four start above them; closeness is reported per model
  as a secondary. Warrants deciding which frame to use — and that choice rests
  on coherence (below), not on which frame lands nearer the human numbers.
  Next step: unbundle speaker from mood.
- **C. Rise.** Framing moves the level away from the human means. Two readings,
  separated in advance by the parse and coherence checks:
  - *Prompt or construct problem* — persona parse rate falls, refusals rise, or
    coherence collapses in the persona arm.
  - *A real framing effect* — parse rate and coherence hold. Candidate
    explanation: an analogue of hypothetical bias (stated WTP above what people
    actually pay). To take to Catherine.
- **Across all three — distance decay decides which frame answers the question
  better.** If distance decay reverses in the persona arm for a model where it
  held under advisor, persona is answering the question worse for that model,
  however close its levels land to the human means. A level nearer the humans
  does not rescue a frame that fails a rational check. The mirror case — a
  reversal under advisor that persona removes — counts for persona.

## Secondary — coherence in each arm

1. **Distance decay — a validity check, not a preference.** Baseline and
   improvement are held identical across spatial units (Deviation 5), so the
   only difference between the local and non-local watershed is whether it
   contains the household's home. Local delivers everything non-local does, plus
   use value, so `WTP(local) >= WTP(nonlocal)` is the rational answer. A
   **reversal** (nonlocal median > local median) is a failure to answer the
   question. A **tie** is flat but defensible (a household with no use value)
   and is reported, not scored as a failure. The argument fixes the direction,
   not the ratio: a nonlocal/local ratio drifting toward 1 is not by itself
   worse. Checked per change type (3 per model, 12 per arm). R12: 12 / 12
   strictly decaying, no ties.
2. **Nested dominance.** `min2 >= min3`, per spatial unit (3 per model, 12 per
   arm; ties pass). R12: 2 violations in 12. *Increase* = persona has at least
   2 more violations than advisor. Reads differently by arm: under advisor a
   violation is an error (the normative argument); under persona it is scope
   insensitivity, which human respondents also show.
3. **Scope ordering and spatial scale.** Reported, not predicted.

## Prediction — FREEZE BEFORE RUNNING

Daniel's bets:

- **Level:** A (no change) in all four models.
- **Distance decay under persona:** no directional bet. Frozen instead as the
  interpretation rule above — a reversal under persona means persona answers
  the question worse, regardless of level.
- **Nested-dominance violations under persona vs advisor:** no bet; reported.
- **Advisor rerun vs R12:** not predicted.

Frozen 2026-09-14, in the commit that adds this section and the persona prompts
(`git log -- PLAN.md`). Any later change to this section or to
`system_persona.txt` / `open_ended_persona.txt` is a deviation and is logged as
one.

## Pre-run checks (R13)

- [x] Persona prompts reviewed and frozen with the prediction
- [x] `direct_wtp` takes a `frame` argument selecting both system and question
      prompt
- [x] Persona smoke test: 6/6 parsed on Haiku
      (`python scripts/run_smoke.py --frame persona`)
- [x] `pytest -q` clean
- [x] Prediction committed

## Attribution

Instrument, scale, and all human estimates: Vossler, Dolph, Finlay, Keiser,
Kling & Phaneuf (2023), PNAS 120(18) e2120251119. Design conversation with
Catherine Kling, September 2026.
