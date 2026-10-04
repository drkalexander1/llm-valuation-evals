> Working memo to coauthor Catherine Kling before the referendum design was
> fixed (17 September 2026). Kept for the record; the design as run is in
> [`PLAN.md`](../../PLAN.md).

# Briefing: do language models have a valuation of water quality?

**To:** Catherine Kling  
**From:** Daniel Alexander  
**Date:** 17 September 2026  
**For:** Saturday Zoom — design discussion, not a results seminar

Vossler, Dolph, Finlay, Keiser, Kling & Phaneuf (*PNAS* 2023) instrument, administered to language models.

## Executive summary

Do language models have a consistent valuation of water-quality improvements — that are conforms to with econ theory (monotonic in the size of the program, decaying with distance, responsive to how much quality changes) — or only dollars that depend on how we asked? Open-ended runs already map where each model sits (~$150–$2,000), so the next data should be the paper’s yes/no referendum on the same nine cells. That run can be a factorial; each extra factor is a full copy of the grid. **One condition** (four models, nine cells, five bids, ten draws) is about **1,800 generations / $7–12**. A 3-income × 2-ladder cross is six conditions, **~$45–70**. Saturday is to pick which factors are worth that, and to lock the change-line wording before any of it is generated.

## What we already know about where they sit

Open-ended is not WTP. It tells us where a posted-price ladder has to reach, and that the *ask* already moves the dollars (a bare `$N` vs a short rationale shifted some models 2–3×). Distance often goes the right way; response to *how much* quality changes often does not.

Week-2 advisor ++++medians, local / non-local / region (human Table 2: one-level 316 / 165 / 300, min-2 492 / 225 / 463, min-3 217 / 95 / 207):


|        | One-level          | Min 2              | Min 3              |
| ------ | ------------------ | ------------------ | ------------------ |
| Sonnet | 700 / 188 / 550    | 725 / 162 / 775    | 525 / 142 / 575    |
| Haiku  | 1000 / 1150 / 1200 | 600 / 575 / 775    | 1650 / 975 / 1050  |
| GPT-4o | 1500 / 1000 / 1750 | 2000 / 1000 / 2000 | 1500 / 1000 / 1500 |
| Mini   | 800 / 1000 / 1200  | 1000 / 500 / 1000  | 1000 / 450 / 400   |


Sonnet fits the human ladder (top $750). GPT-4o does not. That is the case for a second, higher ladder.

## Unit of cost

Prices below use week-2 token bills (models *did* write a paragraph) at current list rates: Sonnet $3/$15 per MTok in/out, Haiku $1/$5, GPT-4o $2.50/$10, mini $0.15/$0.60. Referendum with a short rationale should look similar; if answers run longer, use the high end of the range. Retries and a bit of waste are why the range is not a point.


|                                  | Generations | Observed $ | Budget     |
| -------------------------------- | ----------- | ---------- | ---------- |
| Week 2 (both frames, open-ended) | 720         | ~$3        | —          |
| **One referendum condition**     | **1,800**   | **~$7**    | **$10–12** |
| 1,000 extra generations          | 1,000       | ~$4        | ~$6        |


Almost all of the money is Sonnet (~55%) then GPT-4o (~25%). Mini is ~2%. Cutting mini barely saves; cutting Sonnet halves the bill and drops the model that behaved most like a valuation.

**Generations in one condition** = 9 cells × (bids) × (epochs) × (models). Default 9 × 5 × 10 × 4 = 1,800. Adding a factor *level* copies that whole block.

## Potential factors (Saturday menu)

Hold the grid unless we say otherwise: three programs × three spatial units, advisor, Figure S2 baseline, `ANSWER:` then Yes/No, temperature 1.


