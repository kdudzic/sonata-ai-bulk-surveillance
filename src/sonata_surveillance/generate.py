"""Generate controlled counterfactual post pairs.

Each pair shares one draw of the eight hidden variables in
``data/hidden_variables.json``. Exactly one variable is then flipped to a
different value, producing CASE_A and CASE_B. That single flip is the
experimental manipulation: any difference in how a model treats the two posts
should be attributable to it and nothing else.

Runs are resumable. Output lands in a run directory holding two files:

``generated_posts.json``
    ``{pair_id: {"CASE_A": text, "CASE_B": text}}``
``metadata.json``
    the hidden-variable draw behind each pair, plus run provenance.

Rerunning against an existing run directory continues from the highest pair id
and replays the RNG so the draws stay on the same sequence.

Note: the 48 curated pairs in ``data/pairs.xlsx`` were not produced by this
script -- they came later, through the browser app. ``runs/01-exploratory-100-pairs``
is the archived output of this script, using a prompt that no longer exists.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from copy import deepcopy
from pathlib import Path

from tqdm import tqdm

from . import config
from .openrouter import OpenRouterAPI

GENERATED_POSTS_FILENAME = "generated_posts.json"
METADATA_FILENAME = "metadata.json"


# ── Hidden-variable sampling ──────────────────────────────────────────────────

def load_hidden_variables() -> dict[str, list[str]]:
    return json.loads(config.HIDDEN_VARIABLES_PATH.read_text(encoding="utf-8"))


def choose_hidden_values(
    hidden_variables: dict[str, list[str]], rng: random.Random
) -> dict[str, str]:
    """Draw one value for every hidden variable."""
    return {key: rng.choice(values) for key, values in hidden_variables.items()}


def choose_pair_hidden_values(
    hidden_variables: dict[str, list[str]],
    rng: random.Random,
) -> tuple[dict[str, str], dict[str, str], str, str, str]:
    """Draw a shared scenario, then flip exactly one variable.

    Returns:
        ``(case_a_values, case_b_values, changed_key, case_a_value, case_b_value)``
    """
    shared_values = choose_hidden_values(hidden_variables, rng)
    changed_key = rng.choice(list(hidden_variables.keys()))
    case_a_value = shared_values[changed_key]
    alternatives = [v for v in hidden_variables[changed_key] if v != case_a_value]

    if not alternatives:
        raise ValueError(f"No alternative values available for '{changed_key}'.")

    case_b_value = rng.choice(alternatives)
    case_a = {**shared_values, changed_key: case_a_value}
    case_b = {**shared_values, changed_key: case_b_value}
    return case_a, case_b, changed_key, case_a_value, case_b_value


# ── Prompt rendering and parsing ──────────────────────────────────────────────

def render_prompt(
    template: str,
    shared_values: dict[str, str],
    changed_key: str,
    case_a_value: str,
    case_b_value: str,
) -> str:
    """Substitute ``{placeholder}`` markers in the generation prompt."""
    prompt_values = deepcopy(shared_values)
    prompt_values[changed_key] = f"CASE_A={case_a_value}; CASE_B={case_b_value}"
    prompt_values["changed_variable"] = changed_key
    prompt_values["case_a_value"] = case_a_value
    prompt_values["case_b_value"] = case_b_value

    prompt = template
    for key, value in prompt_values.items():
        prompt = prompt.replace(f"{{{key}}}", value)
    return prompt


def parse_case_pair(response: str) -> tuple[str, str]:
    """Pull CASE_A and CASE_B out of the model's reply."""
    match = re.search(
        r"CASE_A:\s*(.*?)\s*CASE_B:\s*(.*)\Z", response.strip(), re.DOTALL
    )
    if match is None:
        raise ValueError(
            "Model response did not match the expected CASE_A/CASE_B format."
        )

    case_a_text = match.group(1).strip()
    case_b_text = match.group(2).strip()
    if not case_a_text or not case_b_text:
        raise ValueError("Model response contained an empty CASE_A or CASE_B.")
    return case_a_text, case_b_text


# ── Run directory state ───────────────────────────────────────────────────────

def build_metadata(model_id: str, rng_seed: int) -> dict[str, object]:
    return {
        "model_id": model_id,
        "rng_seed": rng_seed,
        "pair_count": 0,
        "api_call_count": 0,
        "output_count": 0,
        "prompt_path": str(config.PROMPT_GENERATE_PATH.relative_to(config.REPO_ROOT)),
        "hidden_variables_path": str(
            config.HIDDEN_VARIABLES_PATH.relative_to(config.REPO_ROOT)
        ),
        "pairs": [],
    }


