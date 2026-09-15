# R13 — advisor vs household persona — 14 September 2026

Same nine cells, same four models, ten draws, temperature 1. Two arms under
the `ANSWER: $N` prompts: advisor (the control) vs a thin household persona
("you are a member of this 4-person, $100,000 household"). 720/720 parsed.
Logs: `logs/r13/`. Worksheet: `results/r13.csv`. Frozen plan is in `PLAN.md`.

R12 is **not** the control. R12 forbade reasoning ("reply with exactly `$N`").
R13 lets every model reason. The persona test is advisor-rerun vs persona.
Advisor-rerun vs R12 is the effect of allowing reasoning, reported with no
bet.

**Prediction:** A (no change) on all four — geometric mean of persona/advisor
cell medians inside `[0.75, 1.33]`. **Headline: mixed.** Anthropic did not
move. GPT-4o dropped clearly. Mini is scored a drop by 0.008.

| Model | L (persona / advisor) | 95% boot | Call | Resampled L in the called band |
|---|---|---|---|---|
| Haiku | 0.985 | 0.72–1.38 | A. No change | 92% |
| Sonnet | 1.195 | 0.95–1.38 | A. No change | 95% |
| GPT-4o | 0.672 | 0.62–0.81 | B. Drop | 81% |
| GPT-4o mini | 0.742 | 0.59–1.07 | B. Drop | 35% |

The frozen rule lets the point estimate decide, so mini stays B. It is the
weakest call in the table: 65% of resamples land in no change. Intervals are
seeded now (`BOOT_SEED = 13`) so they reproduce. The last column is from
`scripts/audit_r13.py`, added after the run and not predeclared.

## How far they moved from R12