| Factor                          | Candidate levels                                                          | Pro                                                                                                                                 | Con                                                                                                                                                                      | Cost vs one condition                             |
| ------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| **Bid ladder**                  | Human-thinned $20/100/250/500/750 vs model-informed covering ~$100–$2,000 | Human ladder is the paper. Second ladder is the only way GPT-4o can say no. Directly tests “dollars from the ask vs from the good.” | Two supports are not the same object; pooling them is wrong. Extra rungs without thinning also work and cost per rung (below).                                           | **×2 → $15–25**                                   |
| **Income**                      | Omit / $40k / $100k / $200k                                               | Sonnet already talks in % of $100k. If WTP scales with income, that is a valuation. If not, the printed number was a prop.          | Three levels is a lot; omit vs $100k vs $200k may be enough. Confounded with “more text on the page.”                                                                    | **each extra level +$10–12**; 3 levels **$30–35** |
| **Ladder × income (the cross)** | e.g. 2 ladders × 3 incomes = 6                                            | Tells you whether income effects are an artifact of hitting the $750 ceiling.                                                       | Six is the first design that is real money. Do not need the full cross on day one: $100k × both ladders, *or* human ladder × three incomes, still identifies one factor. | **6 × $10–12 = $45–70**                           |
| **Speaker**                     | Advisor vs “you are this household”                                       | We have one clean open-ended effect (GPT-4o dropped). If it survives yes/no, framing is part of the valuation object.               | Doubles everything. Anthropic did not move last time. A thicker persona is a different (and worse) experiment.                                                           | **×2**                                            |
| **Rungs on a ladder**           | 5 (current) vs 10 (full Table 1) vs 5 stretched                           | Full Table 1 is what humans were assigned (one bid each). Extra rungs above $750 can replace a second “ladder” factor.              | Each added rung is +360 gens (~$1.50–2.50) per other-factor combination. Ten rungs = **×2 vs five**.                                                                     | +1 rung **+$2**; 10 vs 5 **×2**                   |
| **Draws (epochs)**              | 10 (current) vs 5                                                         | Ten is already noisy for per-cell calls. Five is how we trim if the cross gets large.                                               | Halving n makes nest/distance calls even softer.                                                                                                                         | **×0.5** if 5                                     |
| **Which models**                | Keep 4 / drop mini / drop Haiku / Sonnet+4o only                          | Mini is cheap and lumpy — a useful negative control. Sonnet is the one that looks like a valuation.                                 | Four models is a “model comparison” we are not powered for. Two (Sonnet + 4o) answers the valuation question at **~$6–8 per condition** instead of $10–12.               | Drop mini **~−$0.20**; drop Sonnet **~−$6**       |
| **Context depth**               | Level definitions on vs off                                               | Humans had ~30 minutes with graphics. Neither setting matches; running both is the honest version of “did they see the scale.”      | Full extra factor. Weak relative to ladder/income.                                                                                                                       | **×2**                                            |
| **Interval (p10/p50/p90)**      | On vs skip                                                                | Cheap (90/model, not 450). Format invariance was in the original plan. Smoke glued p50 at $280.                                     | A third elicitation before yes/no is settled.                                                                                                                            | **+$1–2 per other-factor combination**            |
| **Add L3→L2 cell**              | 9 cells vs 10                                                             | Table 1 lists it; Table 2 has no WTP. A fourth program.                                                                             | +11% gens. No human benchmark.                                                                                                                                           | **×1.11**                                         |
| **Drop the region column**      | 9 cells vs 6                                                              | Humans were flat local→region. Saves 1/3.                                                                                           | Loses the spatial-scale check.                                                                                                                                           | **×0.67**                                         |
| **Baseline**                    | Fixed Figure S2 vs watershed-specific                                     | Fixed isolates distance vs area. Specific is what respondents saw.                                                                  | Not a cheap 2-level factor unless we run both; randomizing inside one run is a different estimator.                                                                      | Treat as **×2** if both                           |


## Packages we could actually run


| Package                 | What it is                                 | Gens         | Budget      |
| ----------------------- | ------------------------------------------ | ------------ | ----------- |
| A. Paper replica        | $100k, human ladder, 4 models, 10 draws    | 1,800        | **$10–12**  |
| B. Two supports         | A + model-informed ladder                  | 3,600        | **$20–25**  |
| C. Income at one ladder | A, but $40k / $100k / $200k                | 5,400        | **$30–35**  |
| D. The 2×3 cross        | Two ladders × three incomes                | 10,800       | **$45–70**  |
| E. Cross + speaker      | D × advisor/persona                        | 21,600       | **$90–140** |
| Trim of D               | 5 draws, or drop region, or Sonnet+4o only | ~3,600–5,400 | **~$20–40** |


A is the minimum that is still the paper’s elicitation. B is the minimum that can test GPT-4o. D is the factorial if we want income and support to be separable. E is probably too much for this week.

## Decide on the call

1. **Change lines** (not a cost item). One-level from a voting screen; min-2 generalized from Figure S3; min-3 reconstructed. If min-3 is wrong, the nest test cannot speak to whether a valuation exists. Table 1’s Level-3-to-Level-2: in or out?
2. **Which package** (A–E, or a hybrid). Especially: is a second ladder worth $10, and is the income × ladder cross worth $50?
3. **Levels inside the factors we keep.** Top of the model-informed ladder? Three incomes or omit vs $100k vs $200k? Five rungs or ten?
4. **What is frozen.** Default: advisor, `ANSWER: Yes/No`, Figure S2, temperature 1, all four models, ten draws — unless we trim to pay for D.

If the vote curve ranks programs like a valuation even on a ladder that covers where they sat, the open-ended numbers were at least ordinal. If yes-share never falls, there was no valuation to recover.

Repo: [github.com/drkalexander1/llm-valuation-evals](https://github.com/drkalexander1/llm-valuation-evals).

---

## Call decisions — 19 September 2026 (check together)

One referendum condition. Not a factorial. Budget **~$10–12** if we add a fifth Sonnet-class model; **~$7–8** if we keep the current four.


| Item                   | Decision                                                           | Confirm                                                           |
| ---------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Elicitation            | Yes/no referendum (not more open-ended)                            | Yes                                                               |
| Income                 | One level                                                          | 75,000                                                            |
| Income × ladder cross  | No                                                                 | Yes                                                               |
| Speaker                | One type                                                           | Advisor                                                           |
| Bid rungs              | 10                                                                 | Stretching over LLM levels but with some of the human levels too. |
| Draws                  | 10                                                                 | 10                                                                |
| Spatial units          | Drop study region; keep local vs non-local watershed (**6 cells**) | Yes                                                               |
| Programs               | Three (one-level, min-2, min-3)                                    | Yes                                                               |
| Models                 | Current set **plus** one more Sonnet-class / GPT comparison        | Which model? Keep Haiku and mini?                                 |
| Baseline               | Figure S2 frozen (not discussed as a change)                       | Yes                                                               |
| Context depth          | Level definitions on (not discussed as a change)                   | Level definitions as we previously did in the 2 previous rounds.  |
| Interval (p10/p50/p90) | Off (not discussed)                                                | Off                                                               |
| Change-line wording    | —                                                                  | **Ok as written**                                                 |


**Grid this implies:** 3 programs × 2 places × **10** bids × 10 draws = **600 generations per model**. Five models = 3,000.

**Watch-out we already flagged:** GPT-4o’s open-ended medians sit at $1,000–$2,000, so a $750 top rung may be all yes for that model (a bound, not a curve). Accepted unless we add rungs after all.