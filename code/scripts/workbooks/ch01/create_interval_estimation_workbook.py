"""Создаёт рабочую книгу LibreOffice Calc для примера из § 1.6.

Запускать из корня репозитория:
    python3 code/scripts/workbooks/ch01/create_interval_estimation_workbook.py
"""

from __future__ import annotations

from math import asin, sin, sqrt
from pathlib import Path
from statistics import NormalDist
from subprocess import run
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "code/data/interval-estimation-calc.ods"
DATA = [
    ("Поисковая реклама", 1200, 48),
    ("Партнёрский канал", 310, 9),
    ("Email-рассылка", 95, 2),
    ("Тестовый канал", 60, 1),
]


def cell(value: str, style: str = "") -> str:
    style_attr = f' table:style-name="{style}"' if style else ""
    return f'<table:table-cell office:value-type="string"{style_attr}><text:p>{value}</text:p></table:table-cell>'


def number(value: float, style: str = "") -> str:
    style_attr = f' table:style-name="{style}"' if style else ""
    return (
        f'<table:table-cell office:value-type="float" office:value="{value}"{style_attr}>'
        f"<text:p>{value}</text:p></table:table-cell>"
    )


def formula(expression: str, value: float, style: str = "") -> str:
    style_attr = f' table:style-name="{style}"' if style else ""
    return (
        f'<table:table-cell table:formula="of:={expression}" office:value-type="float" '
        f'office:value="{value}"{style_attr}><text:p>{value}</text:p></table:table-cell>'
    )


def row(cells: list[str], style: str = "") -> str:
    style_attr = f' table:style-name="{style}"' if style else ""
    return f"<table:table-row{style_attr}>{''.join(cells)}</table:table-row>"


def student_critical(degrees_of_freedom: int) -> float:
    """Приближённое значение двустороннего t-критерия для alpha = 0,05."""
    z = NormalDist().inv_cdf(0.975)
    nu = degrees_of_freedom
    return (
        z
        + (z**3 + z) / (4 * nu)
        + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * nu**2)
        + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * nu**3)
    )


def calculation_row(row_number: int, channel: str, n: int, m: int) -> str:
    p = m / n
    validity = n * p * (1 - p)
    standard_error = sqrt(p * (1 - p) / n)
    critical = student_critical(n - 1)
    traditional_min = p - critical * standard_error
    traditional_max = p + critical * standard_error
    phi = 2 * asin(sqrt(p))
    phi_error = 1 / sqrt(n)
    phi_min = phi - critical * phi_error
    phi_max = phi + critical * phi_error
    fisher_min = sin(phi_min / 2) ** 2
    fisher_max = sin(phi_max / 2) ** 2
    lower = traditional_min if validity > 5 else fisher_min
    upper = traditional_max if validity > 5 else fisher_max
    ref = f"{row_number}"

    return row(
        [
            cell(channel, "input"),
            number(n, "input"),
            number(m, "input"),
            formula(f"[.C{ref}]/[.B{ref}]", p, "percent"),
            formula(f"[.B{ref}]*[.D{ref}]*(1-[.D{ref}])", validity, "number"),
            formula(f"SQRT([.D{ref}]*(1-[.D{ref}])/[.B{ref}])", standard_error, "number"),
            formula(f"TINV(0.05;[.B{ref}]-1)", critical, "number"),
            formula(f"[.D{ref}]-[.G{ref}]*[.F{ref}]", traditional_min, "percent"),
            formula(f"[.D{ref}]+[.G{ref}]*[.F{ref}]", traditional_max, "percent"),
            formula(f"2*ASIN(SQRT([.D{ref}]))", phi, "number"),
            formula(f"1/SQRT([.B{ref}])", phi_error, "number"),
            formula(f"[.J{ref}]-[.G{ref}]*[.K{ref}]", phi_min, "number"),
            formula(f"[.J{ref}]+[.G{ref}]*[.K{ref}]", phi_max, "number"),
            formula(f"SIN([.L{ref}]/2)^2", fisher_min, "percent"),
            formula(f"SIN([.M{ref}]/2)^2", fisher_max, "percent"),
            cell("Традиц." if validity > 5 else "Фишер", "result"),
            formula(
                f"IF([.E{ref}]>5;[.H{ref}];[.N{ref}])", lower, "percent"
            ),
            formula(
                f"IF([.E{ref}]>5;[.I{ref}];[.O{ref}])", upper, "percent"
            ),
        ]
    )


def make_fods() -> str:
    headers = [
        "Канал",
        "n",
        "m",
        "p*",
        "Критерий применимости",
        "СКО p*",
        "t(0,05)",
        "Нижняя граница: традиц.",
        "Верхняя граница: традиц.",
        "φ",
        "СКО φ",
        "Нижняя граница φ",
        "Верхняя граница φ",
        "Нижняя граница: Фишер",
        "Верхняя граница: Фишер",
        "Метод",
        "Нижн. 95%",
        "Верхн. 95%",
    ]
    widths = ["4.0cm", "1.2cm", "1.2cm", "1.6cm"] + ["2.2cm"] * 11 + ["2.2cm", "2.1cm", "2.1cm"]
    columns = "".join(
        f'<table:table-column table:style-name="col{index}"'
        f'{" table:visibility=\"collapse\"" if 5 <= index <= 15 else ""}/>'
        for index, _ in enumerate(widths, start=1)
    )
    column_styles = "".join(
        f'<style:style style:name="col{index}" style:family="table-column">'
        f'<style:table-column-properties style:column-width="{width}"/>'
        f"</style:style>"
        for index, width in enumerate(widths, start=1)
    )
    data_rows = "".join(
        calculation_row(index, *values) for index, values in enumerate(DATA, start=2)
    )
    header_cells = "".join(cell(header, "header") for header in headers)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:automatic-styles>
    {column_styles}
    <style:style style:name="header-row" style:family="table-row"><style:table-row-properties style:row-height="0.7cm" style:use-optimal-row-height="false"/></style:style>
    <style:style style:name="header" style:family="table-cell"><style:table-cell-properties fo:background-color="#D9EAF0" fo:border="0.06pt solid #6B7A80" style:vertical-align="middle"/><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-weight="bold" fo:font-size="9pt"/></style:style>
    <style:style style:name="input" style:family="table-cell"><style:table-cell-properties fo:background-color="#FFF4CC" fo:border="0.06pt solid #A0A0A0"/></style:style>
    <style:style style:name="number" style:family="table-cell"><style:table-cell-properties fo:border="0.06pt solid #A0A0A0"/><style:text-properties fo:font-size="9pt"/></style:style>
    <style:style style:name="percent" style:family="table-cell" style:data-style-name="percent2"><style:table-cell-properties fo:border="0.06pt solid #A0A0A0"/></style:style>
    <style:style style:name="result" style:family="table-cell"><style:table-cell-properties fo:background-color="#E8F1E2" fo:border="0.06pt solid #A0A0A0"/></style:style>
    <number:percentage-style style:name="percent2"><number:number number:decimal-places="3" number:min-decimal-places="3"/><number:text>%</number:text></number:percentage-style>
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Расчёт">
        {columns}
        {row([header_cells], "header-row")}
        {data_rows}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
'''


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        fods_path = Path(temp_dir) / "interval-estimation-calc.fods"
        fods_path.write_text(make_fods(), encoding="utf-8")
        run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "ods",
                "--outdir",
                str(OUTPUT.parent),
                str(fods_path),
            ],
            check=True,
        )
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
