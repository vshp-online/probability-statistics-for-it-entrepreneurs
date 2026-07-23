"""Generate figures for the section on discrete distributions.

Run from the repository root:
    python code/scripts/figures/ch02/generate_discrete_distribution_figures.py
"""

from math import comb
from pathlib import Path

import matplotlib.pyplot as plt


OUTPUT_PATH = Path("book/images/14_binomial_distributions.png")


def binomial_probability(n: int, m: int, probability: float) -> float:
    """Return P(X=m) for X following Bin(n, probability)."""
    return comb(n, m) * probability**m * (1 - probability) ** (n - m)


def main() -> None:
    """Build comparable probability polygons for three values of p."""
    n = 10
    values = list(range(n + 1))
    probabilities = (0.2, 0.5, 0.8)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
        }
    )
    figure, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), sharey=True)

    for axis, probability in zip(axes, probabilities, strict=True):
        masses = [
            binomial_probability(n, value, probability) for value in values
        ]
        axis.vlines(values, 0, masses, color="#24758c", linewidth=1.8)
        axis.plot(
            values,
            masses,
            "o-",
            color="#24758c",
            markerfacecolor="white",
            markeredgewidth=1.5,
            linewidth=1.2,
        )
        axis.set_title(f"p = {str(probability).replace('.', ',')}")
        axis.set_xlabel("Число успехов m")
        axis.set_xticks(range(0, n + 1, 2))
        axis.set_xlim(-0.5, n + 0.5)
        axis.grid(axis="y", color="#d9e2e6", linewidth=0.7)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Вероятность P(X = m)")
    figure.suptitle("Биномиальное распределение при n = 10", y=1.02)
    figure.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
