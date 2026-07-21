"""Генерирует QR-код для рабочей книги LibreOffice из § 1.6.

Запускать из корня репозитория:
    python3 code/scripts/figures/ch01/generate_interval_workbook_qr.py
"""

from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "book/images/09_interval-estimation-calc-qr.png"
TARGET = (
    "https://github.com/vshp-online/ps-it-book/"
    "blob/main/code/data/interval-estimation-calc.ods"
)


def main() -> None:
    """Сохраняет QR-код с прямой ссылкой на файл в GitHub."""
    query = urlencode({"size": "360x360", "format": "png", "data": TARGET})
    url = f"https://api.qrserver.com/v1/create-qr-code/?{query}"
    OUTPUT.write_bytes(urlopen(url, timeout=30).read())
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
