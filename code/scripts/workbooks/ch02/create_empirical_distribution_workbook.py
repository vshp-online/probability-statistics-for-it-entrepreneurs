"""Create the LibreOffice Calc workbook for an empirical distribution.

Run from the repository root:
    python code/scripts/workbooks/ch02/create_empirical_distribution_workbook.py
"""

from __future__ import annotations

import csv
from math import ceil, log2, sqrt
from pathlib import Path
from shutil import which
from statistics import mean, median, multimode, stdev, variance
from subprocess import run
from tempfile import TemporaryDirectory

import xlsxwriter


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "code/data/order-processing-times.csv"
OUTPUT = ROOT / "code/data/empirical-distribution-calc.ods"


def load_values() -> list[float]:
    """Read the observations shared by Calc and Python examples."""
    with DATA.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return [float(row["processing_time_seconds"]) for row in reader]


VALUES = load_values()


def percentile_inc(values: list[float], probability: float) -> float:
    """Return a linearly interpolated inclusive percentile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = position - lower_index
    return (
        ordered[lower_index] * (1 - fraction)
        + ordered[upper_index] * fraction
    )


def descriptive_statistics() -> dict[str, float]:
    """Calculate cached values matching the formulas used in Calc."""
    count = len(VALUES)
    average = mean(VALUES)
    sample_standard_deviation = stdev(VALUES)
    centered = [value - average for value in VALUES]
    standardized = [
        difference / sample_standard_deviation for difference in centered
    ]
    skewness = (
        count
        / ((count - 1) * (count - 2))
        * sum(value**3 for value in standardized)
    )
    excess = (
        count
        * (count + 1)
        / ((count - 1) * (count - 2) * (count - 3))
        * sum(value**4 for value in standardized)
        - 3 * (count - 1) ** 2 / ((count - 2) * (count - 3))
    )
    first_quartile = percentile_inc(VALUES, 0.25)
    third_quartile = percentile_inc(VALUES, 0.75)
    return {
        "count": count,
        "sum": sum(VALUES),
        "mean": average,
        "median": median(VALUES),
        "mode": multimode(VALUES)[0],
        "q1": first_quartile,
        "q3": third_quartile,
        "iqr": third_quartile - first_quartile,
        "min": min(VALUES),
        "max": max(VALUES),
        "range": max(VALUES) - min(VALUES),
        "variance": variance(VALUES),
        "standard_deviation": sample_standard_deviation,
        "standard_error": sample_standard_deviation / sqrt(count),
        "coefficient_of_variation": sample_standard_deviation / average,
        "skewness": skewness,
        "excess": excess,
    }


def distribution_rows() -> list[tuple[float, float, float, int, float, float]]:
    """Return grouped intervals and their frequencies."""
    interval_count = ceil(1 + log2(len(VALUES)))
    lower_bound = min(VALUES)
    width = ceil(((max(VALUES) - lower_bound) / interval_count) * 2) / 2
    rows = []
    cumulative = 0
    for index in range(interval_count):
        lower = lower_bound + index * width
        upper = lower + width
        if index < interval_count - 1:
            frequency = sum(lower <= value < upper for value in VALUES)
        else:
            frequency = sum(lower <= value <= upper for value in VALUES)
        relative = frequency / len(VALUES)
        cumulative += frequency
        rows.append(
            (
                lower,
                upper,
                (lower + upper) / 2,
                frequency,
                relative,
                cumulative / len(VALUES),
            )
        )
    return rows


def formats(workbook: xlsxwriter.Workbook) -> dict[str, xlsxwriter.format.Format]:
    """Create the shared workbook formats."""
    return {
        "title": workbook.add_format(
            {
                "bold": True,
                "font_size": 16,
                "font_color": "#1F4E5F",
                "align": "left",
                "valign": "vcenter",
            }
        ),
        "subtitle": workbook.add_format(
            {
                "font_size": 10,
                "font_color": "#4A5A60",
                "text_wrap": True,
                "valign": "top",
            }
        ),
        "header": workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D9EAF0",
                "border": 1,
                "border_color": "#8A9BA1",
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
            }
        ),
        "input": workbook.add_format(
            {
                "bg_color": "#FFF4CC",
                "border": 1,
                "border_color": "#D2C27B",
                "num_format": "0.0",
            }
        ),
        "label": workbook.add_format(
            {
                "bg_color": "#E8F1E2",
                "border": 1,
                "border_color": "#9EB493",
            }
        ),
        "number": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.0"}
        ),
        "number2": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.00"}
        ),
        "number3": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.000"}
        ),
        "number4": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.0000"}
        ),
        "integer": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0"}
        ),
        "percent": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.0%"}
        ),
        "percent2": workbook.add_format(
            {"border": 1, "border_color": "#B7C1C5", "num_format": "0.00%"}
        ),
        "unit": workbook.add_format(
            {
                "border": 1,
                "border_color": "#B7C1C5",
                "align": "center",
                "valign": "vcenter",
            }
        ),
        "text": workbook.add_format(
            {
                "border": 1,
                "border_color": "#B7C1C5",
                "align": "left",
                "valign": "vcenter",
            }
        ),
        "note": workbook.add_format(
            {
                "italic": True,
                "font_color": "#4A5A60",
                "text_wrap": True,
                "valign": "top",
            }
        ),
    }


def write_data_sheet(
    workbook: xlsxwriter.Workbook,
    workbook_formats: dict[str, xlsxwriter.format.Format],
) -> None:
    """Write the editable source observations."""
    worksheet = workbook.add_worksheet("Данные")
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(2, 0)
    worksheet.set_column("A:A", 12)
    worksheet.set_column("B:B", 24)
    worksheet.set_column("C:C", 42)
    worksheet.set_row(0, 28)
    worksheet.merge_range(
        "A1:C1", "Время обработки заказов", workbook_formats["title"]
    )
    worksheet.merge_range(
        "A2:C2",
        "Жёлтые ячейки — исходные наблюдения. Значения указаны в секундах.",
        workbook_formats["subtitle"],
    )
    worksheet.write_row(
        "A3",
        ["Наблюдение", "Время, с", "Комментарий"],
        workbook_formats["header"],
    )
    for row_number, value in enumerate(VALUES, start=4):
        worksheet.write_number(
            row_number - 1,
            0,
            row_number - 3,
            workbook_formats["integer"],
        )
        worksheet.write_number(
            row_number - 1,
            1,
            value,
            workbook_formats["input"],
        )
        worksheet.write_blank(
            row_number - 1,
            2,
            None,
            workbook_formats["number"],
        )


# A single function keeps the sheet geometry, formula ranges, and chart ranges together.
# pylint: disable=too-many-locals,too-many-statements
def write_distribution_sheet(
    workbook: xlsxwriter.Workbook,
    workbook_formats: dict[str, xlsxwriter.format.Format],
) -> None:
    """Write formulas, grouped frequencies, and native charts."""
    worksheet = workbook.add_worksheet("Распределение")
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(10, 0)
    worksheet.set_landscape()
    worksheet.set_paper(9)
    worksheet.fit_to_pages(1, 2)
    worksheet.set_margins(0.35, 0.35, 0.45, 0.45)
    worksheet.set_h_pagebreaks([25])
    worksheet.print_area("A1:N43")
    worksheet.set_column("A:B", 14)
    worksheet.set_column("C:C", 16)
    worksheet.set_column("D:F", 18)
    worksheet.set_column("G:N", 11)
    worksheet.set_row(0, 28)
    worksheet.merge_range(
        "A1:N1",
        "Эмпирическое распределение времени обработки заказов",
        workbook_formats["title"],
    )
    worksheet.merge_range(
        "A2:N2",
        (
            "Расчёты выполняются формулами по листу «Данные». "
            "Замените наблюдения и при необходимости скорректируйте число интервалов."
        ),
        workbook_formats["subtitle"],
    )

    summary = [
        ("Число наблюдений", "=COUNT('Данные'!$B$4:$B$123)", len(VALUES)),
        ("Минимум, с", "=MIN('Данные'!$B$4:$B$123)", min(VALUES)),
        ("Максимум, с", "=MAX('Данные'!$B$4:$B$123)", max(VALUES)),
        (
            "Число интервалов",
            "=ROUNDUP(1+LOG(B3,2),0)",
            ceil(1 + log2(len(VALUES))),
        ),
        (
            "Ширина интервала, с",
            "=ROUNDUP((B5-B4)/B6*2,0)/2",
            3.5,
        ),
    ]
    for row_number, (label, formula, cached_value) in enumerate(
        summary, start=3
    ):
        worksheet.write(row_number - 1, 0, label, workbook_formats["label"])
        value_format = (
            workbook_formats["integer"]
            if row_number in (3, 6)
            else workbook_formats["number"]
        )
        worksheet.write_formula(
            row_number - 1,
            1,
            formula,
            value_format,
            cached_value,
        )

    worksheet.write_row(
        "A11",
        [
            "Нижняя граница",
            "Верхняя граница",
            "Середина",
            "Частота",
            "Частость",
            "Накопленная частость",
        ],
        workbook_formats["header"],
    )

    rows = distribution_rows()
    for index, row_values in enumerate(rows, start=12):
        lower, upper, midpoint, frequency, relative, cumulative = row_values
        source_row = index
        if index == 12:
            lower_formula = "=$B$4"
            frequency_formula = (
                "=COUNTIFS('Данные'!$B$4:$B$123,\">=\"&A12,"
                "'Данные'!$B$4:$B$123,\"<\"&B12)"
            )
        else:
            lower_formula = f"=B{source_row - 1}"
            comparison = "<=" if index == 19 else "<"
            frequency_formula = (
                "=COUNTIFS('Данные'!$B$4:$B$123,\">=\"&"
                f"A{source_row},'Данные'!$B$4:$B$123,\"{comparison}\"&"
                f"B{source_row})"
            )
        formulas = (
            (0, lower_formula, lower, workbook_formats["number"]),
            (
                1,
                f"=A{source_row}+$B$7",
                upper,
                workbook_formats["number"],
            ),
            (
                2,
                f"=(A{source_row}+B{source_row})/2",
                midpoint,
                workbook_formats["number"],
            ),
            (
                3,
                frequency_formula,
                frequency,
                workbook_formats["integer"],
            ),
            (
                4,
                f"=D{source_row}/$B$3",
                relative,
                workbook_formats["percent"],
            ),
            (
                5,
                f"=SUM($E$12:E{source_row})",
                cumulative,
                workbook_formats["percent"],
            ),
        )
        for column, formula, cached_value, cell_format in formulas:
            worksheet.write_formula(
                index - 1,
                column,
                formula,
                cell_format,
                cached_value,
            )

    worksheet.write(
        "A21", "Контроль суммы частот", workbook_formats["label"]
    )
    worksheet.write_formula(
        "B21",
        "=SUM(D12:D19)",
        workbook_formats["integer"],
        len(VALUES),
    )
    worksheet.write(
        "A22", "Контроль суммы частостей", workbook_formats["label"]
    )
    worksheet.write_formula(
        "B22", "=SUM(E12:E19)", workbook_formats["percent"], 1
    )

    histogram = workbook.add_chart({"type": "column"})
    histogram.add_series(
        {
            "name": "Частость",
            "categories": "='Распределение'!$C$12:$C$19",
            "values": "='Распределение'!$E$12:$E$19",
            "fill": {"color": "#4B91A8"},
            "border": {"color": "#24758C"},
            "gap": 5,
        }
    )
    histogram.set_title({"name": "Гистограмма времени обработки"})
    histogram.set_x_axis({"name": "Середина интервала, с"})
    histogram.set_y_axis(
        {"name": "Частость", "num_format": "0%", "min": 0, "max": 0.25}
    )
    histogram.set_legend({"none": True})
    histogram.set_style(10)
    worksheet.insert_chart("G10", histogram, {"x_scale": 1.18, "y_scale": 1.05})

    cumulative_chart = workbook.add_chart({"type": "line"})
    cumulative_chart.add_series(
        {
            "name": "Накопленная частость",
            "categories": "='Распределение'!$B$12:$B$19",
            "values": "='Распределение'!$F$12:$F$19",
            "line": {"color": "#24758C", "width": 2.25},
            "marker": {
                "type": "circle",
                "size": 5,
                "border": {"color": "#24758C"},
                "fill": {"color": "#FFFFFF"},
            },
        }
    )
    cumulative_chart.set_title({"name": "Кумулятивная линия"})
    cumulative_chart.set_x_axis({"name": "Верхняя граница интервала, с"})
    cumulative_chart.set_y_axis(
        {
            "name": "Накопленная частость",
            "num_format": "0%",
            "min": 0,
            "max": 1,
            "major_unit": 0.2,
        }
    )
    cumulative_chart.set_legend({"none": True})
    cumulative_chart.set_style(10)
    worksheet.insert_chart(
        "G28", cumulative_chart, {"x_scale": 1.18, "y_scale": 1.05}
    )

    worksheet.merge_range(
        "A25:F27",
        (
            "Кумулятивная линия показывает долю наблюдений, не превышающих "
            "верхнюю границу соответствующего интервала."
        ),
        workbook_formats["note"],
    )


def write_descriptive_statistics_sheet(
    workbook: xlsxwriter.Workbook,
    workbook_formats: dict[str, xlsxwriter.format.Format],
) -> None:
    """Write formula-driven descriptive statistics for the source data."""
    worksheet = workbook.add_worksheet("Характеристики")
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(4, 0)
    worksheet.set_portrait()
    worksheet.set_paper(9)
    worksheet.fit_to_pages(1, 1)
    worksheet.set_margins(0.45, 0.45, 0.5, 0.5)
    worksheet.print_area("A1:D25")
    worksheet.set_column("A:A", 34)
    worksheet.set_column("B:B", 16)
    worksheet.set_column("C:C", 12)
    worksheet.set_column("D:D", 47)
    worksheet.set_row(0, 28)
    worksheet.merge_range(
        "A1:D1",
        "Числовые характеристики времени обработки заказов",
        workbook_formats["title"],
    )
    worksheet.merge_range(
        "A2:D2",
        (
            "Все значения вычисляются по листу «Данные». "
            "Используются выборочные дисперсия и стандартное отклонение."
        ),
        workbook_formats["subtitle"],
    )
    worksheet.write_row(
        "A4",
        ["Показатель", "Значение", "Единица", "Что характеризует"],
        workbook_formats["header"],
    )

    values = descriptive_statistics()
    source = "'Данные'!$B$4:$B$123"
    rows = [
        (
            "Число наблюдений",
            f"=COUNT({source})",
            values["count"],
            workbook_formats["integer"],
            "шт.",
            "Объём выборки",
        ),
        (
            "Сумма",
            f"=SUM({source})",
            values["sum"],
            workbook_formats["number"],
            "с",
            "Суммарное время",
        ),
        (
            "Среднее",
            f"=AVERAGE({source})",
            values["mean"],
            workbook_formats["number2"],
            "с",
            "Средний уровень",
        ),
        (
            "Медиана",
            f"=MEDIAN({source})",
            values["median"],
            workbook_formats["number2"],
            "с",
            "Граница двух равных половин выборки",
        ),
        (
            "Мода",
            f"=MODE({source})",
            values["mode"],
            workbook_formats["number2"],
            "с",
            "Наиболее частое значение",
        ),
        (
            "Первый квартиль",
            f"=QUARTILE.INC({source},1)",
            values["q1"],
            workbook_formats["number3"],
            "с",
            "Не превышают 25% наблюдений",
        ),
        (
            "Третий квартиль",
            f"=QUARTILE.INC({source},3)",
            values["q3"],
            workbook_formats["number3"],
            "с",
            "Не превышают 75% наблюдений",
        ),
        (
            "Межквартильный размах",
            "=B11-B10",
            values["iqr"],
            workbook_formats["number3"],
            "с",
            "Разброс центральных 50% наблюдений",
        ),
        (
            "Минимум",
            f"=MIN({source})",
            values["min"],
            workbook_formats["number"],
            "с",
            "Наименьшее наблюдение",
        ),
        (
            "Максимум",
            f"=MAX({source})",
            values["max"],
            workbook_formats["number"],
            "с",
            "Наибольшее наблюдение",
        ),
        (
            "Размах",
            "=B14-B13",
            values["range"],
            workbook_formats["number"],
            "с",
            "Полный диапазон наблюдений",
        ),
        (
            "Выборочная дисперсия",
            f"=VAR.S({source})",
            values["variance"],
            workbook_formats["number4"],
            "с²",
            "Средний квадрат отклонения с поправкой",
        ),
        (
            "Выборочное стандартное отклонение",
            f"=STDEV.S({source})",
            values["standard_deviation"],
            workbook_formats["number4"],
            "с",
            "Типичный масштаб отклонения от среднего",
        ),
        (
            "Стандартная ошибка среднего",
            f"=STDEV.S({source})/SQRT(COUNT({source}))",
            values["standard_error"],
            workbook_formats["number4"],
            "с",
            "Точность оценки среднего",
        ),
        (
            "Коэффициент вариации",
            "=B17/B7",
            values["coefficient_of_variation"],
            workbook_formats["percent2"],
            "%",
            "Относительный разброс",
        ),
        (
            "Асимметрия",
            f"=SKEW({source})",
            values["skewness"],
            workbook_formats["number4"],
            "—",
            "Направление и выраженность асимметрии",
        ),
        (
            "Эксцесс",
            f"=KURT({source})",
            values["excess"],
            workbook_formats["number4"],
            "—",
            "Форма относительно нормального распределения",
        ),
    ]
    for row_number, (
        label,
        formula,
        cached_value,
        value_format,
        unit,
        meaning,
    ) in enumerate(rows, start=5):
        worksheet.write(row_number - 1, 0, label, workbook_formats["label"])
        worksheet.write_formula(
            row_number - 1,
            1,
            formula,
            value_format,
            cached_value,
        )
        worksheet.write(
            row_number - 1,
            2,
            unit,
            workbook_formats["unit"],
        )
        worksheet.write(
            row_number - 1,
            3,
            meaning,
            workbook_formats["text"],
        )

    worksheet.merge_range(
        "A23:D25",
        (
            "Стандартная ошибка среднего не является стандартным отклонением "
            "наблюдений. Доверительные интервалы требуют дополнительных "
            "предпосылок и рассматриваются отдельно в части о статистическом "
            "оценивании."
        ),
        workbook_formats["note"],
    )


def build_xlsx(path: Path) -> None:
    """Build the intermediate workbook with formulas and native charts."""
    workbook = xlsxwriter.Workbook(path)
    workbook_formats = formats(workbook)
    write_data_sheet(workbook, workbook_formats)
    write_distribution_sheet(workbook, workbook_formats)
    write_descriptive_statistics_sheet(workbook, workbook_formats)
    workbook.close()


def convert_to_ods(source: Path, output_directory: Path) -> Path:
    """Convert the intermediate XLSX to ODS through LibreOffice."""
    soffice = which("soffice")
    if not soffice:
        raise RuntimeError("LibreOffice soffice is not available")
    profile = output_directory / "lo-profile"
    profile.mkdir()
    run(
        [
            soffice,
            "--headless",
            f"-env:UserInstallation=file://{profile}",
            "--convert-to",
            "ods",
            "--outdir",
            str(output_directory),
            str(source),
        ],
        check=True,
    )
    return output_directory / f"{source.stem}.ods"


def main() -> None:
    """Create and save the final ODS workbook."""
    (ROOT / "tmp").mkdir(exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=ROOT / "tmp") as temporary:
        temporary_directory = Path(temporary)
        source = temporary_directory / "empirical-distribution-calc.xlsx"
        build_xlsx(source)
        converted = convert_to_ods(source, temporary_directory)
        converted.replace(OUTPUT)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
