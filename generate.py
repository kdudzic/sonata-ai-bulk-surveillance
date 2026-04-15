from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
SRC_GENERATE_PATH = SRC_DIR / "generate.py"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_main():
    spec = importlib.util.spec_from_file_location(
        "sonata_generate_entry", SRC_GENERATE_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {SRC_GENERATE_PATH}.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


if __name__ == "__main__":
    load_main()()
