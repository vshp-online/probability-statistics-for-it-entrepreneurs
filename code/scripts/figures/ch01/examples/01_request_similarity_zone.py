# pylint: disable=invalid-name,missing-module-docstring,wrong-import-position,unused-import,line-too-long
meta = {
    "title": "Область временной близости запросов |t₁ - t₂| < 0,2",
    "book_ref": "Пример 1.9 / Рисунок 1.1",
    "description": "Графическая иллюстрация событий, при которых два запроса t₁ и t₂ поступают с разницей менее 0.2 сек. по шкале времени. Используется для анализа сессий и совпадений запросов.",
    "authors": [
        {"name": "П.С. Ткачев", "email": "p.tkachev@vshp.online"}
    ]
}

import numpy as np

def draw(ax):
    """Строит график на переданной оси."""
    x = np.linspace(0, 1, 500)
    X, Y = np.meshgrid(x, x)
    region = np.abs(X - Y) < 0.2

    ax.contourf(X, Y, region, levels=[0.5, 1], colors=['lightblue'])
    ax.plot([0, 1], [0, 1], 'k--', label='t₁ = t₂')

    ax.set_xlabel('t₁')
    ax.set_ylabel('t₂')
    ax.set_title('Область |t₁ - t₂| < 0,2')
    ax.legend()
    ax.grid(True)
