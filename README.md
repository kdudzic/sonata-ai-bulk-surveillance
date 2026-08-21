# SONATA 19 — Legal reasoning, explanation format, and data retention

Research code and data for the pilot study *Testing Legal Reasoning in Large
Language Models: Minimal Intrusion, Data Retention, and Justification in AI
Systems* (NCN SONATA 19).

⚠️ A note to humans: most of the contents of this repository are **intensely** co-authored by a Claude model and might not be easily understandable. I don't really have a reason to sort them out manually anymore. You can contact me directly for details. ⚠️ 

---

## What the study asks

If an LLM is used to triage public social-media posts for data retention, the
decision itself is not the only thing that matters legally. GDPR Arts. 13–15 and
Art. 22 require *meaningful information* about the logic of an automated
decision, enough for a person to contest it; Art. 5(1)(c) and 5(1)(e) require
that retention stay minimal and time-limited. A correct label with the wrong
reason is not a safe decision.

So the pilot compares two **explanation formats** for the same decision, on the
same posts, across the same models:

| Format | What the model returns |
|---|---|
| `RATIONALE` | decision + a short free-text justification |
| `STRUCTURED` | decision + evidence spans, factors for, factors against, and the minimal counterfactual change |

Every post is one half of a **counterfactual pair**. A pair holds eight
controlled scenario variables fixed and flips exactly one — so any difference in
how a model treats CASE_A and CASE_B is attributable to that single flip.

The default decision is `DISCARD`. `KEEP_FOR_REVIEW` has to be earned by a
textual basis in the post.

## What the pilot found

Structured explanations helped, but modestly and unevenly — **the headline
result is over-retention**. Models almost never discarded a case the expert
marked KEEP, but kept many the expert marked DISCARD. Full numbers and the
qualitative read in **[docs/pilot-results.md](docs/pilot-results.md)**.

## Status (as of 2026-08-21)

Pilot is **complete**; results are archived in `runs/` and written up in the
deck at `../legal-reasoning-llms.pptx`. The code is dormant — a second study is
planned on a different design (population-scale selection pipelines, ~15 000
posts, a spectrum of selectors from keyword lists to LLMs). That plan lives in
**[docs/part2-plan.md](docs/part2-plan.md)** and is written in Polish.

Part 2 is not expected to reuse this code much. This repository is preserved as
the record of the pilot.

---

## Layout

```
data/                     inputs that define the study
  pairs.xlsx              MASTER: 48 counterfactual pairs, generation params, gold labels
  rulebook.md             the legal decision framework the prompts derive from
  hidden_variables.json   the eight controlled scenario variables
  prompts/                exact prompt wordings (filenames are provenance — do not rename)

runs/                     every execution, inputs and results — see runs/README.md
docs/                     methodology, results, data dictionary, part 2 plan
src/sonata_surveillance/  the Python pipeline
webapp/                   source template for the browser version
index.html                BUILT artifact — must stay at repo root (GitHub Pages)
```

## Three things that are easy to forget

**1. The spreadsheet is the database.** There is no other store. One row per
evaluated post, output columns grouped side by side by decision mode, so one
post can carry results from several modes at once. The evaluator reads and
writes the workbook *in place*. Column layout is documented in
[docs/data-dictionary.md](docs/data-dictionary.md) and declared in
`src/sonata_surveillance/schema.py`.

**2. There are two implementations of the same pipeline.** The Python package
here, and a self-contained browser app (`webapp/index.template.html`, published
at <https://kdudzic.github.io/sonata-ai-bulk-surveillance/>). The browser app is
what actually produced the pilot results. They differ: Python calls the OpenAI
*Responses* API and leaves sampling at provider defaults; the browser app calls
`/chat/completions` and pins temperature (0.7 generation, 0.0 evaluation).
Results from the two paths are not strictly comparable.

**3. `index.html` is generated and root-pinned.** It is built from
`webapp/index.template.html`. GitHub Pages serves this repo from `main` at path
`/`, so moving it takes the site down. Rebuild after editing any prompt.

## Running it

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Provide an OpenRouter key by either route:

```bash
export OPENROUTER_API_KEY="sk-or-..."
# or point at a key file:
export OPENROUTER_API_KEY_FILE=/path/to/key.txt
```

Without either, the code falls back to `/home/ked/sync/tokens/sonata_openrouter.txt`.
No key is stored in this repository.

```bash
# Generate counterfactual pairs into a run directory (resumable).
uv run sonata-generate --run-dir runs/my-run --pairs 10

# Evaluate: fills the mode's column block, skipping rows already done.
# Writes the workbook in place — copy it first if the original matters.
uv run sonata-evaluate --workbook runs/02-pilot-en/rationale-inputs.xlsx --mode rationale
uv run sonata-evaluate --workbook runs/02-pilot-en/structured-inputs.xlsx --mode structured

# Rebuild the browser app after changing a prompt.
uv run sonata-build-webapp
```

Each command takes `--help`.

## Open threads

- **The `STRUCTURED + CoT` mode is half-finished.** The workbooks reserve a
  column block for it (from column V, with a `reasoning_trace` field) and some
  archived results contain it, but the Python code never implemented it — it was
  run through the browser app. See `schema.COL_COT_BLOCK_START`.
- **The archived result workbooks are not schema-clean.** They were hand-edited
  in Excel during the study and some sheets drift from the canonical column map.
  Trust row 2 of the sheet in front of you. Details in
  [runs/README.md](runs/README.md).
- **The 48 curated pairs have no generation log.** `data/pairs.xlsx` records the
  parameters behind each pair, but the pairs themselves came from the browser
  app, so there is no `metadata.json` for them. The one archived
  `sonata-generate` run (`runs/01-exploratory-100-pairs`) is a separate, earlier
  100-pair batch that used a prompt no longer in the repository, and none of its
  posts made it into the benchmark.

## Ethics note

Every post in this repository is **synthetic**. The bias stress-test set
(`runs/03-bias-en/`) deliberately contains posts with anti-Muslim, antisemitic,
and racist framings — constructed to test whether inserting an identity term
flips a model's retention decision. It did, and mostly toward over-retention.
The material exists to measure that failure, not to depict anyone real.
