"""Filesystem paths and run defaults.

Every path in the project resolves from here, so moving a directory means
editing one file.
"""

from __future__ import annotations

import os
from pathlib import Path

# ── Locations ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
PROMPTS_DIR = DATA_DIR / "prompts"
RUNS_DIR = REPO_ROOT / "runs"
DOCS_DIR = REPO_ROOT / "docs"
WEBAPP_DIR = REPO_ROOT / "webapp"

#: Master benchmark: 48 counterfactual pairs, generation parameters, gold labels.
PAIRS_XLSX = DATA_DIR / "pairs.xlsx"

#: The eight controlled variables that define a scenario.
HIDDEN_VARIABLES_PATH = DATA_DIR / "hidden_variables.json"

#: The legal decision framework the prompts are derived from.
RULEBOOK_PATH = DATA_DIR / "rulebook.md"

PROMPT_GENERATE_PATH = PROMPTS_DIR / "prompt_generate.md"
PROMPT_DECISION_SIMPLE_PATH = PROMPTS_DIR / "prompt_decision_simple.md"
PROMPT_DECISION_STRUCT_PATH = PROMPTS_DIR / "prompt_decision_struct.md"

#: Source template for the browser app.
WEBAPP_TEMPLATE_PATH = WEBAPP_DIR / "index.template.html"

#: Build output. Pinned to the repository root because GitHub Pages serves this
#: repository from ``main`` at path ``/`` -- moving it takes the site down.
WEBAPP_OUTPUT_PATH = REPO_ROOT / "index.html"

# ── Credentials ───────────────────────────────────────────────────────────────

#: Fallback key file, used when neither environment variable is set.
DEFAULT_API_KEY_PATH = Path("/home/ked/sync/tokens/sonata_openrouter.txt")


def read_api_key() -> str:
    """Return the OpenRouter API key.

    Resolution order: ``OPENROUTER_API_KEY``, then the file named by
    ``OPENROUTER_API_KEY_FILE``, then :data:`DEFAULT_API_KEY_PATH`.
    The key is deliberately never stored in the repository.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key.strip()

    key_path = Path(os.environ.get("OPENROUTER_API_KEY_FILE", DEFAULT_API_KEY_PATH))
    if not key_path.exists():
        raise FileNotFoundError(
            f"No OpenRouter API key. Set OPENROUTER_API_KEY, or point "
            f"OPENROUTER_API_KEY_FILE at a key file. Looked in: {key_path}"
        )
    return key_path.read_text(encoding="utf-8").strip()


# ── Run defaults ──────────────────────────────────────────────────────────────

#: Model used to generate the synthetic pairs (not one of the models under test).
DEFAULT_GENERATION_MODEL = "anthropic/claude-sonnet-4.6"

#: Fixed so that a rerun reproduces the same hidden-variable draws.
DEFAULT_RNG_SEED = 42

DEFAULT_PAIR_COUNT = 10

#: Retries per post when a model returns unparseable JSON.
DEFAULT_MAX_ATTEMPTS = 3
