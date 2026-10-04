# Income and basin — 27–28 September 2026

Same advisor referendum, same ten bids ($20 to $3,000), same ten draws, level
definitions on, six models. Two additions, both frozen in `PLAN.md` before any
of these generations. Household income is a run setting. The study-region
column is back: 425,000 square miles, home row kept.

What ran: all nine cells at $35,000 and at $200,000 (5,400 generations each),
plus the three basin cells at $75,000 (1,800). The six watershed cells at
$75,000 are the Saturday run and were not repeated. That middle column is a
different day, and `gpt-5.6-terra` and `claude-sonnet-5` are still undated
model names (see run notes). Parse rate on the
finished logs is 1.00. Logs: `logs/income/35000`, `logs/income/200000`,
`logs/income/75000`. The Saturday watersheds remain in `logs/referendum`.

**WTP is the first posted bid at which yes-share falls below 0.5.** A cell is
censored, written "above $3,000", when yes-share is still 0.5 or higher at
every bid. The dollar figures in
[`results/income-basin-wtp.pdf`](results/income-basin-wtp.pdf) are a different
summary, the logit median. That fit can land between two bids, or a few
hundred dollars past $3,000. The calls below use the crossing rule that was
frozen, not the logit.

Shareable tables, ahead of this writeup:
[`results/income-basin-wtp.pdf`](results/income-basin-wtp.pdf),
[`results/referendum-yes-share.pdf`](results/referendum-yes-share.pdf).

## Prediction

1. **Income.** Within a model and a cell, `WTP($35,000) < WTP($75,000) < WTP($200,000)` when both amounts are identified. A tie is a miss. If the higher income is censored and the lower one is identified, that is consistent with scaling. If both are censored, the comparison is unscored.
2. **Basin versus local.** At a given income and change, `WTP(study region) >= WTP(local watershed)`. A tie passes. Region priced below local fails. Non-local is not part of this bet.

## Income scales where it can be scored

No cell reverses. Wherever both incomes fall inside the ladder, the higher
income crosses at a higher bid. Wherever only the higher income is above
$3,000, the rule counts that as consistent with scaling.

The $200,000 column is above the ladder in most cells, so the top step is
often a floor. Sonnet 5's three non-local cells are the cleanest measured
slope: they rise from $35,000 through $75,000 and are still inside the ladder
at $200,000 ($2,000 for all three changes). Haiku barely moves onto the
ladder at all.

First bid where yes-share falls below 0.5. "Above $3,000" means it does not.
The $75,000 local and non-local cells are Saturday's.

**Sonnet 5**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | $500 | $1,500 | above $3,000 |
| Minimum Level 2, local | $750 | $2,000 | above $3,000 |
| Minimum Level 3, local | $500 | $1,000 | above $3,000 |
| One-level, non-local | $100 | $500 | $2,000 |
| Minimum Level 2, non-local | $250 | $750 | $2,000 |
| Minimum Level 3, non-local | $250 | $500 | $2,000 |
| One-level, basin | $500 | $1,500 | above $3,000 |
| Minimum Level 2, basin | $750 | $2,000 | above $3,000 |
| Minimum Level 3, basin | $500 | $1,500 | above $3,000 |

All nine cells rise from $35,000 to $75,000. The six local and basin cells
are then censored at $200,000. The three non-local cells are identified at
every income and keep rising.

**Sonnet 4.5**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | $1,500 | above $3,000 | above $3,000 |
| Minimum Level 2, local | $2,000 | above $3,000 | above $3,000 |
| Minimum Level 3, local | $1,500 | above $3,000 | above $3,000 |
| One-level, non-local | $100 | $1,500 | above $3,000 |
| Minimum Level 2, non-local | $250 | $750 | above $3,000 |
| Minimum Level 3, non-local | $100 | $750 | above $3,000 |
| One-level, basin | $1,500 | above $3,000 | above $3,000 |
| Minimum Level 2, basin | $1,500 | above $3,000 | above $3,000 |
| Minimum Level 3, basin | $1,000 | above $3,000 | above $3,000 |

$35,000 to $75,000 rises in the three non-local cells and is consistent in
the other six (identified, then censored). $75,000 to $200,000 is unscored
on the six cells that were already above the ladder.

