# sonata-ai-bulk-surveillance

Small dataset-generation project for contrastive OpenRouter calls against a surveillance-retention benchmark prompt.

## Structure

- `src/`: Python source code
- `src/generate.py`: generation workflow
- `src/openrouter_api.py`: OpenRouter client wrapper
- `data/prompt.md`: prompt template used for generation
- `data/hidden_variables.json`: hidden-variable definitions used for contrastive sampling
- `data/`: benchmark reference material such as the rulebook
- `outputs/`: generated model outputs and metadata
- `generate.py`: repo-root wrapper so `python generate.py` still works

## Run

```bash
python generate.py
```

Or, after installing the package:

```bash
sonata-generate
```
