meta = {
    "title": "Событие A и противоположное событие Ā",
    "book_ref": "Пример 1.13 / Рисунок 1.2",
    "description": "Пример диаграммы Венна для противоположных событий A и Ā",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"},
        {"name": "Н.Н. Зубов", "email": "nick-work@bk.ru"}
    ]
}

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.patheffects as path_effects

def draw(ax):
    """Рисует универсум и множество A."""
    ax.add_patch(Rectangle((0, 0), 6, 4, edgecolor='black', facecolor='white', linewidth=1))

    a = Ellipse((3, 2), width=3, height=2, angle=-30, facecolor='lightblue', edgecolor='black')
    ax.add_patch(a)

    text_a = ax.text(3, 2, 'A', ha='center', va='center', fontsize=18, fontstyle='italic')
    text_a.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    ax.text(5.5, 3.5, 'Ā', fontsize=18, fontstyle='italic')

    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
