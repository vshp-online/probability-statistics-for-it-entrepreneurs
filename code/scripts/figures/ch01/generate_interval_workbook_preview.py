"""Создаёт иллюстрацию рабочего листа LibreOffice Calc из § 1.6.

Запускать из корня репозитория:
    python3 code/scripts/figures/ch01/generate_interval_workbook_preview.py
"""

from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[4]
WORKBOOK = ROOT / "code/data/interval-estimation-calc.ods"
OUTPUT = ROOT / "book/images/10_interval-estimation-calc-preview.png"


def trim_to_table(image: Image.Image, padding: int = 12) -> Image.Image:
    """Обрезает белый холст, оставляя небольшое поле вокруг таблицы."""
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, "white")
    bounds = ImageChops.difference(rgb, background).getbbox()
    if bounds is None:
        raise RuntimeError("В экспортированном листе не найдена таблица")

    left, top, right, bottom = bounds
    return rgb.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(rgb.width, right + padding),
            min(rgb.height, bottom + padding),
        )
    )


def main() -> None:
    """Экспортирует лист Calc в PDF и вырезает компактный фрагмент таблицы."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_path),
                str(WORKBOOK),
            ],
            check=True,
        )
        pdf_path = temp_path / f"{WORKBOOK.stem}.pdf"
        prefix = temp_path / "worksheet"
        run(["pdftoppm", "-f", "1", "-l", "1", "-png", "-r", "150", str(pdf_path), str(prefix)], check=True)
        page = Image.open(temp_path / "worksheet-1.png")
        preview = trim_to_table(page.crop((90, 150, 1040, 440)))
        preview.save(OUTPUT)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
