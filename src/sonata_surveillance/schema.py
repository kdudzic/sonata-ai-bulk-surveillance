"""Layout of the evaluation workbooks.

The spreadsheet is this project's database. Sheet ``eval`` holds one row per
evaluated post (one pair contributes two rows, ``case_side`` A and B), and the
output columns are grouped by decision mode, side by side, so a single post can
carry results from several modes at once.

Column indices are 1-based, matching ``openpyxl``.

Caveat for anyone reading old result files: the archived workbooks under
``runs/`` were hand-edited in Excel during the pilot and some sheets drift from
the layout below (``runs/05-results/all-runs-consolidated.xlsx`` is the clearest
example -- its ``short`` sheet uses its own narrower layout). Always trust row 2
of the sheet in front of you over this module when reading historical data.
This module is authoritative only for what the code *writes*.
"""

from __future__ import annotations

from enum import Enum

#: Sheet the evaluator reads from and writes to.
EVAL_SHEET = "eval"

#: Sheet holding generation parameters and gold labels, one row per pair.
PARAMETERS_SHEET = "parameters"

#: Row 1 is a merged group banner, row 2 the real header, data starts at row 3.
HEADER_ROW = 2
FIRST_DATA_ROW = 3


class DecisionMode(str, Enum):
    """Which prompt is used, and therefore which block of columns is filled."""

    #: Free-text rationale only.
    RATIONALE = "RATIONALE"
    #: Structured contrastive explanation: evidence spans, factors, counterfactual.
    STRUCTURED = "STRUCTURED"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def parse(cls, value: str) -> "DecisionMode":
        """Accept the mode name in any casing, for command-line convenience."""
        try:
            return cls(value.upper())
        except ValueError as exc:
            names = ", ".join(m.value for m in cls)
            raise ValueError(f"Unknown mode {value!r}. Expected one of: {names}") from exc


# ── Shared input columns (sheet: eval) ────────────────────────────────────────

COL_PAIR_ID = 1          # A  e.g. "P001"
COL_CASE_SIDE = 2        # B  "A" or "B"
COL_TARGET_MODEL = 3     # C  OpenRouter model id to query
COL_EVALUATE_POST = 4    # D  human-facing run flag, ignored by the Python code
COL_EVALUATED_POST = 5   # E  the post text itself

# ── Output columns, per mode ──────────────────────────────────────────────────

#: Free-text rationale mode, columns F-K.
RATIONALE_COLS: dict[str, int] = {
    "model_id": 6,
    "prompt_id": 7,
    "generated_on": 8,
    "decision": 9,
    "short_rationale": 10,
    "reviewer_notes": 11,
}

#: Structured contrastive mode, columns L-U.
STRUCTURED_COLS: dict[str, int] = {
    "model_id": 12,
    "prompt_id": 13,
    "generated_on": 14,
    "decision": 15,
    "evidence_spans": 16,
    "factors_for_decision": 17,
    "factors_against_decision": 18,
    "counterfactual_change": 19,
    "short_rationale": 20,
    "reviewer_notes": 21,
}

OUTPUT_COLS: dict[DecisionMode, dict[str, int]] = {
    DecisionMode.RATIONALE: RATIONALE_COLS,
    DecisionMode.STRUCTURED: STRUCTURED_COLS,
}

#: Structured-output-plus-CoT mode, columns V-AF. Declared here for reference
#: only: it exists in the workbook banners and in some archived results (note the
#: extra ``reasoning_trace`` field) but was never implemented in this codebase --
#: the browser app under ``webapp/`` was used for it instead. Nothing writes it.
COL_COT_BLOCK_START = 22
STRUCTURED_COT_COLS: dict[str, int] = {
    "model_id": 22,
    "prompt_id": 23,
    "generated_on": 24,
    "decision": 25,
    "evidence_spans": 26,
    "factors_for_decision": 27,
    "factors_against_decision": 28,
    "counterfactual_change": 29,
    "short_rationale": 30,
    "reasoning_trace": 31,
    "reviewer_notes": 32,
}

#: Rubric the legal expert scored explanations with, six dimensions at 0-2 each,
#: summing to the 0-12 ``Score``. Present only in the archived result workbooks
#: under a "Human judicial review" banner; the Python code never writes it.
HUMAN_REVIEW_DIMENSIONS: tuple[str, ...] = (
    "Specificity",
    "Contrastiveness",
    "Contestability",
    "Plain language",
    "Evidential grounding",
    "Proportionality relevance",
)

#: Columns AG-AM. Beware: several of these header cells carry a trailing space in
#: the workbooks ("Specificity "), so match headers with ``.strip()``.
HUMAN_REVIEW_COLS: dict[str, int] = {
    "Specificity": 33,
    "Contrastiveness": 34,
    "Contestability": 35,
    "Plain language": 36,
    "Evidential grounding": 37,
    "Proportionality relevance": 38,
    "Score": 39,
}

#: The two decisions a model may return. DISCARD is the default outcome; the
#: rulebook treats retention as the exception that needs a textual basis.
DECISIONS: tuple[str, ...] = ("DISCARD", "KEEP_FOR_REVIEW")
