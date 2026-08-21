"""Run target models over the posts in an evaluation workbook.

Reads the ``eval`` sheet, asks each row's ``target_model`` to decide
DISCARD or KEEP_FOR_REVIEW on that row's post, and writes the answer back into
the column block belonging to the chosen decision mode.

Two properties worth knowing before you touch this:

* **It writes in place.** The workbook is both input and output. Work on a copy
  if the original matters.
* **It is resumable and idempotent.** A row whose ``model_id`` cell is already
  filled for the current mode is skipped, so rerunning after a crash only fills
  the gaps. To force a redo, clear that mode's column block first.

The two modes differ only in the prompt and therefore in the shape of the JSON
the model returns -- same posts, same models. That is the pilot's comparison:
formats against each other, not models against each other.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import openpyxl
from tqdm import tqdm

from . import config, schema
from .openrouter import OpenRouterAPI

PROMPT_FILES = {
    schema.DecisionMode.RATIONALE: config.PROMPT_DECISION_SIMPLE_PATH,
    schema.DecisionMode.STRUCTURED: config.PROMPT_DECISION_STRUCT_PATH,
}


# ── Response handling ─────────────────────────────────────────────────────────

def parse_json_response(text: str) -> dict:
    """Parse the model's JSON, tolerating a markdown code fence around it."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text.strip())


def join_list(value: object) -> str:
    """Flatten a JSON list into one newline-separated cell."""
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value) if value is not None else ""


def build_row_data(
    parsed: dict,
    mode: schema.DecisionMode,
    target_model: str,
    prompt_id: str,
) -> dict[str, object]:
    """Map a parsed response onto the column names for ``mode``.

    ``prompt_id`` records which prompt file produced the answer; it is the
    provenance link back from a result to the exact wording used, which is why
    the prompt filenames must stay stable.
    """
    row = {
        "model_id": target_model,
        "prompt_id": prompt_id,
        "generated_on": date.today().isoformat(),
        "decision": parsed.get("decision", ""),
        "reviewer_notes": "",
    }
    if mode is schema.DecisionMode.RATIONALE:
        row["short_rationale"] = parsed.get("rationale", "")
    else:
        row["evidence_spans"] = join_list(parsed.get("evidence_spans"))
        row["factors_for_decision"] = join_list(parsed.get("factors_for_decision"))
        row["factors_against_decision"] = join_list(
            parsed.get("factors_against_decision")
        )
        row["counterfactual_change"] = parsed.get("counterfactual_change", "")
        row["short_rationale"] = parsed.get("short_rationale", "")
    return row


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--workbook", type=Path, default=config.PAIRS_XLSX,
        help="Workbook to read and write in place (default: %(default)s)",
    )
    parser.add_argument(
        "--mode",
        type=schema.DecisionMode.parse,
        choices=list(schema.DecisionMode),
        default=schema.DecisionMode.RATIONALE,
        help="Decision mode, selecting both prompt and output columns "
        "(default: %(default)s)",
    )
    parser.add_argument(
        "--raw-output-dir", type=Path, default=None,
        help="Where to dump the unedited JSON responses "
        "(default: alongside the workbook)",
    )
    parser.add_argument(
        "--max-attempts", type=int, default=config.DEFAULT_MAX_ATTEMPTS,
        help="Retries per post on unparseable output (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    mode: schema.DecisionMode = args.mode
    cols = schema.OUTPUT_COLS[mode]

    prompt_path = PROMPT_FILES[mode]
    prompt_template = prompt_path.read_text(encoding="utf-8")
    prompt_id = prompt_path.name

    workbook_path: Path = args.workbook
    raw_output_dir: Path = args.raw_output_dir or workbook_path.parent
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    raw_outputs_path = (
        raw_output_dir
        / f"raw_{workbook_path.stem}_{mode.value.lower()}_{date.today().isoformat()}.json"
    )

    workbook = openpyxl.load_workbook(workbook_path)
    sheet = workbook[schema.EVAL_SHEET]

    # A row is pending when it has a post but no result yet for this mode.
    pending_rows = [
        row_idx
        for row_idx in range(schema.FIRST_DATA_ROW, sheet.max_row + 1)
        if sheet.cell(row_idx, schema.COL_EVALUATED_POST).value
        and not sheet.cell(row_idx, cols["model_id"]).value
    ]

    if not pending_rows:
        print(
            f"Nothing to evaluate in {workbook_path.name} (mode={mode.value}): "
            "every row with a post is already filled."
        )
        return

    clients: dict[str, OpenRouterAPI] = {}

    def get_client(model_name: str) -> OpenRouterAPI:
        if model_name not in clients:
            clients[model_name] = OpenRouterAPI(model_name=model_name)
        return clients[model_name]

    raw_outputs: dict[str, dict] = {}

    with tqdm(
        total=len(pending_rows), desc=f"Evaluating [{mode.value}]", unit="post"
    ) as progress:
        for row_idx in pending_rows:
            post_text = str(sheet.cell(row_idx, schema.COL_EVALUATED_POST).value).strip()
            target_model = str(
                sheet.cell(row_idx, schema.COL_TARGET_MODEL).value or ""
            ).strip()
            pair_id = sheet.cell(row_idx, schema.COL_PAIR_ID).value
            case_side = sheet.cell(row_idx, schema.COL_CASE_SIDE).value
            label = f"{pair_id}/{case_side}"

            if not target_model:
                tqdm.write(f"[{label}] SKIP: target_model is empty")
                progress.update(1)
                continue

            prompt = prompt_template.replace("{post}", post_text)
            client = get_client(target_model)

            parsed: dict | None = None
            last_error: Exception | None = None
            for attempt in range(1, args.max_attempts + 1):
                try:
                    parsed = parse_json_response(client.generate(prompt))
                    last_error = None
                    break
                except Exception as exc:  # network error or unparseable JSON
                    last_error = exc
                    if attempt < args.max_attempts:
                        tqdm.write(
                            f"[{label}] attempt {attempt} failed ({exc}) - retrying..."
                        )

            if last_error is not None or parsed is None:
                tqdm.write(f"[{label}] ERROR: {last_error}")
                progress.update(1)
                continue

            raw_outputs[label] = parsed
            row_data = build_row_data(parsed, mode, target_model, prompt_id)
            for field, col_idx in cols.items():
                sheet.cell(row_idx, col_idx).value = row_data.get(field, "")

            progress.set_postfix(pair=label, decision=parsed.get("decision", "?"))
            progress.update(1)

    workbook.save(workbook_path)
    raw_outputs_path.write_text(
        json.dumps(raw_outputs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved results into {workbook_path}")
    print(f"Saved raw responses to {raw_outputs_path}")


if __name__ == "__main__":
    main()
