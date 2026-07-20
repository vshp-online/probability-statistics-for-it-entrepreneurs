# pylint: disable=invalid-name,missing-module-docstring,wrong-import-position,unused-import,line-too-long
meta = {
    "title": "Эквивалентные события A и B",
    "book_ref": "Раздел 1.2 / Рисунок 1.3",
    "description": "Диаграмма Венна для эквивалентных событий A и B",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"},
        {"name": "Н.Н. Зубов", "email": "nick-work@bk.ru"}
    ]
}

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.patheffects as path_effects

def draw(ax):
    """Диаграмма: два полностью совпадающих эллипса A и B."""
    ax.add_patch(Rectangle((0, 0), 6, 4, edgecolor='black', facecolor='white'))

    ellipse = Ellipse((3, 2), width=3.2, height=2, facecolor='lightblue', edgecolor='black')
    ax.add_patch(ellipse)

    text = ax.text(3, 2, 'A = B', ha='center', va='center', fontsize=18, fontstyle='italic')
    text.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