**gpt-5.6-terra**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | $500 | $1,500 | above $3,000 |
| Minimum Level 2, local | $750 | above $3,000 | above $3,000 |
| Minimum Level 3, local | $500 | $1,500 | above $3,000 |
| One-level, non-local | $250 | $1,000 | above $3,000 |
| Minimum Level 2, non-local | $500 | $1,000 | above $3,000 |
| Minimum Level 3, non-local | $250 | $500 | $2,500 |
| One-level, basin | $500 | $2,500 | above $3,000 |
| Minimum Level 2, basin | $750 | above $3,000 | above $3,000 |
| Minimum Level 3, basin | $500 | $1,500 | above $3,000 |

Seven cells rise from $35,000 to $75,000. Minimum Level 2 local and basin go
from $750 to above $3,000. The only cell still identified at $200,000 is
minimum Level 3, non-local ($2,500).

**GPT-4o**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | $750 | above $3,000 | above $3,000 |
| Minimum Level 2, local | $1,500 | above $3,000 | above $3,000 |
| Minimum Level 3, local | $1,000 | $3,000 | above $3,000 |
| One-level, non-local | $250 | $1,000 | above $3,000 |
| Minimum Level 2, non-local | $250 | $1,000 | above $3,000 |
| Minimum Level 3, non-local | $250 | $1,000 | above $3,000 |
| One-level, basin | $750 | $3,000 | above $3,000 |
| Minimum Level 2, basin | $1,000 | above $3,000 | above $3,000 |
| Minimum Level 3, basin | $750 | $3,000 | above $3,000 |

Six cells rise from $35,000 to $75,000. The three local cells are identified
at $35,000 and censored, or at the top bid, by $75,000. Every cell is above
$3,000 at $200,000.

**GPT-4o mini**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | $3,000 | above $3,000 | above $3,000 |
| Minimum Level 2, local | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 3, local | $2,000 | above $3,000 | above $3,000 |
| One-level, non-local | $1,000 | above $3,000 | above $3,000 |
| Minimum Level 2, non-local | $750 | above $3,000 | above $3,000 |
| Minimum Level 3, non-local | $500 | above $3,000 | above $3,000 |
| One-level, basin | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 2, basin | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 3, basin | $2,500 | above $3,000 | above $3,000 |

Six cells are identified at $35,000 and censored at $75,000. Three cells are
censored at both, so those pairs are unscored. Nothing at $75,000 or
$200,000 falls inside the ladder.

**Haiku 4.5**

| Cell | $35,000 | $75,000 | $200,000 |
|---|---|---|---|
| One-level, local | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 2, local | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 3, local | above $3,000 | above $3,000 | above $3,000 |
| One-level, non-local | $2,500 | above $3,000 | above $3,000 |
| Minimum Level 2, non-local | $3,000 | above $3,000 | above $3,000 |
| Minimum Level 3, non-local | above $3,000 | above $3,000 | above $3,000 |
| One-level, basin | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 2, basin | above $3,000 | above $3,000 | above $3,000 |
| Minimum Level 3, basin | above $3,000 | above $3,000 | above $3,000 |

Two non-local cells at $35,000 are the only identified Haiku numbers. Both
are censored at the higher incomes. The other seven cells are unscored at
every step.

## Basin versus local

Humans in Table 2 were about flat from the local watershed to the full study
region (one-level $316 versus $300). The prediction here is that the region
is worth at least as much as the local watershed, because the home improvement
is in both and the region adds area.

Scored pairs, same change and income:

- **Sonnet 5.** Six identified pairs, all pass. Five are ties. Minimum Level 3 at $75,000 is higher for the basin ($1,500 versus $1,000). All three at $200,000 are unscored.
- **gpt-5.6-terra.** Five identified pairs, all pass. The one strict increase is one-level at $75,000 ($2,500 versus $1,500). Minimum Level 2 at $75,000 and all three at $200,000 are unscored.
- **Sonnet 4.5.** One-level at $35,000 ties at $1,500 and passes. Two failures, both at $35,000: minimum Level 2, basin $1,500 against local $2,000; minimum Level 3, basin $1,000 against local $1,500. The $75,000 and $200,000 pairs are unscored.
- **GPT-4o.** Three failures. At $35,000, minimum Level 2 is $1,000 against $1,500, and minimum Level 3 is $750 against $1,000. At $75,000, one-level crosses at $3,000 for the basin while local stays above $3,000. One-level at $35,000 ties at $750. Minimum Level 3 at $75,000 ties at $3,000. The rest are unscored.
- **GPT-4o mini.** Two passes at $35,000: one-level stays above $3,000 in the basin while local crosses at $3,000, and minimum Level 3 is $2,500 against $2,000. Minimum Level 2 and every higher-income pair are unscored.
- **Haiku 4.5.** All nine pairs unscored. Both columns stay above half through $3,000.

