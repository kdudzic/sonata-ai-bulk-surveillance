# CLAUDE.md

Guidance for coding agents working in this repository. Read
[README.md](README.md) first — it carries the research context.

## What this is

Research code for a finished pilot study on LLM-assisted data-retention
decisions (NCN SONATA 19). Dormant: the next study is a different design, and
this repository is preserved primarily as the record of the pilot. Prefer
changes that make the record clearer over changes that modernise the code.

## Commands

```bash
uv sync
uv run sonata-generate --run-dir runs/my-run --pairs 10
uv run sonata-evaluate --workbook <xlsx> --mode rationale|structured
uv run sonata-build-webapp
```

There is no test suite.

## Hard constraints

- **`index.html` stays at the repository root.** GitHub Pages serves this repo
  from `main` at path `/`. It is generated from `webapp/index.template.html`;
  never hand-edit it, run `sonata-build-webapp`.
- **Prompt filenames are frozen.** `prompt_id` cells in every result workbook
  record the prompt by filename. Renaming a file in `data/prompts/` breaks the
  provenance link from results back to wording.
- **Never commit an API key.** Keys resolve from `OPENROUTER_API_KEY`,
  `OPENROUTER_API_KEY_FILE`, or a path outside the repository.
- **Archived workbooks under `runs/` are historical records.** Do not rewrite,
  reformat, or "fix" them. Read them, copy them, leave them alone.

## Conventions

- The spreadsheet is the database. Column layout lives in one place,
  `src/sonata_surveillance/schema.py`, mirrored in
  [docs/data-dictionary.md](docs/data-dictionary.md). Change both together.
- `sonata-evaluate` writes workbooks **in place** and skips rows already filled
  for the requested mode. That makes reruns cheap and forced redos require
  clearing the mode's columns first.
- Paths resolve from `src/sonata_surveillance/config.py`. Do not hardcode paths
  elsewhere.
- Docstrings here carry research rationale, not just mechanics. Keep that —
  the reader in six months needs the *why*.

## Where things are

| Question | File |
|---|---|
| What was the study and what did it find? | `README.md`, `docs/pilot-results.md` |
| How was it designed? | `docs/methodology.md` |
| What does this spreadsheet column mean? | `docs/data-dictionary.md` |
| Which file holds which results? | `runs/README.md` |
| What happens next? | `docs/part2-plan.md` (Polish) |
