# Open-ended pilot — 6 September 2026

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
