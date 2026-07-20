# pylint: disable=invalid-name,missing-module-docstring,wrong-import-position,unused-import,line-too-long
meta = {
    "title": "Событие A и противоположное событие Ā",
    "book_ref": "Раздел 1.2 / Рисунок 1.2",
    "description": "Диаграмма Венна для противоположных событий A и Ā",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"},
        {"name": "Н.Н. Зубов", "email": "nick-work@bk.ru"}
    ]
}

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.patheffects as path_effects

def draw(ax):
    """Рисует универсум с явно выделенными A и Ā."""
    ax.add_patch(Rectangle((0, 0), 6, 4, edgecolor='black', facecolor='#E8EEF1', linewidth=1))

    a = Ellipse((3, 2), width=3, height=2, angle=-30, facecolor='lightblue', edgecolor='black')
    ax.add_patch(a)

    text_a = ax.text(3, 2, 'A', ha='center', va='center', fontsize=18, fontstyle='italic')
    text_a.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    text_not_a = ax.text(5.5, 3.5, 'Ā', fontsize=18, fontstyle='italic', ha='center', va='center')
    text_not_a.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
