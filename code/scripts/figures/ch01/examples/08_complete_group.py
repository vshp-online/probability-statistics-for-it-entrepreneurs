"""Диаграмма полной группы несовместных событий."""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects

meta = {
    "title": "Полная группа событий",
    "book_ref": "Раздел 2.3 / Рисунок 2.2",
    "description": "Диаграмма полной группы несовместных событий A₁, A₂ и A₃",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"},
        {"name": "Н.Н. Зубов", "email": "nick-work@bk.ru"},
    ],
}


def draw(ax):
    """Рисует разбиение пространства элементарных исходов на три события."""
    formula_box = {'facecolor': 'white', 'edgecolor': 'none', 'pad': 6}
    colors = ['#D8EAF2', '#E6EFD9', '#F5E5C8']
    labels = ['A₁', 'A₂', 'A₃']

    for index, (color, label) in enumerate(zip(colors, labels)):
        ax.add_patch(Rectangle((2 * index, 0), 2, 4, facecolor=color, edgecolor='black'))
        text = ax.text(2 * index + 1, 2.1, label, ha='center', va='center', fontsize=18, fontstyle='italic')
        text.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    ax.text(
        3,
        0.5,
        'A₁ ∪ A₂ ∪ A₃ = Ω',
        ha='center',
        va='center',
        fontsize=14,
        fontstyle='italic',
        bbox=formula_box,
    )
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
