# Stock Return Reconciliation Report

## Executive Summary

- Base currency: `KRW`
- As of: `2026-05-16`
- Positions checked: 2
- Net cash contributed: 4700000.00 KRW
- Current holdings value: 3058160.00 KRW
- Current cash value: 1952354.40 KRW
- Current net asset value: 5010514.40 KRW
- Current value difference vs net contributed cash: 310514.40 KRW
- Cumulative return vs contributed cash: 6.61%
- Cash-flow timing diagnostic: 18.17% annualized from mock dated flows, not a forecast
- App reported P&L: 257004.00 KRW
- Sample-basis calculated difference: 227533.40 KRW
- Return on contributed cash: 4.84%
- Difference vs app: -29470.60 KRW
- Numerically closest candidate basis: `total_net_return_with_dividends`

## Input Files Reviewed

- `data/mock/transactions.csv`
- `data/mock/positions_snapshot.csv`
- `data/mock/app_report.csv`
- `data/mock/cash_ledger.csv`
- `data/mock/dividends.csv`
- `data/mock/fx_rates.csv`

## Calculation Basis

- Synthetic mock data only.
- Weighted-average cost basis for the sample calculation.
- Buy fees and taxes are included in cost basis.
- Sell fees and taxes are deducted from proceeds.
- Net dividends are included only in the total-return candidate.
- USD values are converted to KRW using the provided mock FX rates.
- Current NAV includes reconstructed cash balances from cash ledger, transaction settlements, and dividends.
- XIRR is shown as an annualized reference and is not directly comparable to app-displayed cumulative return.

## Reconciliation Table

| Symbol | App Qty | Calc Qty | Qty Diff | Market Value KRW | Realized P&L KRW | Unrealized P&L KRW | Dividends KRW | Total P&L KRW | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| AAPL | 6 | 6 | 0 | 1538160.00 | 76766.00 | 68544.00 | 2723.40 | 148033.40 | Matched |
| 005930.KS | 20 | 20 | 0 | 1520000.00 | 0.00 | 79500.00 | 0.00 | 79500.00 | Matched |

## Return Candidates

| Candidate | Return % | P&L KRW | Difference vs App % | Difference vs App KRW | Basis |
| --- | ---: | ---: | ---: | ---: | --- |
| current_nav_vs_net_cash_contributed | 6.61 | 310514.40 | 1.14 | 53510.40 | Current holdings plus cash minus net external cash contributed |
| price_only_net_of_fees_taxes | 4.78 | 224810.00 | -0.69 | -32194.00 | Realized + unrealized P&L, net of modeled fees/taxes, excluding dividends |
| total_net_return_with_dividends | 4.84 | 227533.40 | -0.63 | -29470.60 | Realized + unrealized P&L + net dividends, net of modeled fees/taxes |
| app_reported | 5.47 | 257004.00 | 0.00 | 0.00 | Mock app display value from app_report.csv |

## Difference Drivers

- The app-displayed value may use a basis that is not documented in the supplied mock files.
- Possible items to verify: gross-versus-net dividend treatment, FX date policy, fee inclusion policy, denominator choice, and whether cash balances are included.
- The report does not assert that the app is wrong; it identifies calculation-basis differences to review.

## Data Quality Warnings

- No account numbers, customer ids, real names, API keys, or live brokerage exports are included.
- Corporate actions, margin, options, short selling, and multi-account transfers are outside this MVP.

## Manual Checks And Skipped Checks

- Manual check required: confirm the real app's return methodology before using this with real sanitized exports.
- Skipped: live market lookup, brokerage API access, tax filing logic, and trade-decision guidance.

## Limitations

- This is not investment advice, tax advice, legal advice, or a brokerage statement replacement.
- Results depend on the completeness and accuracy of the provided input files.
- App-internal rounding, settlement-date policy, and undisclosed FX policy may not be fully reproducible.
