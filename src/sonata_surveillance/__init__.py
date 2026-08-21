"""Tooling for the SONATA 19 pilot on LLM-assisted data-retention decisions.

The pilot asks whether structured contrastive explanations make an LLM's
retention decision more legally reviewable than a free-text rationale.

Pipeline, in order:

1. ``generate``  -- build controlled counterfactual post pairs (CASE_A/CASE_B)
   from the hidden variables in ``data/hidden_variables.json``.
2. ``evaluate``  -- ask target models to decide DISCARD / KEEP_FOR_REVIEW on
   each post, in one of the decision modes defined in ``schema.DecisionMode``.
3. ``webapp``    -- inline the prompts into a single-file browser version of
   the same pipeline, published via GitHub Pages.

See ``README.md`` for orientation and ``docs/data-dictionary.md`` for the
spreadsheet layout, which is the project's real data model.
"""

__all__ = ["config", "schema", "openrouter", "generate", "evaluate", "webapp"]
