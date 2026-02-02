# pylint: disable=invalid-name,missing-module-docstring,wrong-import-position,unused-import,line-too-long,missing-function-docstring,duplicate-code,no-else-return
meta = {
    "title": "Сумма событий A и B",
    "book_ref": "Пример 1.15 / Рисунок 1.4",
    "description": "Пример диаграммы Венна для суммы событий A и B",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"},
        {"name": "Н.Н. Зубов", "email": "nick-work@bk.ru"}
    ]
}

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch
import matplotlib.patheffects as path_effects
from matplotlib.path import Path
from shapely.geometry import Point
from shapely.affinity import scale, translate
from shapely.ops import unary_union

def ellipse_as_shapely(x, y, width, height):
    circle = Point(0, 0).buffer(1, resolution=256)
    ellipse = scale(circle, width / 2, height / 2)
    ellipse = translate(ellipse, xoff=x, yoff=y)
    return ellipse

def shape_to_patch(shape, **kwargs):
    if shape.geom_type == 'Polygon':
        coords = shape.exterior.coords[:]
        path = Path(coords, [Path.MOVETO] + [Path.LINETO]*(len(coords)-2) + [Path.CLOSEPOLY])
        return PathPatch(path, **kwargs)
    elif shape.geom_type == 'MultiPolygon':
        return [shape_to_patch(geom, **kwargs) for geom in shape.geoms]
    else:
        raise ValueError("Unsupported geometry")

def draw(ax):
    """Диаграмма: сумма событий A и B с видимыми границами и заливкой объединения."""
    ax.add_patch(Rectangle((0, 0), 6, 4, edgecolor='black', facecolor='white'))

    a = ellipse_as_shapely(2, 2, 3, 2)
    b = ellipse_as_shapely(4, 2, 3, 2)
    u = unary_union([a, b])

    # Заливка объединения
    patch = shape_to_patch(u, facecolor='lightblue', edgecolor='none')
    if isinstance(patch, list):
        for p in patch:
            ax.add_patch(p)
    else:
        ax.add_patch(patch)

    # Контуры A и B
    for shape in [a, b]:
        contour = shape_to_patch(shape, facecolor='none', edgecolor='black')
        ax.add_patch(contour)

    # Подписи
    for label, x in [('A', 2.0), ('B', 4.0)]:
        text = ax.text(x, 2, label, ha='center', va='center', fontsize=18, fontstyle='italic')
        text.set_path_effects([path_effects.Stroke(linewidth=4, foreground='white'), path_effects.Normal()])

    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