Where a model fails, it prices the larger region below the home watershed.
That is the scope failure this column was added to see. Sonnet 5 and terra,
the two models that turn over inside the ladder, do not make it.

## Note for Catherine

Income is printed as $35,000, $75,000, and $200,000, same household otherwise.
When a model has a crossing inside the ladder at the lower income, the higher
income either crosses later or stays yes through $3,000. It does not cross
sooner. At $200,000 most cells are still yes at the top bid, so the direction
shows and the size of the slope does not. Haiku barely gets onto the ladder.

Saturday was local versus non-local at the same 17,000 square miles. This run
puts the full Upper Mississippi, Ohio, and Tennessee basins back, at 425,000
square miles, with the home row kept. The prediction was that the region is
worth at least as much as the local watershed. Sonnet 5 and terra do that
wherever both sides are identified. Sonnet 4.5 prices two of the three
programs below local at $35,000. GPT-4o does the same on two programs at
$35,000, and on one-level at $75,000. The $75,000 local numbers in that
comparison are Saturday's, not a same-day rerun.

The PDF already in the repo reports a fitted median, which can sit a little
above $3,000. This note uses the pre-registered rule: the first posted price
where fewer than half the votes are yes.

## Still local

Keeping the curve and the vote file off the public repo was acceptable for
the earlier rounds. It will not be for a release of this design.

What is public now is the crossing (the first bid below half) and, for
Saturday only, the yes-share at each bid
([`results/referendum-yes-share.pdf`](results/referendum-yes-share.pdf)).
The income and basin cells have no public curve. The draw-level dataset is
only in `logs/` (gitignored), and `results/*.csv` is gitignored too, so the
R12 and R13 worksheets named above are local as well.

To publish later, two artifacts:

1. **The curve.** Yes-share at each of the ten bids, for every model, cell,
   and income, including Saturday's watersheds. One row per cell is enough
   for the curve. The crossing is then recoverable from it.
2. **The dataset.** One row per draw: model, income, scenario, bid, replicate,
   and the parsed vote. That is the file a reader needs to refit the logit or
   check a cell. The Inspect logs can stay gitignored; this table should not.

---

# Referendum arm — 19–20 September 2026

Six cells (three change types x local / non-local watershed; the study-region
column was dropped), ten bids from $20 to $3,000, ten draws per cell, advisor
frame. **The household income was set to $75,000, to match the average income
of the human sample in Vossler et al. (2023), rather than the $100,000 used in
R12 and R13.** All six models complete, 600 samples each. Parse rate 600/600
for five models and 599/600 for gpt-5.6-terra.

**Exploratory: no prediction was frozen before this run.** The extended-ladder
follow-up should be pre-registered.

## The headline: two models never turn over

Yes-share, pooled across the six cells.

| Model | $20 | $250 | $750 | $1,500 | $3,000 |
|---|---|---|---|---|---|
| Haiku 4.5 | 1.00 | 1.00 | 1.00 | 1.00 | **1.00** |
| GPT-4o mini | 1.00 | 1.00 | 1.00 | 1.00 | 0.87 |
| Sonnet 4.5 | 1.00 | 0.92 | 0.68 | 0.62 | 0.50 |
| GPT-4o | 1.00 | 0.97 | 0.85 | 0.53 | 0.32 |
| gpt-5.6-terra | 1.00 | 1.00 | 0.70 | 0.28 | 0.08 |
| **Sonnet 5** | 1.00 | 0.97 | 0.62 | 0.23 | **0.00** |

The split is by model generation, not by lab. The two current mid-tier models
(Sonnet 5 and terra) price the good; the older tier mostly does not.

Haiku votes yes in all 600 of its cells: every price, every scenario, up to
$3,000 a year for five years on a $75,000 income (4% of income). This is the
test `RESULTS.md` set for itself after R12 — "if yes-share never falls, they
were not doing the work we assigned them" — and Haiku fails it outright. Mini
nearly so.

## Distance carries the whole response

Average yes-share by spatial unit:

| Model | Local watershed | Non-local |
|---|---|---|
| Haiku 4.5 | 1.00 | 1.00 |
| GPT-4o mini | 1.00 | 0.94 |
| Sonnet 4.5 | 1.00 | 0.48 |
| GPT-4o | 0.95 | 0.47 |
| gpt-5.6-terra | 0.72 | 0.44 |
| Sonnet 5 | 0.62 | 0.36 |

