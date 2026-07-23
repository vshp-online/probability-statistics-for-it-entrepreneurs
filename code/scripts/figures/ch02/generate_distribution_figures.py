"""Генерирует иллюстрации закона распределения для второй части книги.

Запускать из корня репозитория:
    python3 code/scripts/figures/ch02/generate_distribution_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUTPUT_DIR = ROOT / "book" / "images"
BLUE = "#2878A9"
LIGHT_BLUE = "#DCEEF7"
GREEN = "#4F8A5B"
GRID = "#D9DEE3"


def style_axis(axis) -> None:
    """Применяет единый спокойный стиль к координатной области."""
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.8)
    axis.set_axisbelow(True)


def save_discrete_distribution() -> None:
    """Строит ряд распределения и функцию распределения из примера."""
    values = np.array([0, 1, 2, 3])
    probabilities = np.array([0.729, 0.243, 0.027, 0.001])
    cumulative = np.cumsum(probabilities)

    figure, axes = plt.subplots(1, 2, figsize=(10, 4.2))

    polygon, distribution = axes
    polygon.vlines(values, 0, probabilities, color=BLUE, linewidth=2)
    polygon.plot(values, probabilities, color=BLUE, marker="o", linewidth=2)
    for value, probability in zip(values, probabilities):
        polygon.annotate(
            f"{probability:.3f}".replace(".", ","),
            (value, probability),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )
    polygon.set(
        title="Ряд распределения",
        xlabel="Число недоступных экземпляров, $x$",
        ylabel="$P(X=x)$",
        xticks=values,
        ylim=(0, 0.82),
    )
    style_axis(polygon)

    step_x = np.array([-0.5, 0, 1, 2, 3, 3.5])
    step_y = np.array([0, cumulative[0], cumulative[1], cumulative[2], 1, 1])
    distribution.step(step_x, step_y, where="post", color=GREEN, linewidth=2.4)
    distribution.scatter(values, cumulative, color=GREEN, zorder=3)
    distribution.set(
        title="Функция распределения",
        xlabel="$x$",
        ylabel="$F(x)$",
        xticks=values,
        xlim=(-0.5, 3.5),
        ylim=(-0.03, 1.07),
    )
    style_axis(distribution)

    figure.tight_layout(w_pad=3)
    figure.savefig(
        OUTPUT_DIR / "12_discrete_distribution.png",
        dpi=220,
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(figure)


def save_continuous_density() -> None:
    """Показывает вероятность интервала как площадь под плотностью."""
    values = np.linspace(-3.5, 3.5, 700)
    density = np.exp(-(values**2) / 2) / np.sqrt(2 * np.pi)
    left, right = -0.8, 1.2

    figure, axis = plt.subplots(figsize=(8.8, 4.4))
    axis.plot(values, density, color=BLUE, linewidth=2.4)
    interval = (values >= left) & (values <= right)
    axis.fill_between(
        values[interval],
        density[interval],
        color=LIGHT_BLUE,
        edgecolor=BLUE,
        linewidth=0.8,
    )
    axis.axvline(left, color="#6B7280", linestyle="--", linewidth=1)
    axis.axvline(right, color="#6B7280", linestyle="--", linewidth=1)
    axis.text(left, -0.015, "$a$", ha="center", va="top", fontsize=12)
    axis.text(right, -0.015, "$b$", ha="center", va="top", fontsize=12)
    axis.text(
        (left + right) / 2,
        0.16,
        "$P(a<X<b)$",
        ha="center",
        va="center",
        fontsize=12,
    )
    axis.set(
        xlabel="$x$",
        ylabel="$f(x)$",
        xlim=(-3.5, 3.5),
        ylim=(0, 0.44),
    )
    axis.set_xticks([])
    axis.set_yticks([])
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIR / "13_continuous_density.png",
        dpi=220,
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(figure)


def main() -> None:
    """Создаёт обе иллюстрации."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_discrete_distribution()
    save_continuous_density()
    print("book/images/12_discrete_distribution.png")
    print("book/images/13_continuous_density.png")


if __name__ == "__main__":
    main()
