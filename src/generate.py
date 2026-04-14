from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path

from tqdm import tqdm

from openrouter_api import OpenRouterAPI

MODEL_ID = "anthropic/claude-sonnet-4.6"
API_KEY_PATH = Path("/home/ked/sync/tokens/openrouter.txt")
REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = REPO_ROOT / "data" / "prompt.md"
HIDDEN_VARIABLES_PATH = REPO_ROOT / "data" / "hidden_variables.json"
OUTPUTS_DIR = REPO_ROOT / "outputs"
METADATA_PATH = OUTPUTS_DIR / "metadata.json"
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


def mutate_single_variable(
    hidden_values: dict[str, str],
    hidden_variables: dict[str, list[str]],
    rng: random.Random,
) -> tuple[dict[str, str], str, str]:
    changed_key = rng.choice(list(hidden_values.keys()))
    current_value = hidden_values[changed_key]
    alternatives = [
        value
        for value in hidden_variables[changed_key]
        if value != current_value
    ]

    if not alternatives:
        raise ValueError(
            f"No alternative values available for '{changed_key}'."
        )

    updated_values = deepcopy(hidden_values)
    updated_values[changed_key] = rng.choice(alternatives)
    return updated_values, changed_key, current_value


def render_prompt(template: str, hidden_values: dict[str, str]) -> str:
    prompt = template
    for key, value in hidden_values.items():
        prompt = prompt.replace(f"{{{key}}}", value)
    return prompt


def write_metadata(metadata: dict) -> None:
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_output_filename(pair_id: int, pair_member: str) -> str:
    return f"pair_{pair_id:04d}_{pair_member}.txt"


def main() -> None:
    rng = random.Random(RNG_SEED)
    hidden_variables = load_hidden_variables()
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    OUTPUTS_DIR.mkdir(exist_ok=True)

    client = OpenRouterAPI(model_name=MODEL_ID, api_key_path=str(API_KEY_PATH))
    metadata: dict[str, object] = {
        "model_id": MODEL_ID,
        "rng_seed": RNG_SEED,
        "pair_count": PAIR_COUNT,
        "output_count": PAIR_COUNT * 2,
        "prompt_path": "data/prompt.md",
        "hidden_variables_path": "data/hidden_variables.json",
        "outputs_dir": "outputs",
        "pairs": [],
        "outputs": [],
    }

    output_index = 1

    with tqdm(
        total=PAIR_COUNT * 2, desc="Generating outputs", unit="output"
    ) as progress:
        for pair_index in range(1, PAIR_COUNT + 1):
            first_hidden_values = choose_hidden_values(hidden_variables, rng)
            second_hidden_values, changed_key, previous_value = (
                mutate_single_variable(
                    first_hidden_values, hidden_variables, rng
                )
            )

            pair_output_ids = [output_index, output_index + 1]
            prompts = [
                render_prompt(prompt_template, first_hidden_values),
                render_prompt(prompt_template, second_hidden_values),
            ]
            hidden_value_sets = [first_hidden_values, second_hidden_values]

            progress.set_postfix(
                pair=pair_index,
                changed_key=changed_key,
                output=f"{pair_output_ids[0]:04d}-{pair_output_ids[1]:04d}",
            )

            for local_index, (prompt, hidden_values) in enumerate(
                zip(prompts, hidden_value_sets, strict=True)
            ):
                current_output_id = pair_output_ids[local_index]
                paired_output_id = (
                    pair_output_ids[1]
                    if local_index == 0
                    else pair_output_ids[0]
                )
                pair_member = "a" if local_index == 0 else "b"
                filename = build_output_filename(pair_index, pair_member)
                output_path = OUTPUTS_DIR / filename
                response = client.generate(prompt)

                output_path.write_text(response, encoding="utf-8")

                cast_outputs = metadata["outputs"]
                assert isinstance(cast_outputs, list)
                cast_outputs.append(
                    {
                        "output_id": current_output_id,
                        "filename": filename,
                        "pair_id": pair_index,
                        "pair_member": pair_member,
                        "paired_with_output_id": paired_output_id,
                        "hidden_values": hidden_values,
                    }
                )
                progress.update(1)

            cast_pairs = metadata["pairs"]
            assert isinstance(cast_pairs, list)
            cast_pairs.append(
                {
                    "pair_id": pair_index,
                    "output_ids": pair_output_ids,
                    "changed_key": changed_key,
                    "changed_from": previous_value,
                    "changed_to": second_hidden_values[changed_key],
                    "outputs": [
                        {
                            "output_id": pair_output_ids[0],
                            "filename": build_output_filename(pair_index, "a"),
                            "pair_member": "a",
                            "hidden_values": first_hidden_values,
                        },
                        {
                            "output_id": pair_output_ids[1],
                            "filename": build_output_filename(pair_index, "b"),
                            "pair_member": "b",
                            "hidden_values": second_hidden_values,
                        },
                    ],
                }
            )

            write_metadata(metadata)
            output_index += 2


if __name__ == "__main__":
    main()
