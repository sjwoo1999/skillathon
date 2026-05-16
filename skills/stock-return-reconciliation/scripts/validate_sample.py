#!/usr/bin/env python3
"""Validate the stock-return-reconciliation Skillathon sample package."""

from __future__ import annotations

import csv
import json
import re
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = "skills/stock-return-reconciliation"

REQUIRED_FILES = [
    "README.md",
    f"{SKILL_DIR}/SKILL.md",
    f"{SKILL_DIR}/references/data-schema.md",
    f"{SKILL_DIR}/references/return-methodology.md",
    f"{SKILL_DIR}/references/reconciliation-rules.md",
    f"{SKILL_DIR}/references/output-format.md",
    f"{SKILL_DIR}/references/eval-checklist.md",
    f"{SKILL_DIR}/references/troubleshooting.md",
    f"{SKILL_DIR}/references/example-prompts.md",
    f"{SKILL_DIR}/scripts/reconcile_returns.py",
    f"{SKILL_DIR}/scripts/build_demo_workbook.py",
    f"{SKILL_DIR}/scripts/validate_sample.py",
    "data/mock/transactions.csv",
    "data/mock/positions_snapshot.csv",
    "data/mock/app_report.csv",
    "data/mock/cash_ledger.csv",
    "data/mock/dividends.csv",
    "data/mock/fx_rates.csv",
    "outputs/reconciliation-report.md",
    "outputs/return-candidates.csv",
    "outputs/reconciliation-summary.json",
    "outputs/stock_return_reconciliation_demo.xlsx",
]

CSV_COLUMNS = {
    "data/mock/transactions.csv": {
        "date",
        "account",
        "symbol",
        "name",
        "side",
        "quantity",
        "price",
        "currency",
        "fee",
        "tax",
        "settlement_amount",
    },
    "data/mock/positions_snapshot.csv": {
        "as_of",
        "account",
        "symbol",
        "name",
        "quantity",
        "market_price",
        "currency",
        "market_value",
    },
    "data/mock/app_report.csv": {
        "as_of",
        "account",
        "period",
        "app_total_pnl",
        "app_return_pct",
        "currency",
        "app_label",
    },
    "data/mock/cash_ledger.csv": {"date", "account", "type", "currency", "amount", "description"},
    "data/mock/dividends.csv": {"pay_date", "account", "symbol", "gross_amount", "tax", "net_amount", "currency"},
    "data/mock/fx_rates.csv": {"date", "base", "quote", "rate"},
}

OUTPUT_HEADINGS = [
    "## Executive Summary",
    "## Input Files Reviewed",
    "## Calculation Basis",
    "## Reconciliation Table",
    "## Return Candidates",
    "## Difference Drivers",
    "## Data Quality Warnings",
    "## Manual Checks And Skipped Checks",
    "## Limitations",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(api[_-]?key|token|webhook[_-]?url)\s*[:=]\s*['\"]?[A-Za-z0-9_./:-]{12,}", re.I),
    re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9_/+-]+", re.I),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{10,16}\b"),
]

