# Output Format

Produce a markdown report. Keep calculations auditable and separate factual
reconciliation findings from limitations. Do not provide investment, trading,
tax, legal, or accounting advice.

## Filename

Recommended paths:

```text
outputs/reconciliation-report.md
outputs/return-candidates.csv
outputs/reconciliation-summary.json
```

If the user requests another path, use that path after confirming it is inside
the workspace.

## Report Template

```markdown
# Stock Return Reconciliation Report

## Executive Summary

- Base currency: `KRW`
- As of: `YYYY-MM-DD`
- Positions checked: ...
- Net cash contributed: ...
- App reported P&L: ...
- Sample-basis calculated difference: ...
- Return on contributed cash: ...
- Difference vs app: ...
- Numerically closest candidate basis: `...`

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
- Foreign-currency values are converted to KRW using supplied mock FX rates.
- Security-level P&L basis is explicitly labeled, including whether it is a
  sample source-currency translation, historical-FX cost basis, FIFO, tax lot,
  or another method.
- Annualized XIRR values are labeled as diagnostics from dated cash flows, not
  forecasts.

## Reconciliation Table

| Symbol | App Qty | Calc Qty | Qty Diff | Market Value KRW | Realized P&L KRW | Unrealized P&L KRW | Dividends KRW | Total P&L KRW | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| AAPL | 6 | 6 | 0 | ... | ... | ... | ... | ... | PASS |

## Return Candidates

| Candidate | Return % | P&L KRW | Difference vs App % | Difference vs App KRW | Basis |
| --- | ---: | ---: | ---: | ---: | --- |
| price_only_net_of_fees_taxes | ... | ... | ... | ... | ... |
| total_net_return_with_dividends | ... | ... | ... | ... | ... |
| app_reported | ... | ... | 0.00 | 0.00 | ... |

## Difference Drivers

- ...

## Data Quality Warnings

- ...

## Manual Checks And Skipped Checks

- ...

## Limitations

- This is not investment advice, tax advice, legal advice, or a brokerage statement replacement.
- Results depend on the completeness and accuracy of the provided input files.
```

## Required Sections

Every complete report must include:

- Executive Summary
- Input Files Reviewed
- Calculation Basis
- Reconciliation Table
- Return Candidates
- Difference Drivers
- Data Quality Warnings
- Manual Checks And Skipped Checks
- Limitations

If the output is limited because data is missing, keep the same sections but mark
unsupported tables as `Not calculated` and explain why.

## JSON Summary Keys

`outputs/reconciliation-summary.json` must include:

- `as_of`
- `base_currency`
- `status`
- `positions_checked`
- `unresolved_count`
- `closest_candidate`
- `net_cash_contributed_krw`
- `current_cash_value_krw`
- `current_net_asset_value_krw`
- `cumulative_pnl_krw`
- `cumulative_return_pct`
- `annualized_xirr_pct`
- `annualized_xirr_note`
- `security_pnl_basis`
- `app_total_pnl_krw`
- `recalculated_total_pnl_krw`
- `return_on_contributed_cash_pct`
- `difference_vs_app_krw`
- `advice_boundary`
- `safety_boundary_note_present`

## Status Vocabulary

Use only these reconciliation statuses:

- `Matched`
- `Explained Difference`
- `Unresolved Break`
- `Not Comparable`
- `Not Calculated`

Use only these validation results:

- `Pass`
- `Warning`
- `Break`
- `Blocker`
- `Skipped`

## Formatting Rules

- Display percentages with two decimal places unless the user requests another
  precision.
- Display basis-point differences as signed integers or one decimal place when
  needed.
- Display currency with two decimals and a currency code when multiple
  currencies appear.
- Cite source filenames in notes where important.
- Avoid hidden calculations in prose; show the key arithmetic inputs in tables.
- Keep sensitive identifiers masked or omitted.

## Language Rules

Use neutral reconciliation language:

- Say `The calculated return differs from the reported return by 8 bps`.
- Say `A missing dividend row could explain the break`.
- Say `This is not comparable because the reported method is unknown`.

Do not say:

- `This security is attractive`.
- `A trade action is warranted`.
- `This loss has a specific tax treatment`.
- `The source system is at fault`.
