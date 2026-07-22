"""Создаёт видимую метку версии и времени сборки книги.

Quarto запускает скрипт перед каждой сборкой. В CI значения можно задать
переменными BOOK_VERSION и BOOK_BUILD_TIME.
"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from subprocess import CalledProcessError, run


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "tmp/build-info.qmd"


def git_version() -> str:
    """Возвращает ближайший тег или краткий идентификатор текущего коммита."""
    try:
        result = run(
            [
                "git",
                "describe",
                "--tags",
                "--match",
                "v[0-9]*",
                "--always",
                "--dirty",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (CalledProcessError, FileNotFoundError):
        return "локальная-сборка"
    return result.stdout.strip()


def build_time() -> str:
    """Возвращает время из CI или текущее локальное время с часовым поясом."""
    configured = os.getenv("BOOK_BUILD_TIME")
    if configured:
        return configured
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def main() -> None:
    version = os.getenv("BOOK_VERSION") or git_version()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "::: {.build-info}\n"
        f"**Сборка книги:** `{version}` · {build_time()}\n"
        ":::\n",
        encoding="utf-8",
    )
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