def load_metadata(run_dir: Path, model_id: str, rng_seed: int) -> dict[str, object]:
    """Load an existing run's metadata, or start a fresh one."""
    metadata_path = run_dir / METADATA_FILENAME
    if not metadata_path.exists():
        return build_metadata(model_id, rng_seed)

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata.get("pairs"), list):
        metadata["pairs"] = []

    # Refresh provenance to match this invocation, but keep the accumulated
    # pairs. Counts are recomputed by sync_metadata_counts.
    fresh = build_metadata(model_id, rng_seed)
    for field in ("model_id", "rng_seed", "prompt_path", "hidden_variables_path"):
        metadata[field] = fresh[field]
    return metadata


def load_generated_posts(run_dir: Path) -> dict[str, dict[str, str]]:
    posts_path = run_dir / GENERATED_POSTS_FILENAME
    if not posts_path.exists():
        return {}
    return json.loads(posts_path.read_text(encoding="utf-8"))


def next_pair_id(
    metadata: dict[str, object], generated_posts: dict[str, dict[str, str]]
) -> int:
    """One past the highest pair id seen in either file."""
    pair_ids: list[int] = []

    pairs = metadata.get("pairs", [])
    if isinstance(pairs, list):
        pair_ids.extend(
            pair["pair_id"]
            for pair in pairs
            if isinstance(pair, dict) and isinstance(pair.get("pair_id"), int)
        )
    pair_ids.extend(int(pid) for pid in generated_posts if pid.isdigit())
    return max(pair_ids, default=0) + 1


def sync_metadata_counts(metadata: dict[str, object]) -> None:
    pairs = metadata.get("pairs", [])
    assert isinstance(pairs, list)
    metadata["pair_count"] = len(pairs)
    metadata["api_call_count"] = len(pairs)
    metadata["output_count"] = len(pairs) * 2


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=config.RUNS_DIR / "generation",
        help="Directory holding generated_posts.json and metadata.json. "
        "Point at an existing run to resume it. (default: %(default)s)",
    )
    parser.add_argument(
        "--pairs", type=int, default=config.DEFAULT_PAIR_COUNT,
        help="Number of new pairs to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--model", default=config.DEFAULT_GENERATION_MODEL,
        help="Generating model, distinct from the models under test "
        "(default: %(default)s)",
    )
    parser.add_argument(
        "--seed", type=int, default=config.DEFAULT_RNG_SEED,
        help="RNG seed for hidden-variable draws (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run_dir: Path = args.run_dir
    run_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    hidden_variables = load_hidden_variables()
    prompt_template = config.PROMPT_GENERATE_PATH.read_text(encoding="utf-8")

    client = OpenRouterAPI(model_name=args.model)
    metadata = load_metadata(run_dir, args.model, args.seed)
    generated_posts = load_generated_posts(run_dir)

    start_pair_id = next_pair_id(metadata, generated_posts)
    sync_metadata_counts(metadata)

    # Replay the draws already consumed so a resumed run stays on the same
    # RNG sequence as an uninterrupted one.
    for _ in range(start_pair_id - 1):
        choose_pair_hidden_values(hidden_variables, rng)

    with tqdm(total=args.pairs, desc="Generating pairs", unit="pair") as progress:
        for pair_index in range(start_pair_id, start_pair_id + args.pairs):
            (
                case_a_values,
                case_b_values,
                changed_key,
                case_a_value,
                case_b_value,
            ) = choose_pair_hidden_values(hidden_variables, rng)

            prompt = render_prompt(
                template=prompt_template,
                shared_values=case_a_values,
                changed_key=changed_key,
                case_a_value=case_a_value,
                case_b_value=case_b_value,
            )
            case_a_text, case_b_text = parse_case_pair(client.generate(prompt))

            progress.set_postfix(pair=pair_index, changed_key=changed_key)

            pairs = metadata["pairs"]
            assert isinstance(pairs, list)
            pairs.append(
                {
                    "pair_id": pair_index,
                    "changed_key": changed_key,
                    "changed_from": case_a_value,
                    "changed_to": case_b_value,
                    "cases": {
                        "CASE_A": {"hidden_values": case_a_values},
                        "CASE_B": {"hidden_values": case_b_values},
                    },
                }
            )
            generated_posts[str(pair_index)] = {
                "CASE_A": case_a_text,
                "CASE_B": case_b_text,
            }

            # Written every iteration so an interrupted run stays resumable.
            sync_metadata_counts(metadata)
            write_json(run_dir / METADATA_FILENAME, metadata)
            write_json(run_dir / GENERATED_POSTS_FILENAME, generated_posts)
            progress.update(1)

    print(f"Wrote {run_dir / GENERATED_POSTS_FILENAME}")


if __name__ == "__main__":
    main()
