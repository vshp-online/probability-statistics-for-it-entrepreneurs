"""Создаёт QR-код и иллюстрации Calc для эмпирического распределения.

Запускать из корня репозитория:
    python code/scripts/figures/ch02/generate_empirical_workbook_assets.py
"""

from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[4]
WORKBOOK = ROOT / "code/data/empirical-distribution-calc.ods"
QR_OUTPUT = ROOT / "book/images/17_empirical-distribution-calc-qr.png"
HISTOGRAM_OUTPUT = ROOT / "book/images/18_empirical-histogram-calc.png"
CUMULATIVE_OUTPUT = ROOT / "book/images/19_empirical-cumulative-calc.png"
DESCRIPTIVE_OUTPUT = ROOT / "book/images/20_descriptive-statistics-calc.png"
TARGET = (
    "https://github.com/vshp-online/ps-it-book/"
    "blob/main/code/data/empirical-distribution-calc.ods"
)


def trim_white_canvas(image: Image.Image, padding: int = 12) -> Image.Image:
    """Обрезает белый холст, оставляя одинаковое поле вокруг диаграммы."""
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, "white")
    bounds = ImageChops.difference(rgb, background).getbbox()
    if bounds is None:
        raise RuntimeError("В экспортированном фрагменте не найдена диаграмма")
    left, top, right, bottom = bounds
    return rgb.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(rgb.width, right + padding),
            min(rgb.height, bottom + padding),
        )
    )


def create_qr_code() -> None:
    """Сохраняет QR-код со ссылкой на рабочую книгу в GitHub."""
    query = urlencode({"size": "360x360", "format": "png", "data": TARGET})
    url = f"https://api.qrserver.com/v1/create-qr-code/?{query}"
    with urlopen(url, timeout=30) as response:
        QR_OUTPUT.write_bytes(response.read())


def export_workbook_images() -> None:
    """Экспортирует диаграммы и таблицу характеристик из Calc."""
    with TemporaryDirectory(dir=ROOT / "tmp") as temporary:
        temporary_path = Path(temporary)
        profile = temporary_path / "lo-profile"
        profile.mkdir()
        run(
            [
                "soffice",
                "--headless",
                f"-env:UserInstallation=file://{profile}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temporary_path),
                str(WORKBOOK),
            ],
            check=True,
        )
        pdf_path = temporary_path / f"{WORKBOOK.stem}.pdf"
        prefix = temporary_path / "distribution"
        run(
            [
                "pdftoppm",
                "-f",
                "4",
                "-l",
                "5",
                "-png",
                "-r",
                "150",
                str(pdf_path),
                str(prefix),
            ],
            check=True,
        )
        with Image.open(temporary_path / "distribution-4.png") as page:
            histogram = trim_white_canvas(page.crop((904, 260, 1590, 620)))
            cumulative = trim_white_canvas(page.crop((890, 650, 1590, 970)))
        with Image.open(temporary_path / "distribution-5.png") as page:
            descriptive = trim_white_canvas(page, padding=18)
        histogram.save(HISTOGRAM_OUTPUT)
        cumulative.save(CUMULATIVE_OUTPUT)
        descriptive.save(DESCRIPTIVE_OUTPUT)


def main() -> None:
    """Обновляет связанные с рабочей книгой изображения."""
    (ROOT / "tmp").mkdir(exist_ok=True)
    QR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    create_qr_code()
    export_workbook_images()
    for output in (
        QR_OUTPUT,
        HISTOGRAM_OUTPUT,
        CUMULATIVE_OUTPUT,
        DESCRIPTIVE_OUTPUT,
    ):
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
