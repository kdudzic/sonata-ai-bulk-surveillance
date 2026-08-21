# Runs

Every execution of the pipeline, inputs and results. Directories are numbered in
rough chronological order.

**Naming:** `*-inputs.xlsx` is a prepared workbook (posts and model assignments,
no model answers yet). `*-results.xlsx` is the same workbook after the models
ran.

---

## `01-exploratory-100-pairs/`

The only archived output of `sonata-generate`. 100 pairs from
`anthropic/claude-sonnet-4.6`, seed 42.

- `generated_posts.json` — `{pair_id: {CASE_A, CASE_B}}`
- `metadata.json` — the hidden-variable draw behind each pair

**Dead end, kept for the record.** It used a prompt (`data/prompt.md`) that no
longer exists in the repository, and **none of its 100 pairs made it into the
benchmark** — verified by text comparison against `data/pairs.xlsx`. The 48
curated pairs were produced later, through the browser app.

Resume it with `sonata-generate --run-dir runs/01-exploratory-100-pairs`
(it would continue from pair 101).

## `02-pilot-en/` — the main study

96 posts × 5 models = 480 evaluations per format.

| File | Contents |
|---|---|
| `rationale-inputs.xlsx` | prepared, no answers |
| `rationale-results.xlsx` | **480 decisions — 342 KEEP_FOR_REVIEW / 138 DISCARD** |
| `structured-inputs.xlsx` | prepared, no answers |
| `structured-results.xlsx` | **480 decisions — 335 KEEP_FOR_REVIEW / 145 DISCARD** |

These two result files are the source of the headline numbers in
[../docs/pilot-results.md](../docs/pilot-results.md).

## `03-bias-en/` — identity-substitution stress test

10 pairs re-run with a single identity term inserted (e.g. "those people" →
"those Muslim people"), everything else held constant. 20 posts × 5 models = 100
evaluations per format.

| File | Contents |
|---|---|
| `rationale-inputs.xlsx` | prepared, no answers |
| `rationale-results.xlsx` | 100 decisions — 88 KEEP / 12 DISCARD |
| `structured-inputs.xlsx` | prepared, no answers |
| `structured-results.xlsx` | 100 decisions — 87 KEEP / 13 DISCARD |

14 of 200 answers changed decision when the identity term was added, 12 of them
toward retention.

Content warning: this set deliberately contains anti-Muslim, antisemitic, and
racist framings. Synthetic, constructed to measure the failure.

## `04-replication-fr/` — French replication

The 96 posts translated to French, prepared for both formats, 480 rows each.

**Both files are inputs only — no model answers.** No completed French result
workbook was found anywhere on disk. Either the replication was never run, or
its output lives somewhere outside this machine. Treat the French arm as
**prepared but unfinished** until that is resolved.

The EN→FR translation table is in the `French` sheet of
`05-results/all-runs-consolidated.xlsx`.

## `05-results/`

`all-runs-consolidated.xlsx` — **the most important single file here.** The
hand-assembled master workbook, and the only place the expert's scores survive.

| Sheet | Rows × cols | Contents |
|---|---|---|
| `Structured` | 499 × 39 | main study, structured format, **480 rows carrying human 0–12 scores** |
| `short` | 499 × 46 | main study, rationale format — **uses its own narrower column layout** |
| `Bias` | 20 × 26 | hand-built bias summary, no header row |
| `Bias_short` | 102 × 41 | bias run, rationale format, with human scores |
| `Bias_structured` | 102 × 40 | bias run, structured format |
| `French` | 97 × 4 | EN→FR translation table (`pair_id`, `case_side`, EN, FR) |

**Do not parse this file with the canonical column map.** The sheets were edited
by hand and their layouts diverge from each other. Read row 2 of whichever sheet
you are in. See [../docs/data-dictionary.md](../docs/data-dictionary.md).

## `99-staging/`

Working copies with no unique results. Kept only so their existence is not a
mystery later.

- `all-96-posts.xlsx` — all 96 posts staged in the `eval` sheet with no
  `target_model` assigned. Its `parameters` sheet is byte-identical in content
  to `data/pairs.xlsx`.
- `parameters-dominika-copy.xlsx` — Dominika's copy. Its `POST_EVAL` sheet holds
  a 19-post smoke test against `openai/gpt-5.4` from 2026-04-21, superseded by
  the runs above.

---

## Provenance: original filenames

These files were moved here during the 2026-08-21 cleanup. Mapping, in case an
old note or email refers to the previous name:

| Now | Was |
|---|---|
| `01-exploratory-100-pairs/` | `outputs/` |
| `02-pilot-en/rationale-inputs.xlsx` | `eval_simple_4models.xlsx` |
| `02-pilot-en/structured-inputs.xlsx` | `eval_structured_4models.xlsx` |
| `02-pilot-en/rationale-results.xlsx` | `../eval_filled_short.xlsx` |
| `02-pilot-en/structured-results.xlsx` | `../eval_filled_struct.xlsx` |
| `03-bias-en/rationale-inputs.xlsx` | `eval_simple_dbs.xlsx` |
| `03-bias-en/structured-inputs.xlsx` | `eval_structured_dbs.xlsx` |
| `03-bias-en/rationale-results.xlsx` | `../eval_filled_simple_dbs.xlsx` |
| `03-bias-en/structured-results.xlsx` | `../eval_filled_struct_dbs.xlsx` |
| `04-replication-fr/rationale-inputs.xlsx` | `eval_simple_french.xlsx` |
| `04-replication-fr/structured-inputs.xlsx` | `eval_structured_french.xlsx` |
| `05-results/all-runs-consolidated.xlsx` | `../eval_filled_struct_dbs_french.xlsx` |
| `99-staging/all-96-posts.xlsx` | `parameters_copy.xlsx` |
| `99-staging/parameters-dominika-copy.xlsx` | `../parameters_dom.xlsx` |
| `data/pairs.xlsx` | `parameters.xlsx` |

`..` means the parent working folder, `/home/ked/sync/work/sonata/`. Files
copied from there still exist at their original location; the copies here are
what the repository now tracks. The `dbs` in the old names meant the bias set,
and `simple` meant the rationale format.
