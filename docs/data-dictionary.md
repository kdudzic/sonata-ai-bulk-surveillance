# Data dictionary

The spreadsheet is this project's database. This file documents its layout.
The machine-readable version is
[`src/sonata_surveillance/schema.py`](../src/sonata_surveillance/schema.py) —
keep the two in step.

## Conventions

- **Row 1** is a merged group banner (`MODEL DECISION - RATIONALE MODE` etc.).
  Cosmetic; only the first cell of each group carries text.
- **Row 2** is the real header.
- **Data starts at row 3.**
- Column indices below are 1-based, matching `openpyxl`.
- List-valued model outputs (`evidence_spans`, `factors_*`) are flattened into a
  single cell, newline-separated.

> **Read this before parsing an archived workbook.** The files under `runs/`
> were hand-edited in Excel during the study, and some sheets drift from the
> layout below — `runs/05-results/all-runs-consolidated.xlsx` is the clearest
> case, where the `short` sheet uses its own narrower column arrangement.
> **Always trust row 2 of the sheet in front of you.** This document is
> authoritative only for what the code *writes*.

---

## Sheet `parameters` — one row per pair

The generation recipe and the gold labels. 48 rows, `P001`–`P048`.

| Col | Field | Meaning |
|---|---|---|
| A | `pair_id` | `P001`–`P048` |
| B | `target_model` | model used to generate the pair |
| C | `generate_pair` | run flag for the browser app (`YES`/`NO`) |
| D | `target_lang` | output language (`EN`, `FR`) |
| E | `retention_profile` | `clear_discard` / `borderline` / `clear_keep` |
| F | `legal_relevance_focus` | legal salience of the scenario |
| G | `changed_variable` | **which of the eight variables is flipped** |
| H–M | `speech_act`, `speaker_perspective`, `target_specificity`, `imminence`, `agency_cue`, `exculpatory_signal` | the controlled variables; the flipped one holds `VARIES_BY_CASE` |
| N | `case_a_value` | value of the flipped variable in CASE_A |
| O | `case_b_value` | value of the flipped variable in CASE_B |
| P | `generated_case_a` | CASE_A post text |
| Q | `generated_case_b` | CASE_B post text |
| R | `review_assessment` | human check on pair quality (`OK`, …) |
| S | `gold_label_A` | expert label for CASE_A |
| T | `gold_label_B` | expert label for CASE_B |
| U | `decisive_factor` | which variable should drive the difference |
| V | `notes` | free text on construction intent |

Columns S–V are the ground truth. Nothing automated writes them.

---

## Sheet `eval` — one row per evaluated post

Each pair contributes two rows (`case_side` A and B). When a workbook fans a
post across five models, that post appears five times.

### Input columns

| Col | Idx | Field | Meaning |
|---|---|---|---|
| A | 1 | `pair_id` | links back to `parameters` |
| B | 2 | `case_side` | `A` or `B` |
| C | 3 | `target_model` | OpenRouter model id to query — **rows with this empty are skipped** |
| D | 4 | `evaluate_post` | run flag for the browser app; the Python code ignores it |
| E | 5 | `evaluated_post` | the post text |

`evaluate_post` uses the `Def` sheet's dropdown: `0 - No`,
`1 - Simple rationale`, `2 - Structured output`, …

### `RATIONALE` block — columns F–K

| Col | Idx | Field |
|---|---|---|
| F | 6 | `model_id` |
| G | 7 | `prompt_id` |
| H | 8 | `generated_on` |
| I | 9 | `decision` |
| J | 10 | `short_rationale` |
| K | 11 | `reviewer_notes` |

### `STRUCTURED` block — columns L–U

| Col | Idx | Field |
|---|---|---|
| L | 12 | `model_id` |
| M | 13 | `prompt_id` |
| N | 14 | `generated_on` |
| O | 15 | `decision` |
| P | 16 | `evidence_spans` |
| Q | 17 | `factors_for_decision` |
| R | 18 | `factors_against_decision` |
| S | 19 | `counterfactual_change` |
| T | 20 | `short_rationale` |
| U | 21 | `reviewer_notes` |

### `STRUCTURED + CoT` block — columns V–AF

Same as above plus `reasoning_trace` (column AE, index 31). **Never implemented
in the Python code** — present in the layout and in some browser-app results.

### `Human judicial review` block — columns AG–AM

| Col | Idx | Field |
|---|---|---|
| AG | 33 | `Specificity` |
| AH | 34 | `Contrastiveness` |
| AI | 35 | `Contestability` |
| AJ | 36 | `Plain language` |
| AK | 37 | `Evidential grounding` |
| AL | 38 | `Proportionality relevance` |
| AM | 39 | `Score` |

Each dimension is scored **0–2**; `Score` is their sum, **0–12**. Filled by the
legal expert, never by code.

> **Gotcha:** several of these header cells carry a **trailing space**
> (`"Specificity "`, `"Contrastiveness "`, `"Plain language "`,
> `"Evidential grounding "`, `"Proportionality relevance "`). Match with
> `.strip()`.

---

## Field values

`decision` is one of `DISCARD` / `KEEP_FOR_REVIEW`.

`prompt_id` is the **filename** of the prompt that produced the answer, e.g.
`prompt_decision_struct.md`. This is the only provenance link from a result back
to the exact wording used — which is why prompt filenames must not be renamed,
even though they now sit in `data/prompts/`.

`generated_on` is an ISO date, written at evaluation time.

---

## Supporting sheets

| Sheet | Purpose |
|---|---|
| `Przyklad_podstawienia` | worked example of one variable substitution (Polish: "substitution example"); documentation for human authors |
| `Def` | dropdown definitions backing the `evaluate_post` / `generate_pair` flags |

---

## How the evaluator uses this

`sonata-evaluate` treats a row as **pending** when `evaluated_post` (E) is
non-empty and the chosen mode's `model_id` cell is empty. It fills that mode's
whole block and moves on.

Consequences worth remembering:

- Rerunning after a crash fills only the gaps — safe and cheap.
- **To force a re-evaluation, clear that mode's column block first.** Otherwise
  nothing happens and the command reports there is nothing to do.
- The workbook is written **in place**. Copy it first if the original matters.
