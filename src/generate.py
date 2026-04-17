from __future__ import annotations

import json
import random
import re
from copy import deepcopy
from pathlib import Path

from tqdm import tqdm

from openrouter_api import OpenRouterAPI

MODEL_ID = "anthropic/claude-sonnet-4.6"
API_KEY_PATH = Path("/home/ked/sync/tokens/sonata_openrouter.txt")
REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = REPO_ROOT / "data" / "prompt.md"
HIDDEN_VARIABLES_PATH = REPO_ROOT / "data" / "hidden_variables.json"
OUTPUTS_DIR = REPO_ROOT / "outputs"
METADATA_PATH = OUTPUTS_DIR / "metadata.json"
GENERATED_POSTS_PATH = OUTPUTS_DIR / "generated_posts.json"
RNG_SEED = 42
PAIR_COUNT = 10


def load_hidden_variables() -> dict[str, list[str]]:
    return json.loads(HIDDEN_VARIABLES_PATH.read_text(encoding="utf-8"))


def choose_hidden_values(
    hidden_variables: dict[str, list[str]], rng: random.Random
) -> dict[str, str]:
    return {
        key: rng.choice(values) for key, values in hidden_variables.items()
    }


def choose_pair_hidden_values(
    hidden_variables: dict[str, list[str]],
    rng: random.Random,
) -> tuple[dict[str, str], dict[str, str], str, str, str]:
    shared_values = choose_hidden_values(hidden_variables, rng)
    changed_key = rng.choice(list(hidden_variables.keys()))
    case_a_value = shared_values[changed_key]
    alternatives = [
        value
        for value in hidden_variables[changed_key]
        if value != case_a_value
    ]

    if not alternatives:
        raise ValueError(
            f"No alternative values available for '{changed_key}'."
        )

    case_b_value = rng.choice(alternatives)
    case_a_hidden_values, case_b_hidden_values = build_case_hidden_values(
        shared_values, changed_key, case_a_value, case_b_value
    )
    return (
        case_a_hidden_values,
        case_b_hidden_values,
        changed_key,
        case_a_value,
        case_b_value,
    )


def build_case_hidden_values(
    shared_values: dict[str, str],
    changed_key: str,
    case_a_value: str,
    case_b_value: str,
) -> tuple[dict[str, str], dict[str, str]]:
    case_a = {**shared_values, changed_key: case_a_value}
    case_b = {**shared_values, changed_key: case_b_value}
    return case_a, case_b


def render_prompt(
    template: str,
    shared_values: dict[str, str],
    changed_key: str,
    case_a_value: str,
    case_b_value: str,
) -> str:
    prompt = template
    prompt_values = deepcopy(shared_values)
    prompt_values[changed_key] = (
        f"CASE_A={case_a_value}; CASE_B={case_b_value}"
    )
    prompt_values["changed_variable"] = changed_key
    prompt_values["case_a_value"] = case_a_value
    prompt_values["case_b_value"] = case_b_value

    for key, value in prompt_values.items():
        prompt = prompt.replace(f"{{{key}}}", value)
    return prompt


def parse_case_pair(response: str) -> tuple[str, str]:
    match = re.search(
        r"CASE_A:\s*(.*?)\s*CASE_B:\s*(.*)\Z",
        response.strip(),
        re.DOTALL,
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


def write_metadata(metadata: dict) -> None:
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_generated_posts(generated_posts: dict[str, dict[str, str]]) -> None:
    GENERATED_POSTS_PATH.write_text(
        json.dumps(generated_posts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_metadata() -> dict[str, object]:
    return {
        "model_id": MODEL_ID,
        "rng_seed": RNG_SEED,
        "pair_count": 0,
        "api_call_count": 0,
        "output_count": 0,
        "prompt_path": "data/prompt.md",
        "hidden_variables_path": "data/hidden_variables.json",
        "outputs_dir": "outputs",
        "pairs": [],
    }


def load_metadata() -> dict[str, object]:
    if not METADATA_PATH.exists():
        return build_metadata()

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if "pairs" not in metadata or not isinstance(metadata["pairs"], list):
        metadata["pairs"] = []
    metadata["model_id"] = MODEL_ID
    metadata["rng_seed"] = RNG_SEED
    metadata["prompt_path"] = "data/prompt.md"
    metadata["hidden_variables_path"] = "data/hidden_variables.json"
    metadata["outputs_dir"] = "outputs"
    return metadata


def load_generated_posts() -> dict[str, dict[str, str]]:
    if not GENERATED_POSTS_PATH.exists():
        return {}
    return json.loads(GENERATED_POSTS_PATH.read_text(encoding="utf-8"))


def next_pair_id(
    metadata: dict[str, object], generated_posts: dict[str, dict[str, str]]
) -> int:
    pair_ids = []

    pairs = metadata.get("pairs", [])
    if isinstance(pairs, list):
        pair_ids.extend(
            pair["pair_id"]
            for pair in pairs
            if isinstance(pair, dict) and isinstance(pair.get("pair_id"), int)
        )

    pair_ids.extend(
        int(pair_id) for pair_id in generated_posts if pair_id.isdigit()
    )

    return max(pair_ids, default=0) + 1


def sync_metadata_counts(metadata: dict[str, object]) -> None:
    pairs = metadata.get("pairs", [])
    assert isinstance(pairs, list)
    pair_count = len(pairs)
    metadata["pair_count"] = pair_count
    metadata["api_call_count"] = pair_count
    metadata["output_count"] = pair_count * 2


def main() -> None:
    rng = random.Random(RNG_SEED)
    hidden_variables = load_hidden_variables()
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    OUTPUTS_DIR.mkdir(exist_ok=True)

    client = OpenRouterAPI(model_name=MODEL_ID, api_key_path=str(API_KEY_PATH))
    metadata = load_metadata()
    generated_posts = load_generated_posts()
    start_pair_id = next_pair_id(metadata, generated_posts)
    sync_metadata_counts(metadata)
    for _ in range(start_pair_id - 1):
        choose_pair_hidden_values(hidden_variables, rng)

    with tqdm(
        total=PAIR_COUNT, desc="Generating pairs", unit="pair"
    ) as progress:
        for pair_index in range(start_pair_id, start_pair_id + PAIR_COUNT):
            (
                case_a_hidden_values,
                case_b_hidden_values,
                changed_key,
                case_a_value,
                case_b_value,
            ) = choose_pair_hidden_values(hidden_variables, rng)

            prompt = render_prompt(
                template=prompt_template,
                shared_values=case_a_hidden_values,
                changed_key=changed_key,
                case_a_value=case_a_value,
                case_b_value=case_b_value,
            )
            case_a_text, case_b_text = parse_case_pair(client.generate(prompt))

            progress.set_postfix(
                pair=pair_index,
                changed_key=changed_key,
                cases="A/B",
            )

            cast_pairs = metadata["pairs"]
            assert isinstance(cast_pairs, list)
            cast_pairs.append(
                {
                    "pair_id": pair_index,
                    "changed_key": changed_key,
                    "changed_from": case_a_value,
                    "changed_to": case_b_value,
                    "cases": {
                        "CASE_A": {
                            "hidden_values": case_a_hidden_values,
                        },
                        "CASE_B": {
                            "hidden_values": case_b_hidden_values,
                        },
                    },
                }
            )
            generated_posts[str(pair_index)] = {
                "CASE_A": case_a_text,
                "CASE_B": case_b_text,
            }

            sync_metadata_counts(metadata)
            write_metadata(metadata)
            write_generated_posts(generated_posts)
            progress.update(1)


if __name__ == "__main__":
    main()
