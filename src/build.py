from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "index.template.html"
OUTPUT_PATH = REPO_ROOT / "index.html"
PROMPT_GENERATE_PATH = REPO_ROOT / "data" / "prompt_generate.md"
PROMPT_DECISION_SIMPLE_PATH = REPO_ROOT / "data" / "prompt_decision_simple.md"
PROMPT_DECISION_STRUCT_PATH = REPO_ROOT / "data" / "prompt_decision_struct.md"
HIDDEN_VARIABLES_PATH = REPO_ROOT / "data" / "hidden_variables.json"


def escape_for_js_template_literal(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    return text


def build() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    replacements = {
        "__PROMPT_GENERATE__": escape_for_js_template_literal(
            PROMPT_GENERATE_PATH.read_text(encoding="utf-8")
        ),
        "__PROMPT_DECISION_SIMPLE__": escape_for_js_template_literal(
            PROMPT_DECISION_SIMPLE_PATH.read_text(encoding="utf-8")
        ),
        "__PROMPT_DECISION_STRUCT__": escape_for_js_template_literal(
            PROMPT_DECISION_STRUCT_PATH.read_text(encoding="utf-8")
        ),
        "__SHARED_VARIABLE_KEYS__": json.dumps(
            list(json.loads(HIDDEN_VARIABLES_PATH.read_text(encoding="utf-8")).keys())
        ),
    }

    output = template
    for placeholder, value in replacements.items():
        output = output.replace(placeholder, value)

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Built {OUTPUT_PATH.name} from {TEMPLATE_PATH.name}")


if __name__ == "__main__":
    build()
