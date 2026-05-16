#!/usr/bin/env python3
"""Generate a deterministic mock stock-return reconciliation report."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "mock"
OUTPUTS = ROOT / "outputs"
BASE_CURRENCY = "KRW"


@dataclass
class PositionState:
    quantity: Decimal = Decimal("0")
    cost: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pct(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_fx() -> dict[tuple[str, str], Decimal]:
    rates: dict[tuple[str, str], Decimal] = {}
    for row in read_csv(DATA / "fx_rates.csv"):
        rates[(row["date"], row["base"])] = Decimal(row["rate"])
    return rates


def fx_rate(rates: dict[tuple[str, str], Decimal], date: str, currency: str) -> Decimal:
    if currency == BASE_CURRENCY:
        return Decimal("1")
    return rates[(date, currency)]


def calculate_positions() -> tuple[dict[str, PositionState], dict[str, Decimal]]:
    states: dict[str, PositionState] = defaultdict(PositionState)
    realized_by_symbol_krw: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    rates = load_fx()

    for row in read_csv(DATA / "transactions.csv"):
        symbol = row["symbol"]
        state = states[symbol]
        quantity = Decimal(row["quantity"])
        price = Decimal(row["price"])
        fee = Decimal(row["fee"])
        tax = Decimal(row["tax"])
        currency = row["currency"]
        side = row["side"]

        if side == "BUY":
            state.quantity += quantity
            state.cost += quantity * price + fee + tax
        elif side == "SELL":
            if state.quantity <= 0 or quantity > state.quantity:
                raise ValueError(f"Cannot sell {quantity} {symbol}; available quantity is {state.quantity}")
            average_cost = state.cost / state.quantity
            allocated_cost = average_cost * quantity
            net_proceeds = quantity * price - fee - tax
            realized = net_proceeds - allocated_cost
            state.quantity -= quantity
            state.cost -= allocated_cost
            state.realized_pnl += realized
            realized_by_symbol_krw[symbol] += realized * fx_rate(rates, row["date"], currency)
        else:
            raise ValueError(f"Unsupported transaction side: {side}")

    return states, realized_by_symbol_krw


def calculate_cash_balances() -> dict[str, Decimal]:
    balances: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for row in read_csv(DATA / "cash_ledger.csv"):
        balances[row["currency"]] += Decimal(row["amount"])
    for row in read_csv(DATA / "transactions.csv"):
        balances[row["currency"]] += Decimal(row["settlement_amount"])
    for row in read_csv(DATA / "dividends.csv"):
        balances[row["currency"]] += Decimal(row["net_amount"])
    return balances


def cash_value_krw(balances: dict[str, Decimal], rates: dict[tuple[str, str], Decimal], as_of: str) -> Decimal:
    total = Decimal("0")
    for currency, amount in balances.items():
        total += amount * fx_rate(rates, as_of, currency)
    return total


def xirr(cashflows: list[tuple[str, Decimal]]) -> Decimal | None:
    if not cashflows or not any(amount > 0 for _, amount in cashflows) or not any(amount < 0 for _, amount in cashflows):
        return None
    dated = [(date.fromisoformat(day), float(amount)) for day, amount in cashflows]
    start = dated[0][0]

    def npv(rate: float) -> float:
        return sum(amount / ((1 + rate) ** ((day - start).days / 365.0)) for day, amount in dated)

    low = -0.9999
    high = 10.0
    low_npv = npv(low)
    high_npv = npv(high)
    if low_npv * high_npv > 0:
        return None
    for _ in range(100):
        mid = (low + high) / 2
        mid_npv = npv(mid)
        if abs(mid_npv) < 0.0001:
            return Decimal(str(mid * 100))
        if low_npv * mid_npv <= 0:
            high = mid
            high_npv = mid_npv
        else:
            low = mid
            low_npv = mid_npv
    return Decimal(str(((low + high) / 2) * 100))


def calculate_reconciliation() -> dict[str, object]:
    rates = load_fx()
    states, realized_by_symbol_krw = calculate_positions()
    positions = read_csv(DATA / "positions_snapshot.csv")
    dividends = read_csv(DATA / "dividends.csv")
    app_report = read_csv(DATA / "app_report.csv")[0]
    as_of = app_report["as_of"]

    dividends_by_symbol_krw: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for row in dividends:
        dividends_by_symbol_krw[row["symbol"]] += (
            Decimal(row["net_amount"]) * fx_rate(rates, row["pay_date"], row["currency"])
        )

    rows: list[dict[str, object]] = []
    totals = {
        "realized_pnl": Decimal("0"),
        "unrealized_pnl": Decimal("0"),
        "dividends": Decimal("0"),
        "market_value": Decimal("0"),
    }

    for position in positions:
        symbol = position["symbol"]
        state = states[symbol]
        currency = position["currency"]
        app_quantity = Decimal(position["quantity"])
        market_value = Decimal(position["market_value"])
        unrealized_local = market_value - state.cost
        current_fx = fx_rate(rates, as_of, currency)
        unrealized_krw = unrealized_local * current_fx
        market_value_krw = market_value * current_fx
        realized_krw = realized_by_symbol_krw[symbol]
        dividend_krw = dividends_by_symbol_krw[symbol]
        total_pnl = realized_krw + unrealized_krw + dividend_krw
        quantity_diff = app_quantity - state.quantity

        status = "Matched" if abs(quantity_diff) <= Decimal("0.000001") else "Unresolved Break"
        rows.append(
            {
                "symbol": symbol,
                "currency": currency,
                "calc_quantity": state.quantity,
                "app_quantity": app_quantity,
                "quantity_diff": quantity_diff,
                "remaining_cost": state.cost,
                "market_value": market_value,
                "market_value_krw": market_value_krw,
                "realized_pnl_krw": realized_krw,
                "unrealized_pnl_krw": unrealized_krw,
                "dividends_krw": dividend_krw,
                "total_pnl_krw": total_pnl,
                "status": status,
            }
        )
        totals["realized_pnl"] += realized_krw
        totals["unrealized_pnl"] += unrealized_krw
        totals["dividends"] += dividend_krw
        totals["market_value"] += market_value_krw

    net_contribution = Decimal("0")
    external_cashflows: list[tuple[str, Decimal]] = []
    for row in read_csv(DATA / "cash_ledger.csv"):
        if row["type"] == "DEPOSIT":
            net_contribution += Decimal(row["amount"])
            external_cashflows.append((row["date"], -Decimal(row["amount"])))
        elif row["type"] == "WITHDRAWAL":
            net_contribution += Decimal(row["amount"])
            external_cashflows.append((row["date"], -Decimal(row["amount"])))

    app_total_pnl = Decimal(app_report["app_total_pnl"])
    total_pnl = totals["realized_pnl"] + totals["unrealized_pnl"] + totals["dividends"]
    price_only_pnl = totals["realized_pnl"] + totals["unrealized_pnl"]
    cash_balances = calculate_cash_balances()
    current_cash_value = cash_value_krw(cash_balances, rates, as_of)
    current_nav = totals["market_value"] + current_cash_value
    cumulative_pnl = current_nav - net_contribution
    cumulative_return = cumulative_pnl / net_contribution * Decimal("100")
    xirr_cashflows = external_cashflows + [(as_of, current_nav)]
    xirr_return = xirr(xirr_cashflows)
    contribution_return = total_pnl / net_contribution * Decimal("100")
    candidates = [
        {
            "candidate": "current_nav_vs_net_cash_contributed",
            "return_pct": cumulative_return,
            "pnl_krw": cumulative_pnl,
            "basis": "Current holdings plus cash minus net external cash contributed",
        },
        {
            "candidate": "price_only_net_of_fees_taxes",
            "return_pct": price_only_pnl / net_contribution * Decimal("100"),
            "pnl_krw": price_only_pnl,
            "basis": "Realized + unrealized P&L, net of modeled fees/taxes, excluding dividends",
        },
        {
            "candidate": "total_net_return_with_dividends",
            "return_pct": total_pnl / net_contribution * Decimal("100"),
            "pnl_krw": total_pnl,
            "basis": "Realized + unrealized P&L + net dividends, net of modeled fees/taxes",
        },
        {
            "candidate": "app_reported",
            "return_pct": Decimal(app_report["app_return_pct"]),
            "pnl_krw": app_total_pnl,
            "basis": "Mock app display value from app_report.csv",
        },
    ]

    for candidate in candidates:
        candidate["app_return_diff_pct"] = candidate["return_pct"] - Decimal(app_report["app_return_pct"])
        candidate["app_pnl_diff_krw"] = candidate["pnl_krw"] - app_total_pnl

    closest = min(
        [candidate for candidate in candidates if candidate["candidate"] != "app_reported"],
        key=lambda candidate: abs(candidate["app_return_diff_pct"]),
    )
    return {
        "as_of": as_of,
        "base_currency": BASE_CURRENCY,
        "net_contribution": net_contribution,
        "current_cash_value": current_cash_value,
        "current_nav": current_nav,
        "cumulative_pnl": cumulative_pnl,
        "cumulative_return_pct": cumulative_return,
        "xirr_return_pct": xirr_return,
        "cash_balances": cash_balances,
        "app_total_pnl": app_total_pnl,
        "app_return_pct": Decimal(app_report["app_return_pct"]),
        "rows": rows,
        "totals": totals,
        "total_pnl": total_pnl,
        "price_only_pnl": price_only_pnl,
        "contribution_return_pct": contribution_return,
        "candidates": candidates,
        "closest_candidate": closest["candidate"],
    }


def write_outputs(result: dict[str, object]) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    candidates = result["candidates"]
    rows = result["rows"]

    with (OUTPUTS / "return-candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["candidate", "return_pct", "pnl_krw", "app_return_diff_pct", "app_pnl_diff_krw", "basis"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in candidates:
            writer.writerow(
                {
                    "candidate": row["candidate"],
                    "return_pct": pct(row["return_pct"]),
                    "pnl_krw": money(row["pnl_krw"]),
                    "app_return_diff_pct": pct(row["app_return_diff_pct"]),
                    "app_pnl_diff_krw": money(row["app_pnl_diff_krw"]),
                    "basis": row["basis"],
                }
            )

    unresolved = [row for row in rows if row["status"] != "Matched"]
    summary = {
        "as_of": result["as_of"],
        "base_currency": result["base_currency"],
        "status": "needs_review" if unresolved else "pass_with_manual_review",
        "positions_checked": len(rows),
        "unresolved_count": len(unresolved),
        "closest_candidate": result["closest_candidate"],
        "net_cash_contributed_krw": str(money(result["net_contribution"])),
        "current_cash_value_krw": str(money(result["current_cash_value"])),
        "current_net_asset_value_krw": str(money(result["current_nav"])),
        "cumulative_pnl_krw": str(money(result["cumulative_pnl"])),
        "cumulative_return_pct": str(pct(result["cumulative_return_pct"])),
        "annualized_xirr_pct": str(pct(result["xirr_return_pct"])) if result["xirr_return_pct"] is not None else None,
        "app_total_pnl_krw": str(money(result["app_total_pnl"])),
        "recalculated_total_pnl_krw": str(money(result["total_pnl"])),
        "return_on_contributed_cash_pct": str(pct(result["contribution_return_pct"])),
        "difference_vs_app_krw": str(money(result["total_pnl"] - result["app_total_pnl"])),
        "advice_boundary": "factual_reconciliation_only",
        "safety_boundary_note_present": True,
    }
    (OUTPUTS / "reconciliation-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Stock Return Reconciliation Report",
        "",
        "## Executive Summary",
        "",
        f"- Base currency: `{result['base_currency']}`",
        f"- As of: `{result['as_of']}`",
        f"- Positions checked: {len(rows)}",
        f"- Net cash contributed: {money(result['net_contribution'])} KRW",
        f"- Current holdings value: {money(result['totals']['market_value'])} KRW",
        f"- Current cash value: {money(result['current_cash_value'])} KRW",
        f"- Current net asset value: {money(result['current_nav'])} KRW",
        f"- Current value difference vs net contributed cash: {money(result['cumulative_pnl'])} KRW",
        f"- Cumulative return vs contributed cash: {pct(result['cumulative_return_pct'])}%",
        f"- Cash-flow timing diagnostic: {pct(result['xirr_return_pct']) if result['xirr_return_pct'] is not None else 'Not calculated'}% annualized from mock dated flows, not a forecast",
        f"- App reported P&L: {money(result['app_total_pnl'])} KRW",
        f"- Sample-basis calculated difference: {money(result['total_pnl'])} KRW",
        f"- Return on contributed cash: {pct(result['contribution_return_pct'])}%",
        f"- Difference vs app: {money(result['total_pnl'] - result['app_total_pnl'])} KRW",
        f"- Numerically closest candidate basis: `{result['closest_candidate']}`",
        "",
        "## Input Files Reviewed",
        "",
        "- `data/mock/transactions.csv`",
        "- `data/mock/positions_snapshot.csv`",
        "- `data/mock/app_report.csv`",
        "- `data/mock/cash_ledger.csv`",
        "- `data/mock/dividends.csv`",
        "- `data/mock/fx_rates.csv`",
        "",
        "## Calculation Basis",
        "",
        "- Synthetic mock data only.",
        "- Weighted-average cost basis for the sample calculation.",
        "- Buy fees and taxes are included in cost basis.",
        "- Sell fees and taxes are deducted from proceeds.",
            "- Net dividends are included only in the total-return candidate.",
            "- USD values are converted to KRW using the provided mock FX rates.",
            "- Current NAV includes reconstructed cash balances from cash ledger, transaction settlements, and dividends.",
            "- XIRR is shown as an annualized reference and is not directly comparable to app-displayed cumulative return.",
        "",
        "## Reconciliation Table",
        "",
        "| Symbol | App Qty | Calc Qty | Qty Diff | Market Value KRW | Realized P&L KRW | Unrealized P&L KRW | Dividends KRW | Total P&L KRW | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {symbol} | {app_quantity} | {calc_quantity} | {quantity_diff} | {market_value_krw} | {realized_pnl_krw} | {unrealized_pnl_krw} | {dividends_krw} | {total_pnl_krw} | {status} |".format(
                symbol=row["symbol"],
                app_quantity=row["app_quantity"],
                calc_quantity=row["calc_quantity"],
                quantity_diff=row["quantity_diff"],
                market_value_krw=money(row["market_value_krw"]),
                realized_pnl_krw=money(row["realized_pnl_krw"]),
                unrealized_pnl_krw=money(row["unrealized_pnl_krw"]),
                dividends_krw=money(row["dividends_krw"]),
                total_pnl_krw=money(row["total_pnl_krw"]),
                status=row["status"],
            )
        )
    lines.extend(
        [
            "",
            "## Return Candidates",
            "",
            "| Candidate | Return % | P&L KRW | Difference vs App % | Difference vs App KRW | Basis |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in candidates:
        lines.append(
            f"| {row['candidate']} | {pct(row['return_pct'])} | {money(row['pnl_krw'])} | {pct(row['app_return_diff_pct'])} | {money(row['app_pnl_diff_krw'])} | {row['basis']} |"
        )
    lines.extend(
        [
            "",
            "## Difference Drivers",
            "",
            "- The app-displayed value may use a basis that is not documented in the supplied mock files.",
            "- Possible items to verify: gross-versus-net dividend treatment, FX date policy, fee inclusion policy, denominator choice, and whether cash balances are included.",
            "- The report does not assert that the app is wrong; it identifies calculation-basis differences to review.",
            "",
            "## Data Quality Warnings",
            "",
            "- No account numbers, customer ids, real names, API keys, or live brokerage exports are included.",
            "- Corporate actions, margin, options, short selling, and multi-account transfers are outside this MVP.",
            "",
            "## Manual Checks And Skipped Checks",
            "",
            "- Manual check required: confirm the real app's return methodology before using this with real sanitized exports.",
            "- Skipped: live market lookup, brokerage API access, tax filing logic, and trade-decision guidance.",
            "",
            "## Limitations",
            "",
            "- This is not investment advice, tax advice, legal advice, or a brokerage statement replacement.",
            "- Results depend on the completeness and accuracy of the provided input files.",
            "- App-internal rounding, settlement-date policy, and undisclosed FX policy may not be fully reproducible.",
            "",
        ]
    )
    (OUTPUTS / "reconciliation-report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_outputs(calculate_reconciliation())
    print("Generated reconciliation outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