Geometric mean over the nine cells of (this week's median / R12 median).
Same L construction as the persona test; no prediction was frozen.

| Model | Advisor / R12 | Persona / advisor | Persona / R12 | vs humans (R12 → advisor → persona) |
|---|---|---|---|---|
| Haiku | **2.79** | 0.99 | 2.75 | 1.4x → 3.8x → 3.8x |
| Sonnet | 0.80 | 1.20 | 0.96 | 2.0x → 1.6x → 2.0x |
| GPT-4o | **2.28** | **0.67** | 1.53 | 2.5x → 5.8x → 3.9x |
| Mini | 0.80 | **0.74** | 0.59 | 3.8x → 3.1x → 2.3x |

Allowing reasoning moved Haiku and GPT-4o more than the persona did. Haiku's
one-level local went 310 → 1000; min3 local 320 → 1650. GPT-4o roughly doubled
every cell (local min2 850 → 2000). Sonnet and mini eased down ~20% from R12,
then diverged: Sonnet's persona ticked back up, mini's persona medians settled
on $500 (7 of 9 cells, though only 32 of its 90 draws are $500).

Two checks that this is the prompt and not something else
(`scripts/audit_r13.py`):

- **Same models.** The API returned the same dated snapshot in R12 and R13 for
  all four (`claude-haiku-4-5-20251001`, `claude-sonnet-4-5-20250929`,
  `gpt-4o-2024-08-06`, `gpt-4o-mini-2024-07-18`).
- **The prompt really changed what they did.** In R12, Haiku, GPT-4o and mini
  wrote a median of 4–6 characters before the answer — a bare `$N`. In R13
  every model writes 1,000–2,000. Sonnet was already writing ~1,300 in R12,
  and it moved least (0.80): the closest thing here to a control.

So: R12's levels were not "the advisor frame." They came from the prompt
format. Two limits on that. It is the prompt change, not reasoning alone —
the rewrite also dropped "do not add caveats" and added the `ANSWER:` line.
And it is not uniform: mini started reasoning too and moved only 0.80. Once
every model is allowed to think, the household "you" vs "they" is a smaller
knob, and it trips the predeclared band for GPT-4o clearly and for mini by a
hair.

## Medians (local / nonlocal / region)

Human Table 2 in parentheses.

**Advisor (R13 control)**

| Policy | Haiku | Sonnet | GPT-4o | Mini | Human |
|---|---|---|---|---|---|
| One-level | 1000 / 1150 / 1200 | 700 / 188 / 550 | 1500 / 1000 / 1750 | 800 / 1000 / 1200 | 316 / 165 / 300 |
| Min 2 | 600 / 575 / 775 | 725 / 162 / 775 | 2000 / 1000 / 2000 | 1000 / 500 / 1000 | 492 / 225 / 463 |
| Min 3 | 1650 / 975 / 1050 | 525 / 142 / 575 | 1500 / 1000 / 1500 | 1000 / 450 / 400 | 217 / 95 / 207 |

**Persona**

| Policy | Haiku | Sonnet | GPT-4o | Mini | Human |
|---|---|---|---|---|---|
| One-level | 700 / 700 / 1200 | 900 / 162 / 725 | 1000 / 500 / 1500 | 750 / 1000 / 500 | 316 / 165 / 300 |
| Min 2 | 1050 / 1200 / 1000 | 1100 / 188 / 1000 | 1750 / 500 / 2000 | 500 / 500 / 500 | 492 / 225 / 463 |
| Min 3 | 1500 / 700 / 700 | 700 / 175 / 525 | 1000 / 500 / 1000 | 500 / 500 / 500 | 217 / 95 / 207 |

R12 table is below, for the side-by-side: Haiku 310/240/320, Sonnet 850/150/1000,
GPT-4o 700/450/750, mini 1000/600/1000 on one-level.

## Coherence, scored as frozen

Distance: a **reversal** (nonlocal > local) is a failure. A **tie** is
reported, not a failure. Nested dominance: `min2 >= min3`; ties pass.

| Model | Distance (R12 → advisor → persona) | Nest (violations / 3) |
|---|---|---|
| Haiku | 3/3 decay → **1 reversal** → 1 reversal + 1 tie | 0 → **3** → 1 |
| Sonnet | steep ~0.2, holds in all three | 1 → **0** → 0 |
| GPT-4o | ~0.6, holds in all three (persona a bit steeper) | 0 → 0 → 0 |
| Mini | 3/3 decay → **1 reversal** → 1 reversal + 2 ties | 1 → 0 → 0 |

**How firm these calls are.** Each is a comparison of two medians of ten, and
Haiku's draws within one cell run from $150 to $2,000. Resampling the draws
within each cell (`scripts/audit_r13.py`, 2,000 reps, not predeclared), the
chance each flagged violation holds:

| Call | P(violation) |
|---|---|
| Haiku advisor, distance reversal (one-level) | 0.48 |
| Haiku persona, distance reversal (min2) | 0.61 |
| Haiku advisor, nest violation: local / nonlocal / region | 0.98 / 0.80 / 0.63 |
| Haiku persona, nest violation (local) | 0.76 |
| Mini advisor / persona, distance reversal (one-level) | 0.73 / 0.47 |
| Sonnet and GPT-4o, any distance cell, either arm | ≤ 0.02 |

So the distance "reversals" for Haiku and mini are closer to flat than
reversed. The calls that survive resampling are Sonnet's and GPT-4o's distance
decay (solid everywhere) and Haiku's local nest violation under advisor.

The predeclared rule: if distance reverses under persona where it held under
advisor, persona is answering the question worse, even if the dollars move
toward the humans. Read per model — "for a model where it held," as frozen —
that case **does not fire**: Haiku and mini already reverse on the advisor
rerun. Read per change type, it would fire once, on Haiku min2 (600 vs 575
under advisor, 1050 vs 1200 under persona). Both of those sit inside the noise
(0.37 and 0.61 above), so the reading does not change the conclusion, but the
per-model reading is the one scored here. GPT-4o's drop keeps distance and the
nest, so it is a real framing effect under the plan — next step, if we chase
it, is unbundling speaker ("I") from mood ("would" vs "should"). Mini's
persona medians sit on $500 and distance goes flat; closer to humans is not a
reason to keep that frame.

Sonnet is the one model whose story is stable across R12 and both R13 arms:
steep local/nonlocal split, nest now holds, persona does not move the level
past the band.

Haiku is the warning about "allow reasoning." R12 Haiku looked like the
best-behaved small model (distance held, nest held, some cells on the human
means). The advisor rerun nearly triples its level and spreads its answers
across a factor of ten within a cell. Its nest fails at the local watershed
(0.98 under resampling); distance goes flat rather than cleanly reversing.
Persona does not fix that. The $240/$280 palette from R12 is gone
once it is allowed to write a paragraph.

## What this does to the design

- **Persona is not closed.** The bet was all four in A. Two of four were
  scored as drops. For GPT-4o that drop is clean enough to be a result. For
  mini it is a palette shift, and a borderline one (L 0.742, 35% of resamples
  in the drop band). Unbundle speaker vs mood only if we care about the GPT-4o
  drop; do not pile on a richer persona until that is separate.
- **Do not treat R12 as the advisor baseline.** The prompt format moved Haiku
  and GPT-4o by more than 2x. Any later arm (referendum, income off the page)
  should keep the `ANSWER:` line so it matches this week's control, not R12.
- **Referendum is still the check on whether these dollars are valuation.**
  Several cells sit at or above $750, and GPT-4o advisor is $1000–$2000. A
  ladder that tops out at $750 will not turn over for those models.
- **The next pre-registration needs a noise floor on coherence calls.** A
  median of ten cannot carry a per-cell call for a model whose draws span a
  factor of ten. Freeze a resampling threshold together with the rule, not
  after the run.

## Note for Catherine (R13)

Asked the same nine cells two ways: advise a household, or *be* a member of
that household. Same income ($100k), no extra biography. Prediction was that
the dollars would not move. Anthropic did not (Haiku L=0.99, Sonnet L=1.20).
Both GPTs dropped by the rule we froze (4o L=0.67, mini L=0.74). GPT-4o's is
the solid one; mini's is a hair under the cutoff, and only about a third of
resamples reproduce it.

The larger shift was not the "you." It was letting the model reason at all.
R12 said "reply with exactly `$N`." This week every model writes a paragraph
then an `ANSWER:` line. Same model versions both weeks, so it is the prompt.
Haiku's levels almost tripled, its answers spread out, and it now pays more
for the smaller improvement at the local watershed.
GPT-4o roughly doubled, then the persona brought it partway back. Sonnet is
the stable one: still ~0.2 nonlocal/local, nest now holds, persona does not
matter.

I would not pick a frame by which table is closer to the human means. Mini's
persona lands nearer because its medians settle on $500. Distance goes flat
for Haiku and mini once they reason — flat, not clearly reversed, at ten
draws a cell — so that is about the prompt, not a reason to become the
household. GPT-4o's drop is the one clean framing
effect; if we chase it, the next cut is "I" vs "should," not a thicker
persona.

---

# R12 — open-ended pilot — 6 September 2026

Nine scenarios from Vossler, Dolph, Finlay, Keiser, Kling & Phaneuf (2023),
asked as an open-ended maximum annual tax. Four models, ten draws each at
temperature 1. Referendum and interval are built; they run next week.

The figure in every cell is the **median of ten open-ended amounts**. Human
comparators are Table 2 Model 1 means (mixed logit, 2021 dollars / year for five
years). Those are unlike objects on purpose: a recommendation vs a population
parameter.

## Parser (read this first)

Sonnet 4.5 did not return `$100,000` as WTP. It wrote a ~1,300-character essay
that mentioned the household income line, then named a tax at the end. The first
pass took the first `$` in the transcript. `parse_vote` already preferred the
last line; `parse_dollars` did not. After last-`$` rescoring (no new API calls):

- 87/90 Sonnet rows were essays; 3 were a bare `$850`
- First `$`: $100,000 on all 87 essays
- Last `$`: a tax, usually in the $75–$1,200 range, with a sharp local vs
  nonlocal split

Haiku, GPT-4o, and GPT-4o mini already answered `$N` only, so they did not move.
Structured JSON is deferred to the next run.

## What Sonnet actually does: a range, then a point

This is the new piece, and the one to walk through with Catherine.

Sonnet almost never gives a single number. In **76 of 90** transcripts it names
two or more distinct taxes and uses range language (`between $500–$1,500`,
`range of $800–$1,200`, `around $75–100`). Then **every one of those 90 still
ends on a single `$N` line**. Typical shape:

> A reasonable household might value this between $500–$1,500 annually.
> $1,200

The last `$` is usually **inside** the band, often near the middle. Last-`$`
scoring is therefore a point estimate *after* a range, not a unique reservation
price, and not the same object as Haiku's single token.

The three exceptions are bare `$850` on min2 region — no essay, no band.

A keyword flag (`range_hint`) is *not* the same thing. It fires on hedging
words (`approximately`, `perhaps`) even when only one tax appears: 87/90. The
column that means "discussed a band" is **two or more distinct taxes** (76/90).
Worksheet: `results/sonnet_manual_score.csv`.

So there are three different Sonnet objects one could score:

1. The **last `$N`** (what the tables below use)
2. The **midpoint of the stated range**
3. The **low / high of the stated range** (interval-like)

We have not hand-coded (2) or (3) yet. If the human open-ended pilots did
anything like this, that is the comparison.

## Medians vs Table 2

Local watershed / nonlocal watershed / study region. Sonnet is last-`$` after
the range. Human in parentheses.

| Policy | Haiku | Sonnet (last `$`) | GPT-4o | GPT-4o mini | Human |
|---|---|---|---|---|---|
| One-level | 310 / 240 / 320 | 850 / 150 / 1000 | 700 / 450 / 750 | 1000 / 600 / 1000 | 316 / 165 / 300 |
| Min 2 | 820 / 280 / 450 | 850 / 175 / 950 | 850 / 500 / 1025 | 1500 / 500 / 1250 | 492 / 225 / 463 |
| Min 3 | 320 / 240 / 320 | 900 / 175 / 750 | 700 / 400 / 500 | 1500 / 500 / 1500 | 217 / 95 / 207 |

Nested dominance (`min2 >= min3`) holds for Haiku and GPT-4o in all three
spatial units. It **fails** for Sonnet at the local watershed (850 vs 900) and
for GPT-4o mini on the region (1250 vs 1500). Scope (`min2 > one-level > min3`)
fails in most columns; GPT-4o holds it on region and nonlocal only.

Distance decay is the pattern that shows up in every model: nonlocal is a
fraction of local. Humans were about 0.45–0.52. Haiku 0.34–0.77, GPT-4o
~0.6, **Sonnet ~0.2** (steeper than the humans), mini 0.33–0.60. Spatial scale
is flatter, as in the human table, except Haiku's min2 (local 820 vs region 450).

## Why the dollars are still in doubt

Open-ended amounts **can** be reservation prices. They can also be a small set
of round numbers whose mix shifts with the scenario. This design cannot separate
those.

Haiku used about 14 distinct values in 90 draws. `$240` and `$280` are 40 of
those 90. `$850` is the high chip, mostly on min2. Smoke at temperature 0 had
already locked local open-ended to `$850` and every interval p50 to `$280`.
min2 local in the pilot is bimodal (`$850` four times, `$240` twice), which is
an awkward shape for one reservation price plus jitter.

Sonnet is lumpy in a different way: it *talks* in bands, then commits to a
round number inside the band. That is closer to how a careful respondent might
think out loud — and also closer to "0.5–1.5% of the $100,000 we printed on
the prompt." Several essays say exactly that.

None of that proves the numbers are fake. It is why the original survey did not
use open-ended as the primary question. Next week's yes/no ladder is the
comparison that can move the doubt: if the vote curve ranks cells the same way,
the lumps were at least ordinal; if yes-share never falls, they were not doing
the work we assigned them.

---

## Note for Catherine

Same instrument as the 2023 paper, nine Table 2 cells, asked as an open-ended
maximum annual tax (ten draws per cell). Models advised; they were not treated
as a sample of households. Numbers below are medians. Human means in
parentheses: local / nonlocal / region.

| Policy | Haiku | Sonnet | GPT-4o | Mini | Human |
|---|---|---|---|---|---|
| One-level | 310 / 240 / 320 | 850 / 150 / 1000 | 700 / 450 / 750 | 1000 / 600 / 1000 | 316 / 165 / 300 |
| Min 2 | 820 / 280 / 450 | 850 / 175 / 950 | 850 / 500 / 1025 | 1500 / 500 / 1250 | 492 / 225 / 463 |
| Min 3 | 320 / 240 / 320 | 900 / 175 / 750 | 700 / 400 / 500 | 1500 / 500 / 1500 | 217 / 95 / 207 |

**Distance decay holds.** Nonlocal is a fraction of local in every model, same
direction as the humans (~0.45–0.52). GPT-4o is closest (~0.6). Sonnet is
steeper (~0.2). Haiku 0.34–0.77. Extending from the local watershed to the
full region is mostly flat, as in Table 2, with one exception (Haiku min2:
820 local vs 450 region).

**Scope and the nest mostly do not.** min2 > one-level > min3 fails in most
columns. The sharp test — min2 must be at least min3, because it is a strict
superset — fails for Sonnet locally (850 vs 900) and for mini on the region
(1250 vs 1500). Haiku and GPT-4o pass the nest, then fail the finer scope
ordering (often because one-level and min3 tie).

**The dollars are lumpy.** Haiku used ~14 distinct values in 90 draws; $240
and $280 are 40 of those 90; $850 is the high chip, mostly on min2. Mini
lives on $500 / $1000 / $1500. Sonnet is lumpy in a different way: 76/90
essays name a **range** ($500–$1,500, $800–$1,200, …) and then commit to a
point inside it. The table uses that last point. That can still be WTP; it
can also be a small set of round numbers whose mix shifts with local vs far.
Open-ended cannot tell those apart.

**Income is in the numbers for Sonnet, with direct evidence.** We printed a
4-person household at $100,000. Sonnet's essays say so: they talk about
0.5–1.5% of income, and local last-points sit near 1% ($850–$1,000).
Nonlocal last-points are ~0.15–0.2% of the same $100k. Haiku never mentions
income in the reply (it only emits `$N`) and still uses $850, so we do not
have the same smoking gun there.

A few cells sit on the human means (Haiku one-level local 310 vs 316; Haiku
min2 region 450 vs 463). I would not lean on those. The pattern that
survives is distance without scope.

Design notes, not the point of the conversation: advisor framing rather than
a respondent; baseline mix held fixed at Fig. S2; min3 change line is
reconstructed; next week is the referendum on a thinned bid ladder, which is
the check on whether these dollars were doing valuation work.


---

## LinkedIn draft

When you hand a language model a real stated-preference survey, the format of
the question does as much work as the scenario.

This week I ran the water-quality instrument from Vossler, Dolph, Finlay,
Keiser, Kling & Phaneuf (PNAS 2023) on four frontier models — the same
six-level scale, the same nine policy cells, asked as an open-ended maximum
annual tax. Ten draws per cell. Design conversation with Catherine Kling, who
coauthored the original study.

Two things showed up that are easy to misread.

First: the most capable model in the set (Claude Sonnet 4.5) looked like it
valued every policy at $100,000. It had copied the household income line into a
long essay and put the actual tax at the end. A smaller model (Haiku) followed
"reply with exactly `$N`" and looked well-behaved. That was a parser taking the
first dollar sign, not a sophistication reversal. After scoring the last `$`,
Sonnet shows a steep local-vs-nonlocal drop, in the same direction as the human
sample. It also does something the others don't: it names a **range**, then
commits to a point inside it. That is closer to thinking out loud than to a
single reservation price.

Second: even with a fair parser, the open-ended amounts sit on a small set of
round numbers. Haiku reused $240 / $280 / $850 across cells. That *might* be
its willingness to pay. It might also be how it talks about willingness to pay.
An open-ended question cannot tell those apart — which is a good deal of why
the original survey used a yes/no referendum at a posted price, not "name a
dollar."

Human means from the paper sit between $95 and $492. Some model cells land on
top of those; some sit above the survey's highest bid ($750). Next week I run
the same nine cells as the referendum. If the vote curve ranks policies the
same way, the lumps were doing real work. If it does not, the dollars were not.

Not a silicon sample of Midwestern households. The models were asked to advise.
The check is whether the numbers cohere — scope, distance, nested dominance —
and whether the elicitation is even asking what we think it is.
