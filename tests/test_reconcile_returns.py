from __future__ import annotations

import csv
import importlib.util
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills/stock-return-reconciliation/scripts/reconcile_returns.py"


def load_module():
    spec = importlib.util.spec_from_file_location("reconcile_returns", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReconcileReturnsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_calculates_expected_mock_total_pnl(self) -> None:
        result = self.module.calculate_reconciliation()

        self.assertEqual(result["base_currency"], "KRW")
        self.assertEqual(result["app_total_pnl"], Decimal("257004"))
        self.assertEqual(self.module.money(result["total_pnl"]), Decimal("227533.40"))
        self.assertEqual(self.module.money(result["total_pnl"] - result["app_total_pnl"]), Decimal("-29470.60"))
        self.assertEqual(self.module.pct(result["contribution_return_pct"]), Decimal("4.84"))
        self.assertEqual(result["closest_candidate"], "total_net_return_with_dividends")

    def test_main_writes_expected_outputs(self) -> None:
        result = self.module.main()

        self.assertEqual(result, 0)
        self.assertTrue((REPO_ROOT / "outputs/reconciliation-report.md").exists())
        with (REPO_ROOT / "outputs/return-candidates.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["candidate"] for row in rows], [
            "current_nav_vs_net_cash_contributed",
            "price_only_net_of_fees_taxes",
            "total_net_return_with_dividends",
            "app_reported",
        ])
        summary = json.loads((REPO_ROOT / "outputs/reconciliation-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["advice_boundary"], "factual_reconciliation_only")
        self.assertIn("not a forecast", summary["annualized_xirr_note"])
        self.assertIn("not a historical-FX cost-basis", summary["security_pnl_basis"])
        self.assertTrue(summary["safety_boundary_note_present"])
        self.assertEqual(summary["unresolved_count"], 0)
        self.assertEqual(summary["return_on_contributed_cash_pct"], "4.84")


if __name__ == "__main__":
    unittest.main()
