"""Создаёт параметрическую обложку книги в стилистике графика Matplotlib.

Запускать из корня репозитория:
    python3 code/scripts/figures/generate_cover.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "book" / "images" / "cover-vshp-matplotlib.png"
PDF_OUTPUT = ROOT / "book" / "images" / "cover-vshp-matplotlib.pdf"

# Цвет взят из официального SVG щита ВШП:
# https://api.vshp.online/system/press_kit/item/20/VSHP_SHIELD_ORIGINAL.svg
VSHP_MAROON = "#8D282E"
BACKGROUND = "#F7F2EC"
INK = "#292221"
GRID = "#CEB9B4"
MARK = "#E8D1CB"

SHIELD_EDITOR_POINTS = {
    "H": (400.00, 700.00),
    "c1a": (358.92, 659.73),
    "c1b": (305.38, 644.86),
    "J1": (253.30, 629.99),
    "c2a": (179.58, 609.31),
    "c2b": (109.90, 589.36),
    "F": (100.00, 462.03),
    "c3a": (143.64, 500.48),
    "c3b": (191.82, 506.18),
    "J2": (246.47, 516.69),
    "c4a": (309.72, 528.86),
    "c4b": (366.63, 556.71),
    "G": (400.00, 600.00),
    "c5a": (379.55, 468.83),
    "c5b": (305.38, 446.35),
    "J3": (233.40, 423.49),
    "c6a": (175.09, 404.96),
    "c6b": (118.89, 381.81),
    "D": (100.00, 266.14),
    "c7a": (143.64, 304.59),
    "c7b": (187.49, 322.48),
    "J4": (252.66, 329.29),
    "c8a": (314.37, 335.75),
    "c8b": (366.63, 360.82),
    "E": (400.00, 400.00),
    "c9a": (379.55, 268.95),
    "c9b": (305.38, 247.07),
    "J5": (233.40, 225.55),
    "c10a": (175.09, 208.12),
    "c10b": (118.89, 206.97),
    "A": (100.00, 100.00),
    "c11a": (145.48, 124.30),
    "c11b": (181.05, 124.67),
    "J6": (218.46, 125.03),
    "c12a": (274.21, 125.39),
    "c12b": (331.78, 126.12),
    "B": (400.00, 200.00),
    "c13a": (468.22, 125.76),
    "c13b": (525.79, 125.39),
    "J7": (581.54, 125.03),
    "c14a": (618.95, 124.67),
    "c14b": (654.52, 124.30),
    "C": (700.00, 100.00),
    "R": (700.00, 504.47),
    "c15a": (690.10, 589.36),
    "c15b": (620.42, 608.95),
    "J8": (546.70, 629.99),
    "c16a": (494.99, 644.50),
    "c16b": (441.44, 659.73),
    "HN": (403.67, 698.55),
}

SHIELD_CUBIC_SEGMENTS = (
    ("c1a", "c1b", "J1"),
    ("c2a", "c2b", "F"),
    ("c3a", "c3b", "J2"),
    ("c4a", "c4b", "G"),
    ("c5a", "c5b", "J3"),
    ("c6a", "c6b", "D"),
    ("c7a", "c7b", "J4"),
    ("c8a", "c8b", "E"),
    ("c9a", "c9b", "J5"),
    ("c10a", "c10b", "A"),
    ("c11a", "c11b", "J6"),
    ("c12a", "c12b", "B"),
    ("c13a", "c13b", "J7"),
    ("c14a", "c14b", "C"),
)

SMOOTH_JOINS = {
    "J1": ("c1b", "c2a"),
    "J2": ("c3b", "c4a"),
    "J3": ("c5b", "c6a"),
    "J4": ("c7b", "c8a"),
    "J5": ("c9b", "c10a"),
    "J6": ("c11b", "c12a"),
    "J7": ("c13b", "c14a"),
    "J8": ("c15b", "c16a"),
}


def shield_path_from_editor() -> MplPath:
    """Строит контур из координат интерактивного редактора кривых Безье."""
    editor_points = {
        name: np.array(point, dtype=float)
        for name, point in SHIELD_EDITOR_POINTS.items()
    }

    for join_name, (incoming_name, outgoing_name) in SMOOTH_JOINS.items():
        join = editor_points[join_name]
        incoming = editor_points[incoming_name] - join
        outgoing = editor_points[outgoing_name] - join
        cross_product = incoming[0] * outgoing[1] - incoming[1] * outgoing[0]
        scale = np.linalg.norm(incoming) * np.linalg.norm(outgoing)
        # Координаты редактора передаются с округлением до сотых, поэтому
        # допускается расхождение направлений менее 0,35 градуса.
        if (
            scale == 0
            or abs(cross_product) > 6e-3 * scale
            or np.dot(incoming, outgoing) >= 0
        ):
            raise ValueError(f"Стык {join_name} утратил гладкость")

    def to_plot(point_name: str) -> tuple[float, float]:
        x, y = editor_points[point_name]
        return ((x - 400.0) / 100.0, (400.0 - y) / 100.0)

    vertices = [to_plot("H")]
    codes = [MplPath.MOVETO]
    for control_1, control_2, endpoint in SHIELD_CUBIC_SEGMENTS:
        vertices.extend(
            (to_plot(control_1), to_plot(control_2), to_plot(endpoint))
        )
        codes.extend((MplPath.CURVE4,) * 3)

    vertices.append(to_plot("R"))
    codes.append(MplPath.LINETO)
    for control_1, control_2, endpoint in (
        ("c15a", "c15b", "J8"),
        ("c16a", "c16b", "HN"),
    ):
        vertices.extend(
            (to_plot(control_1), to_plot(control_2), to_plot(endpoint))
        )
        codes.extend((MplPath.CURVE4,) * 3)

    vertices.append(to_plot("H"))
    codes.append(MplPath.CLOSEPOLY)
    return MplPath(vertices, codes)


def add_shield(axis) -> None:
    """Строит адаптированный контур щита по отредактированным кривым Безье."""
    shield_path = shield_path_from_editor()
    shield = PathPatch(
        shield_path,
        facecolor=VSHP_MAROON,
        edgecolor=VSHP_MAROON,
        linewidth=1.2,
        joinstyle="miter",
        zorder=3,
    )
    axis.add_patch(shield)

    grid_lines = []
    for coordinate in np.arange(-4, 4.5, 1):
        grid_lines.append(((coordinate, -4.3), (coordinate, 4.5)))
        grid_lines.append(((-3.8, coordinate), (3.8, coordinate)))

    shield_grid = LineCollection(
        grid_lines,
        colors=MARK,
        linewidths=0.8,
        alpha=0.65,
        zorder=4,
        clip_path=shield,
    )
    axis.add_collection(shield_grid)


def make_cover() -> None:
    """Собирает A4-обложку и сохраняет её в разрешении для печати."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    figure = plt.figure(figsize=(8.27, 11.69), facecolor=BACKGROUND)
    axis = figure.add_axes((0.10, 0.16, 0.80, 0.45), facecolor=BACKGROUND)
    axis.set_xlim(-4.25, 4.25)
    axis.set_ylim(-4.5, 5.0)
    axis.set_aspect("equal")
    axis.set_axisbelow(True)
    axis.set_xticks(np.arange(-4, 5, 1))
    axis.set_yticks(np.arange(-4, 6, 1))
    axis.grid(color=GRID, linewidth=0.75)
    axis.tick_params(colors="#786C68", labelsize=10, length=3, pad=5)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_position("zero")
    axis.spines["bottom"].set_position("zero")
    axis.spines["left"].set_color("#9B8984")
    axis.spines["bottom"].set_color("#9B8984")
    axis.spines["left"].set_linewidth(0.9)
    axis.spines["bottom"].set_linewidth(0.9)
    axis.annotate(
        "t, период наблюдения",
        xy=(4.18, 0),
        xytext=(4.45, 0.2),
        color="#786C68",
        fontsize=10,
        ha="left",
        va="bottom",
        rotation=90,
    )
    axis.annotate(
        "p, вероятность",
        xy=(0, 4.85),
        xytext=(0.22, 5.15),
        color="#786C68",
        fontsize=10,
        ha="left",
        va="bottom",
    )
    axis.text(
        -4.15,
        -4.35,
        "1 клетка = 1 усл. ед.",
        color="#9B8984",
        fontsize=9.5,
        ha="left",
        va="bottom",
    )
    add_shield(axis)

    figure.text(
        0.12,
        0.925,
        "ВЫСШАЯ ШКОЛА ПРЕДПРИНИМАТЕЛЬСТВА",
        color=VSHP_MAROON,
        fontsize=13,
        fontweight="bold",
        ha="left",
        va="top",
    )
    figure.lines.append(
        plt.Line2D(
            [0.12, 0.88],
            [0.900, 0.900],
            color=VSHP_MAROON,
            linewidth=1.1,
            transform=figure.transFigure,
        )
    )
    figure.text(
        0.12,
        0.855,
        "ТЕОРИЯ ВЕРОЯТНОСТЕЙ\nИ МАТЕМАТИЧЕСКАЯ\nСТАТИСТИКА",
        color=INK,
        fontsize=25,
        fontweight="bold",
        linespacing=1.07,
        ha="left",
        va="top",
    )
    figure.text(
        0.12,
        0.705,
        "для начинающих\nIT-предпринимателей",
        color=VSHP_MAROON,
        fontsize=19,
        linespacing=1.1,
        ha="left",
        va="top",
    )
    figure.text(
        0.12,
        0.095,
        "Н.Н. Зубов · П.С. Ткачев · С.З. Умаров\nПод редакцией П.С. Ткачева",
        color=INK,
        fontsize=13,
        linespacing=1.5,
        ha="left",
        va="bottom",
    )
    figure.text(
        0.88,
        0.095,
        "2026",
        color=VSHP_MAROON,
        fontsize=14,
        ha="right",
        va="bottom",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=300, facecolor=BACKGROUND)
    figure.savefig(PDF_OUTPUT, facecolor=BACKGROUND)
    plt.close(figure)
    print(OUTPUT.relative_to(ROOT))
    print(PDF_OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    make_cover()
