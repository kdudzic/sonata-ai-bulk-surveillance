# Pilot results

Findings as presented in `../legal-reasoning-llms.pptx`. Underlying data is in
`runs/` — see [runs/README.md](../runs/README.md) for which file holds what.

## Headline

**Structured contrastive explanations are legally useful — but not because they
are more accurate. They are useful because they create a better review record.**

## Decisions and agreement

| Metric | `STRUCTURED` | `RATIONALE` |
|---|---|---|
| Ratings | 480 | 480 |
| Agreement with human expert | 67.9% | 66.0% |
| `KEEP_FOR_REVIEW` decisions | 335 | 342 |
| Over-retention (kept, expert said discard) | 152 | 160 |
| Under-retention (discarded, expert said keep) | 2 | 3 |

**Over-retention is the finding.** The asymmetry is stark: 152–160 cases of
keeping what should have been discarded, against 2–3 of the reverse. Models
almost never miss what an expert would keep. They keep far too much else.

Legally this is the wrong error to make. It is the failure mode that
Art. 5(1)(c) data minimisation exists to prevent, and the one an accuracy metric
alone will not surface.

## Expert preference between formats

Of 480 paired comparisons: **107 better**, **325 equal**, **48 worse** for the
structured format. Mean advantage **+0.19 on the 0–12 rubric**.

Small. Real, but small — and driven by two models.

## Per-model legal quality (mean expert score, 0–12)

| Model | `RATIONALE` | `STRUCTURED` | Δ |
|---|---|---|---|
| Grok 4.20 | 8.54 | 9.03 | **+0.49** |
| GPT-5.5 | 7.96 | 8.53 | **+0.57** |
| DeepSeek v4 Pro | 7.95 | 8.05 | +0.10 |
| Mistral Large 2512 | 7.56 | 7.47 | −0.09 |
| Gemini 3.1 Pro | 8.16 | 8.03 | −0.12 |

The structured format is **not neutral and not automatic**. It helps models that
handle imposed structure well and does nothing — or slightly harms — the others.

## Effect on retention rate

Change in `KEEP_FOR_REVIEW` rate when moving to the structured format:

| Model | Change |
|---|---|
| Gemini 3.1 Pro | −6.25 pp |
| Grok 4.20 | −2.08 pp |
| GPT-5.5 | −1.04 pp |
| DeepSeek v4 Pro | 0.00 pp |
| Mistral Large 2512 | +2.08 pp |

Most retention-prone: **Mistral Large 2512** (KEEP in 84–86% of cases).
Least: **DeepSeek v4 Pro** (56%).

Different models carry different *default settings* toward retention. That is a
procurement question, not a tuning detail.

## Cross-format decision consistency

| Model | Consistency |
|---|---|
| Grok 4.20 | 97.92% |
| Mistral Large 2512 | 97.92% |
| GPT-5.5 | 94.79% |
| Gemini 3.1 Pro | 91.67% |
| DeepSeek v4 Pro | 89.58% |

Two readings, and the pilot cannot separate them: either the format does not
much change the decision, or the format improves the *record* of the decision
rather than the decision itself. The expert-score data leans toward the second.

Note the edge-case profile: DeepSeek is simultaneously least retention-prone and
least stable across formats — low retention is not the same as reliable
judgment.

## Where each format wins

**Structured helps** where proportionality matters: civic pressure, protest,
complaints, contacting media. The forced "factors against" field makes the model
state the mitigating side out loud.

**Free text sometimes helps** where communicative function matters: sarcasm,
irony, hearsay, reporting, gossip, describing someone else's statement. Free
prose recognised more readily that a post was not the author's own declaration.
Structure can flatten that distinction.

## Borderline cases that show the legal risk

- **P003_B** — sarcasm read as intent ("…to show them what we're 'capable of'")
- **P005_B** — a news report read as a threat
- **P031_B** — civic complaint correctly protected (printed complaints, mapped
  departments — preparation cues that are entirely lawful)
- **P046_B** — infrastructure detail over-weighted in hearsay

The pattern: **preparation and specificity cues get weighted as risk even when
the speech act is protected.**

## Bias stress test

Ten pairs, one identity term inserted, nothing else changed. **14 of 200
answers changed decision — 12 `DISCARD` → `KEEP`, 2 the reverse.**

When bias moved a decision, it mostly moved toward over-retention. This directly
violates the rulebook's own invariance safeguard.

## What the study can and cannot show

**Can:** explanation fidelity, counterfactual sensitivity, over-retention
patterns, legal contestability.

**Cannot:** operational performance, real-world context, legality of an actual
deployment.

## Design implications drawn from this

1. Default to non-retention.
2. Require textual evidence for retention.
3. Require factors both for *and against*.
4. Log the counterfactual threshold.
5. Audit over-retention specifically — accuracy hides it.
6. Test bias sensitivity by identity substitution.

## What this sets up for part 2

The pilot measured decisions on single posts at a balanced base rate. That is
not how selection works in the field, where relevant cases are one in a thousand
or rarer, and where the alternative to broad collection is deeper profiling of
individuals. Part 2 moves to that level — see
[part2-plan.md](part2-plan.md).
