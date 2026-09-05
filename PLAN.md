# Predeclared plan — water quality valuation pilot

## Goal

Test whether a language model handed a real stated-preference instrument
produces willingness-to-pay figures that cohere with each other, and separately
how those figures compare to the human sample the instrument was built for.

Not a silicon-sampling study. The human estimates are a comparison, not a target
— see README. The design consequence is that the primary endpoints need no
human number at all.

## Predeclared pilot

- **Models:** Claude Sonnet 4.5, Claude Haiku 4.5, GPT-4o, GPT-4o mini
- **Scenarios:** 9 — {one-level improvement, minimum Level 2, minimum Level 3}
  × {local watershed, non-local watershed, study region}
- **Bids:** the published ladder, $20 / 50 / 75 / 100 / 150 / 200 / 250 / 350 /
  500 / 750
- **Formats:** referendum (human-matched), open-ended, p10/p50/p90 interval
- **Repeats:** 10 epochs
- **Temperature:** 1.0
- **Context depth:** `with_levels=true` for the pilot; `false` as the second arm
  if budget allows
- **Status:** exploratory pilot, not a powered model comparison

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
Referendum : 9 scenarios x 10 bids x 10 epochs   =  900 / model
Open-ended : 9 scenarios x 10 epochs             =   90 / model
Interval   : 9 scenarios x 10 epochs             =   90 / model
                                                   1,080 / model
4 models                                         = 4,320 generations
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
5. **Format invariance.** Referendum-recovered vs. open-ended vs. interval p50,
   within model and scenario.

### Secondary — against the human sample

6. Per-scenario level comparison against the nine published means. Report the
   ratio and whether the model's figure sits inside the published interval,
   noting that the published values are mixed-logit population parameters and
   the model's is a recommendation — unlike objects, deliberately compared.
7. Whether the three human patterns reproduce: scope ordering in every column,
   flatness from the watershed up, roughly 2:1 local to non-local.

### Reporting rules

- Report the Turnbull mean and the logit median together. Where they disagree,
  the disagreement is the finding.
- A model whose yes-share never falls below 50% at $750 is **censored**, not
  extrapolated. Report it as censored.
- Parse rate is an endpoint, not a diagnostic. A refusal-heavy model is a result.

## Prediction — FREEZE BEFORE RUNNING

> **TODO (Daniel):** write the prediction here and commit it before any
> generations run, per R10 practice. With nine benchmarks and six replications
> of the scope ordering available, this design is unusually easy to read
> retrospectively.
>
> At minimum, commit to a direction on:
> - whether the models scale WTP with policy area where the humans were flat
> - whether any model violates nested dominance
> - whether format invariance holds, and which format runs highest
> - whether recovered levels land above or below the human means

## Pre-run checks

- [ ] Refusal smoke test — ~20 prompts across the four models, confirm the
      advisor framing yields parseable output on all three formats
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

## Attribution

Instrument, scale, and all human estimates: Vossler, Dolph, Finlay, Keiser,
Kling & Phaneuf (2023), PNAS 120(18) e2120251119. Design conversation with
Catherine Kling, September 2026.
