"""Generate density plots for common continuous distributions.

Run from the repository root:
    python code/scripts/figures/ch02/generate_continuous_distribution_figures.py
"""

from math import pi
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_PATHS = (
    Path("book/images/15_uniform_exponential_distributions.png"),
    Path("book/images/16_weibull_normal_distributions.png"),
)
COLORS = ("#24758c", "#cc7a29", "#579c62")


def normal_density(
    values: np.ndarray, mean: float, standard_deviation: float
) -> np.ndarray:
    """Return normal-density values."""
    coefficient = 1 / (standard_deviation * np.sqrt(2 * pi))
    exponent = -0.5 * ((values - mean) / standard_deviation) ** 2
    return coefficient * np.exp(exponent)


def weibull_density(
    values: np.ndarray, scale: float, shape: float
) -> np.ndarray:
    """Return Weibull-density values for nonnegative values."""
    normalized = values / scale
    return (
        shape
        / scale
        * normalized ** (shape - 1)
        * np.exp(-(normalized**shape))
    )


def style_axis(axis: plt.Axes, title: str) -> None:
    """Apply the shared visual style to a subplot."""
    axis.set_title(title, fontweight="semibold")
    axis.set_xlabel("x")
    axis.set_ylabel("Плотность")
    axis.grid(axis="y", color="#d9e2e6", linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)


def save_figure(figure: plt.Figure, path: Path, title: str) -> None:
    """Apply the shared layout and save one figure."""
    figure.suptitle(title, fontsize=13)
    figure.tight_layout(rect=(0, 0, 1, 0.93), w_pad=2.5)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    """Build two comparable pairs of continuous-density plots."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "legend.fontsize": 8.5,
        }
    )
    first_figure, first_axes = plt.subplots(1, 2, figsize=(10.5, 3.5))

    uniform_axis = first_axes[0]
    uniform_axis.plot([-1, 0], [0, 0], color=COLORS[0], linewidth=2)
    uniform_axis.plot([0, 4], [0.25, 0.25], color=COLORS[0], linewidth=2)
    uniform_axis.plot([4, 5], [0, 0], color=COLORS[0], linewidth=2)
    uniform_axis.vlines([0, 4], 0, 0.25, color=COLORS[0], linewidth=1.3)
    uniform_axis.set_xlim(-1, 5)
    uniform_axis.set_ylim(0, 0.32)
    style_axis(uniform_axis, "Равномерное: a = 0, b = 4")

    exponential_axis = first_axes[1]
    positive_values = np.linspace(0, 5, 500)
    for color, intensity in zip(COLORS, (0.5, 1.0, 2.0), strict=True):
        density = intensity * np.exp(-intensity * positive_values)
        exponential_axis.plot(
            positive_values,
            density,
            color=color,
            linewidth=1.8,
            label=f"λ = {str(intensity).replace('.', ',')}",
        )
    exponential_axis.set_ylim(0, 2.1)
    exponential_axis.legend(frameon=False)
    style_axis(exponential_axis, "Показательное")

    save_figure(
        first_figure,
        OUTPUT_PATHS[0],
        "Равномерное и показательное распределения",
    )

    second_figure, second_axes = plt.subplots(1, 2, figsize=(10.5, 3.5))

    weibull_axis = second_axes[0]
    positive_values = np.linspace(0.02, 3.5, 500)
    for color, shape in zip(COLORS, (0.7, 1.0, 2.0), strict=True):
        weibull_axis.plot(
            positive_values,
            weibull_density(positive_values, scale=1, shape=shape),
            color=color,
            linewidth=1.8,
            label=f"k = {str(shape).replace('.', ',')}",
        )
    weibull_axis.set_ylim(0, 2.1)
    weibull_axis.legend(frameon=False)
    style_axis(weibull_axis, "Вейбулла: η = 1")

    normal_axis = second_axes[1]
    symmetric_values = np.linspace(-4, 4, 500)
    for color, standard_deviation in zip(
        COLORS, (0.6, 1.0, 1.5), strict=True
    ):
        normal_axis.plot(
            symmetric_values,
            normal_density(symmetric_values, 0, standard_deviation),
            color=color,
            linewidth=1.8,
            label=f"σ = {str(standard_deviation).replace('.', ',')}",
        )
    normal_axis.set_ylim(0, 0.7)
    normal_axis.legend(frameon=False)
    style_axis(normal_axis, "Нормальное: μ = 0")

    save_figure(
        second_figure,
        OUTPUT_PATHS[1],
        "Распределения Вейбулла и нормальное",
    )


if __name__ == "__main__":
    main()
