"""
Утилиты для сохранения графиков matplotlib (файл изображения, путь, DPI и др.).
"""

import os
import matplotlib.pyplot as plt

def get_image_filename(script_path: str, ext: str = 'png') -> str:
    """
    Возвращает имя файла изображения по имени скрипта.
    Например: 'venn_diagram.py' -> 'venn_diagram.png'
    """
    base = os.path.splitext(os.path.basename(script_path))[0]
    return f"{base}.{ext}"

def save_figure(filename: str,
                directory: str = 'figures',
                dpi: int = 300,
                pad_inches: float = 0.05,
                save: bool = True,
                show: bool = False,
                close: bool = True) -> None:
    """
    Универсальная функция для сохранения matplotlib-графиков с обрезкой полей.

    :param filename: Имя сохраняемого файла
    :param directory: Папка для сохранения
    :param dpi: Разрешение
    :param pad_inches: Отступы по краям
    :param save: Сохранять график
    :param show: Показывать график после сохранения
    :param close: Закрывать график после сохранения
    """

    if save:
        if not os.path.exists(directory):
            os.makedirs(directory)
        full_path = os.path.join(directory, filename)
        plt.savefig(full_path, dpi=dpi, bbox_inches='tight', pad_inches=pad_inches)
        print(f"[✔] Сохранено: {full_path}")
    elif show:
        plt.show()
    elif close:
        plt.close()

def run_example(draw_fn, filename, save=True, show=False, directory='figures'):
    """Создаёт фигуру, вызывает draw_fn(ax), затем сохраняет или показывает график."""
    fig, ax = plt.subplots(figsize=(6, 6))
    draw_fn(ax)
    save_figure(filename, directory=directory, save=save, show=show)