Haiku, GPT-4o mini, and Sonnet 4.5 say yes at every local price. GPT-4o's
local cells stay above half until the top of the ladder; minimum Level 3
crosses at $3,000. Sonnet 5's local crossings are in the next section, and
terra's are in the paragraph after it. For the older models, the price
sensitivity in the pooled curve is the non-local cells. Same direction as
R13's open-ended distance decay, now in vote space.

## Sonnet 5 passes all three coherence checks

It is the only model whose every cell turns over inside the ladder. Bid at
which yes-share first falls below 0.5:

| Change | Local | Non-local |
|---|---|---|
| Minimum Level 2 | $2,000 | $750 |
| One-level improvement | $1,500 | $500 |
| Minimum Level 3 | $1,000 | $500 |

- **Scope ordering** (min2 > one-level > min3) holds in the local column and
  holds weakly in the non-local column. In R13's open-ended arm this ordering
  failed in most columns for every model.
- **Nested dominance** (min2 at least min3) holds in both columns.
- **Distance decay** holds for all three change types: local crosses at a
  higher price than non-local every time.

terra shows the same pattern more roughly (min2 local never crosses; the rest
cross between $500 and $1,500). Sonnet 5's crossings are still about three to
five times the human means in Table 2, but they are the closest of any model
so far, and the first to reproduce the human *ordering* rather than only the
distance effect.

## A coherence test the open-ended arm cannot run

A vote curve must weakly decrease in price. Counting adjacent-bid increases
within a cell:

| Model | Increases | Largest |
|---|---|---|
| Haiku 4.5 | 0 | — |
| Sonnet 4.5 | 4 | min2 non-local, $750 -> $1,000: 0.30 -> 0.60 |
| GPT-4o | 2 | one-level local, $2,000 -> $2,500: 0.80 -> 1.00 |
| GPT-4o mini | 2 | min3 non-local, $1,000 -> $1,500: 0.80 -> 1.00 |
| gpt-5.6-terra | 2 | min2 local, $1,500 -> $2,000: 0.90 -> 1.00 |
| Sonnet 5 | 1 | min2 local, $2,000 -> $2,500: 0.10 -> 0.20 |

With ten draws per cell and bid the standard error is about 0.15, so the
0.10–0.20 increases are noise. Sonnet 4.5's 0.30 jump is about two standard
errors and appears in more than one cell; it is the one worth a closer look.
Haiku's zero violations are not a pass — a flat line at 1.00 cannot violate
monotonicity.

## Comparability with R12 and R13

The $75,000 household matches the average income of the survey's human sample,
so this arm is *better* aligned with Table 2 than R12 and R13 were. The cost is
that it cannot be compared numerically with those earlier rounds.

The direction still carries across rounds, on one assumption: water quality is
a normal good, so a household with *less* income should not be willing to pay
*more*. Under that assumption the central finding holds a fortiori — models
voting yes at $3,000 on $75,000 would also do so at $100,000. Note that R12
Sonnet reasoned explicitly in shares of income (~1%), which under this change
would scale its figures down rather than leave them flat.

**Housekeeping, since done:** income is a task argument rather than an edit to
`instrument.yaml`, so R12 and R13 still reproduce from a clean checkout and
each income is its own condition. The sample-income figure is SI Table S6.

## Two run notes

- **Temperature is split by model generation.** Haiku, Sonnet 4.5, GPT-4o and
  mini ran at an explicit T=1.0. Sonnet 5 and gpt-5.6-terra reject the
  parameter and ran at provider default.
- **Both current models are undated.** Sonnet 5 returned `claude-sonnet-5`
  and terra returned `gpt-5.6-terra`, not dated snapshots like
  `claude-sonnet-4-5-20250929`. Neither provider offers a dated version: the
  model lists checked on 28 September show only these names. Runs are dated
  19–20 and 27–28 September. If either name is later pointed at a different
  model, these runs are not reproducible from the name alone.

## Next

Haiku, mini, and Sonnet 4.5 still have no local crossing, so their local
willingness to pay is above $3,000. Sonnet 5 and terra do cross locally. The
follow-up that ran is the income and basin section above. A longer ladder for
the cells that stay yes through $3,000 is still open, and still wants a
prediction frozen first.

---

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
