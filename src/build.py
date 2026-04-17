from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "index.template.html"
OUTPUT_PATH = REPO_ROOT / "index.html"
PROMPT_PATH = REPO_ROOT / "data" / "prompt.md"
HIDDEN_VARIABLES_PATH = REPO_ROOT / "data" / "hidden_variables.json"


def escape_for_js_template_literal(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    return text


def build() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    escaped_prompt = escape_for_js_template_literal(prompt)

    variables = json.loads(HIDDEN_VARIABLES_PATH.read_text(encoding="utf-8"))
    keys_js = json.dumps(list(variables.keys()))

    output = template.replace("__PROMPT_TEMPLATE__", escaped_prompt)
    output = output.replace("__SHARED_VARIABLE_KEYS__", keys_js)

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Built {OUTPUT_PATH.name} from {TEMPLATE_PATH.name}")


if __name__ == "__main__":
    build()
