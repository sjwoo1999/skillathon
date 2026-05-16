from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/stock-return-reconciliation/scripts/validate_sample.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_sample", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, text: str = "placeholder\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ValidateSampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.validator.ROOT = self.root

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_required_files_use_stock_skill_layout(self) -> None:
        errors = self.validator.validate_required_files()

        self.assertIn("Missing required file: README.md", errors)
        self.assertIn("Missing required file: skills/stock-return-reconciliation/SKILL.md", errors)
        self.assertNotIn("Missing required file: SKILL.md", errors)

    def test_csv_columns_reports_missing_required_fields(self) -> None:
        write_text(self.root / "data/mock/transactions.csv", "date,account,symbol\n2026-01-01,main,AAPL\n")

        errors = self.validator.validate_csv_columns()

        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("data/mock/transactions.csv missing columns:"))
        self.assertIn("side", errors[0])
        self.assertIn("settlement_amount", errors[0])

    def test_secret_scan_reports_sensitive_identifiers(self) -> None:
        write_text(self.root / "notes.md", "mock account " + "123456" + "789012")

        errors = self.validator.validate_no_secrets_or_advice()

        self.assertEqual(errors, ["Potential secret or sensitive identifier pattern in notes.md"])

    def test_advice_scan_reports_recommendation_language(self) -> None:
        write_text(self.root / "outputs/reconciliation-report.md", "buy " + "recommendation for AAPL\n")

        errors = self.validator.validate_no_secrets_or_advice()

        self.assertEqual(errors, ["Potential investment advice wording in outputs/reconciliation-report.md"])

    def test_advice_scan_reports_should_trade_language(self) -> None:
        write_text(self.root / "outputs/reconciliation-report.md", "you should " + "buy AAPL\n")

        errors = self.validator.validate_no_secrets_or_advice()

        self.assertEqual(errors, ["Potential investment advice wording in outputs/reconciliation-report.md"])

    def test_current_repository_passes_validation_after_generation(self) -> None:
        validator = load_validator()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = validator.main()

        self.assertEqual(result, 0, output.getvalue())
        self.assertIn("Validation passed.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
