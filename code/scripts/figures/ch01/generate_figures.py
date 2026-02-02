"""
Генерация рисунков для раздела 1.1.
Запуск из корня проекта:
  python code/scripts/figures/ch01/generate_figures.py
"""
from pathlib import Path
import importlib.util

from code.lib.plot_utils import run_example

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"
OUTPUT_DIR = ROOT / "book" / "images"

EXAMPLE_FILES = [
    "01_request_similarity_zone.py",
    "02_venn_event_and_complement.py",
    "03_equivalent_events.py",
    "04_event_union.py",
    "05_event_intersection.py",
    "06_event_joint.py",
    "07_event_disjoint.py",
]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for fname in EXAMPLE_FILES:
        fpath = EXAMPLES_DIR / fname
        module = load_module(fpath)
        out_name = fpath.with_suffix('.png').name
        run_example(module.draw, out_name, save=True, show=False, directory=str(OUTPUT_DIR))


if __name__ == "__main__":
    main()
