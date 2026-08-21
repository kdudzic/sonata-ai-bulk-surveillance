"""Build the single-file browser version of the pipeline.

``webapp/index.template.html`` is the source; the build inlines the prompt files
and the hidden-variable keys into it and writes ``index.html`` at the repository
root. Root is not a style choice: GitHub Pages serves this repository from
``main`` at path ``/``, so the built file has to live there.

The browser app was how the pilot was actually run -- it takes the user's own
OpenRouter key, reads and writes the same ``eval`` sheet layout, and downloads
the filled workbook. Rerun this build after editing any prompt, or the published
site keeps serving the old wording.
"""

from __future__ import annotations

import json

from . import config

#: Placeholder in the template -> text to inline.
PROMPT_PLACEHOLDERS = {
    "__PROMPT_GENERATE__": config.PROMPT_GENERATE_PATH,
    "__PROMPT_DECISION_SIMPLE__": config.PROMPT_DECISION_SIMPLE_PATH,
    "__PROMPT_DECISION_STRUCT__": config.PROMPT_DECISION_STRUCT_PATH,
}


def escape_for_js_template_literal(text: str) -> str:
    """Make ``text`` safe to paste inside a JavaScript backtick string."""
    text = text.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    return text


def build() -> None:
    output = config.WEBAPP_TEMPLATE_PATH.read_text(encoding="utf-8")

    for placeholder, prompt_path in PROMPT_PLACEHOLDERS.items():
        output = output.replace(
            placeholder,
            escape_for_js_template_literal(prompt_path.read_text(encoding="utf-8")),
        )

    hidden_variables = json.loads(
        config.HIDDEN_VARIABLES_PATH.read_text(encoding="utf-8")
    )
    output = output.replace(
        "__SHARED_VARIABLE_KEYS__", json.dumps(list(hidden_variables.keys()))
    )

    config.WEBAPP_OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(
        f"Built {config.WEBAPP_OUTPUT_PATH.relative_to(config.REPO_ROOT)} "
        f"from {config.WEBAPP_TEMPLATE_PATH.relative_to(config.REPO_ROOT)}"
    )


def main() -> None:
    build()


if __name__ == "__main__":
    main()