ADVICE_PATTERNS = [
    re.compile(r"\b(buy|sell|hold)\s+(recommendation|signal|advice)\b", re.I),
    re.compile(r"\bshould\s+(buy|sell|hold|rebalance)\b", re.I),
    re.compile(r"\b(consider|start|increase|reduce|add|trim)\s+(buying|selling|adding|reducing|trimming|exposure)\b", re.I),
    re.compile(r"\b(good|bad)\s+(entry|exit)\b", re.I),
    re.compile(r"\b(tax\s+deductible|deductible\s+expense|legal\s+opinion|accounting\s+treatment)\b", re.I),
    re.compile(r"\b(will|likely to|expected to)\s+(rise|fall|outperform|underperform|beat|miss)\b", re.I),
    re.compile(r"\b(price\s*target|undervalued|overvalued)\b", re.I),
    re.compile(r"(매수|매도|보유)\s*(추천|권고)", re.I),
    re.compile(r"(사야|팔아야|리밸런싱해야|목표가)", re.I),
    re.compile(r"(비중을|노출을)\s*(늘려|줄여|확대|축소)", re.I),
    re.compile(r"(세금\s*공제|공제\s*가능|법적\s*의견|회계\s*처리)", re.I),
    re.compile(r"(유망|저평가|고평가)\s*(종목|주식)", re.I),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_required_files() -> list[str]:
    return [f"Missing required file: {rel}" for rel in REQUIRED_FILES if not (ROOT / rel).exists()]


def validate_csv_columns() -> list[str]:
    errors: list[str] = []
    for rel, required in CSV_COLUMNS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = set(reader.fieldnames or [])
        missing = sorted(required - fieldnames)
        if missing:
            errors.append(f"{rel} missing columns: {', '.join(missing)}")
    return errors


def validate_csv_values() -> list[str]:
    errors: list[str] = []
    numeric_columns = {
        "data/mock/transactions.csv": ["quantity", "price", "fee", "tax", "settlement_amount"],
        "data/mock/positions_snapshot.csv": ["quantity", "market_price", "market_value"],
        "data/mock/app_report.csv": ["app_total_pnl", "app_return_pct"],
        "data/mock/cash_ledger.csv": ["amount"],
        "data/mock/dividends.csv": ["gross_amount", "tax", "net_amount"],
        "data/mock/fx_rates.csv": ["rate"],
    }
    date_columns = {
        "data/mock/transactions.csv": ["date"],
        "data/mock/positions_snapshot.csv": ["as_of"],
        "data/mock/app_report.csv": ["as_of"],
        "data/mock/cash_ledger.csv": ["date"],
        "data/mock/dividends.csv": ["pay_date"],
        "data/mock/fx_rates.csv": ["date"],
    }
    for rel, columns in numeric_columns.items():
        path = ROOT / rel
        if not path.exists():
            continue
        for index, row in enumerate(read_csv_dicts(path), start=2):
            for column in columns:
                try:
                    float(row[column])
                except ValueError:
                    errors.append(f"{rel}:{index} has nonnumeric {column}")
    for rel, columns in date_columns.items():
        path = ROOT / rel
        if not path.exists():
            continue
        for index, row in enumerate(read_csv_dicts(path), start=2):
            for column in columns:
                try:
                    date.fromisoformat(row[column])
                except ValueError:
                    errors.append(f"{rel}:{index} has invalid ISO date {column}")
    return errors


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_output_sections() -> list[str]:
    output_path = ROOT / "outputs/reconciliation-report.md"
    if not output_path.exists():
        return []
    text = read_text(output_path)
    return [f"Output missing heading: {heading}" for heading in OUTPUT_HEADINGS if heading not in text]


def validate_summary_json() -> list[str]:
    path = ROOT / "outputs/reconciliation-summary.json"
    if not path.exists():
        return []
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON summary: {exc}"]
    required = {
        "as_of",
        "base_currency",
        "status",
        "positions_checked",
        "unresolved_count",
        "net_cash_contributed_krw",
        "return_on_contributed_cash_pct",
        "annualized_xirr_note",
        "security_pnl_basis",
        "advice_boundary",
        "safety_boundary_note_present",
    }
    missing = sorted(required - set(data))
    return [f"Summary JSON missing keys: {', '.join(missing)}"] if missing else []


def validate_workbook() -> list[str]:
    path = ROOT / "outputs/stock_return_reconciliation_demo.xlsx"
    if not path.exists():
        return []
    if not zipfile.is_zipfile(path):
        return ["Demo workbook is not a valid XLSX zip package"]
    with zipfile.ZipFile(path) as archive:
        required_parts = {
            "[Content_Types].xml",
            "xl/workbook.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
        }
        missing = sorted(required_parts - set(archive.namelist()))
    return [f"Demo workbook missing parts: {', '.join(missing)}"] if missing else []


def validate_no_secrets_or_advice() -> list[str]:
    errors: list[str] = []
    env_path = ROOT / ".env"
    if env_path.exists() and env_path.stat().st_size > 0:
        errors.append("Local .env is non-empty; keep secrets out of the submission folder")
    for path in ROOT.rglob("*"):
        if (
            path.is_dir()
            or ".git" in path.parts
            or path.name == ".env"
            or path.name == "validate_sample.py"
            or "tests" in path.parts
        ):
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Potential secret or sensitive identifier pattern in {path.relative_to(ROOT)}")
                break
        for pattern in ADVICE_PATTERNS:
            if pattern.search(text):
                errors.append(f"Potential investment advice wording in {path.relative_to(ROOT)}")
                break
    return errors


def main() -> int:
    errors = []
    errors.extend(validate_required_files())
    errors.extend(validate_csv_columns())
    errors.extend(validate_csv_values())
    errors.extend(validate_output_sections())
    errors.extend(validate_summary_json())
    errors.extend(validate_workbook())
    errors.extend(validate_no_secrets_or_advice())

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    print(
        f"Checked {len(REQUIRED_FILES)} files, CSV schemas, numeric/date fields, outputs, workbook, secrets, and advice boundaries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
