#!/usr/bin/env python3
"""Build a lightweight XLSX demo workbook from the mock reconciliation outputs."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "mock"
OUTPUTS = ROOT / "outputs"
WORKBOOK = OUTPUTS / "stock_return_reconciliation_demo.xlsx"


def read_csv(path: Path) -> list[list[object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [list(row) for row in csv.reader(handle)]


def read_dict_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cell_ref(row: int, col: int) -> str:
    letters = ""
    while col:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"


def value_cell(row: int, col: int, value: object) -> str:
    ref = cell_ref(row, col)
    if value is None or value == "":
        return f'<c r="{ref}"/>'
    try:
        if isinstance(value, str) and not value.strip():
            raise ValueError
        number = float(value)
    except (TypeError, ValueError):
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
    return f'<c r="{ref}"><v>{number}</v></c>'


def sheet_xml(rows: list[list[object]]) -> str:
    row_xml = []
    for row_index, row in enumerate(rows, start=1):
        cells = "".join(value_cell(row_index, col_index, value) for col_index, value in enumerate(row, start=1))
        row_xml.append(f'<row r="{row_index}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>"
        + "".join(row_xml)
        + "</sheetData></worksheet>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets></workbook>"
    )


def workbook_rels(sheet_names: list[str]) -> str:
    rels = "".join(
        f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        for index, _ in enumerate(sheet_names, start=1)
    )
    rels += (
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + rels
        + "</Relationships>"
    )


def content_types(sheet_names: list[str]) -> str:
    overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index, _ in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + overrides
        + "</Types>"
    )


def root_rels() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<fonts count=\"1\"><font><sz val=\"11\"/><name val=\"Calibri\"/></font></fonts>"
        "<fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>"
        "<borders count=\"1\"><border/></borders>"
        "<cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"
        "<cellXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/></cellXfs>"
        "</styleSheet>"
    )


def build_sheets() -> dict[str, list[list[object]]]:
    summary = json.loads((OUTPUTS / "reconciliation-summary.json").read_text(encoding="utf-8"))
    candidates = read_csv(OUTPUTS / "return-candidates.csv")
    transactions = read_csv(DATA / "transactions.csv")
    positions = read_csv(DATA / "positions_snapshot.csv")

    dashboard = [
        ["Stock Return Reconciliation Demo"],
        ["Status", summary["status"]],
        ["As of", summary["as_of"]],
        ["Base currency", summary["base_currency"]],
        ["Positions checked", summary["positions_checked"]],
        ["Unresolved count", summary["unresolved_count"]],
        ["Closest candidate", summary["closest_candidate"]],
        ["Net cash contributed KRW", summary["net_cash_contributed_krw"]],
        ["App total P&L KRW", summary["app_total_pnl_krw"]],
        ["Sample-basis calculated difference KRW", summary["recalculated_total_pnl_krw"]],
        ["Return on contributed cash %", summary["return_on_contributed_cash_pct"]],
        ["Difference vs app KRW", summary["difference_vs_app_krw"]],
        ["Security P&L basis", summary["security_pnl_basis"]],
        ["Annualized XIRR note", summary["annualized_xirr_note"]],
        ["Boundary", "Not investment, tax, legal, accounting, or trading advice"],
    ]
    checks = [
        ["Check", "Result"],
        ["Workbook generated from mock data", "Pass"],
        ["Required reconciliation outputs exist", "Pass"],
        ["Unresolved positions", summary["unresolved_count"]],
        ["Safety boundary note present", "Pass" if summary["safety_boundary_note_present"] else "Break"],
    ]
    return {
        "Dashboard": dashboard,
        "Transactions": transactions,
        "Positions": positions,
        "Return Candidates": candidates,
        "Checks": checks,
    }


def main() -> int:
    OUTPUTS.mkdir(exist_ok=True)
    sheets = build_sheets()
    sheet_names = list(sheets)
    with zipfile.ZipFile(WORKBOOK, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types(sheet_names))
        archive.writestr("_rels/.rels", root_rels())
        archive.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels(sheet_names))
        archive.writestr("xl/styles.xml", styles_xml())
        for index, name in enumerate(sheet_names, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", sheet_xml(sheets[name]))
    print(f"Generated {WORKBOOK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
