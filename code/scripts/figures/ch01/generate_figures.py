"""
Генерация рисунков для главы 1.

Запуск из корня проекта:
  python code/scripts/figures/ch01/generate_figures.py
"""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[4]
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
    """Динамически загружает модуль по пути."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plot_utils():
    """Загружает модуль plot_utils из code/lib."""
    utils_path = ROOT / "code" / "lib" / "plot_utils.py"
    spec = importlib.util.spec_from_file_location("plot_utils", utils_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    """Генерирует PNG для списка примеров в book/images."""
    plot_utils = load_plot_utils()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for fname in EXAMPLE_FILES:
        fpath = EXAMPLES_DIR / fname
        module = load_module(fpath)
        out_name = fpath.with_suffix('.png').name
        plot_utils.run_example(
            module.draw,
            out_name,
            save=True,
            show=False,
            directory=str(OUTPUT_DIR),
        )


if __name__ == "__main__":
    main()
