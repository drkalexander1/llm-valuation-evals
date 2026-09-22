# Literature brief — R14 "willingness to correct"

Hand this file, unchanged, to whoever does the search (Claude, Gemini, or both)
so the results come back in the same shape and can be compared.

## The project, in one paragraph

We give frontier language models the stated-preference water-quality survey
from Vossler, Dolph, Finlay, Keiser, Kling & Phaneuf (2023, PNAS 120(18)
e2120251119) and test whether their valuations are internally coherent (scope,
nested dominance, distance decay), treating human estimates as a comparison,
not an answer key. The next step, "willingness to correct," shows the model a
household that plans to vote YES or NO on the tax at a posted price, across a
log-spaced ladder from $1 to $90,000 a year on a $100,000 income, and asks for
advice. An LLM judge labels whether the reply accepts the plan, questions it,
or recommends the opposite vote. The range of prices where the model lets both
votes stand is a revealed "tolerance band." We compare it with the model's
stated p10–p90 interval and its own referendum votes, and separate uncertainty
from deference by presenting the same plan as a neutral survey finding.

## Questions — one section per question in the report

1. **LLMs answering stated-preference / contingent-valuation / WTP
   questions.** Who has elicited willingness to pay from LLMs, for what goods,
   and did they test scope sensitivity, embedding, or other internal-validity
   checks — or only compare levels to human data ("silicon sampling")?
2. **Sycophancy when a user states a plan or value.** When does a model defer
   to a user's stated choice versus push back, especially in advice settings
   where there is no factual right answer? Anything on a *threshold* — how far
   a user's position must be from the model's before it corrects?
3. **Stated vs behavioural uncertainty in LLMs.** Work comparing a model's
   verbalized confidence or interval with how it actually behaves (acts,
   defers, hedges). Is "the range a model tolerates" used anywhere as an
   uncertainty measure?
4. **Protest zeros and implausible responses in stated-preference practice.**
   How are protest bids identified and handled, and are there accepted
   criteria for when a stated value is "implausible" versus a legitimate
   preference? (Human-subjects SP literature, not LLM.)
5. **LLM-as-judge validity** for classifying free-text advice into categories
   like accept / question / recommend-change: known biases (self-preference,
   position, verbosity) and recommended validation practice.
6. **Anchoring from user-attributed numbers.** LLM anchoring studies where the
   anchor comes from the user rather than a neutral source, and whether
   attribution changes the size of the pull.

## What to return

For each question:

- 3–8 works, most relevant first. For each: authors, year, title, venue, and a
  link or DOI; two lines on what it did; one line on **what it leaves open**
  for this design.
- Mark each citation **[verified]** only if you opened the source and
  confirmed it exists and says what you report. Otherwise mark it
  **[unverified]**. Invented or misattributed citations are the main failure
  mode of this task — an honest "unverified" is far more useful than a
  confident wrong one.
- If you searched and found nothing, say so explicitly, with the search terms
  you used. Absence is a result.

Then, at the end:

- **Closest five.** The five works nearest to R14 overall, and for each, the
  single biggest difference from our design.
- **Do not assess novelty** or say "no one has done this." Report the closest
  work and what it leaves open; the novelty judgement is ours, at writeup.

Keep the whole report skimmable — under about 2,500 words.
