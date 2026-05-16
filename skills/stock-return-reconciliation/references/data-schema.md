# Data Schema

This skill is designed for fictional, mock, public, or sanitized portfolio data.
Do not include real account numbers, tax identifiers, credentials, or private
client information in sample rows.

## File Set

Use these six inputs unless the user provides equivalent files with mapped
columns:

- `data/mock/transactions.csv`
- `data/mock/positions_snapshot.csv`
- `data/mock/app_report.csv`
- `data/mock/cash_ledger.csv`
- `data/mock/dividends.csv`
- `data/mock/fx_rates.csv`

If a file is missing, ask whether to proceed with a limited reconciliation. Do
not silently infer transaction activity or prices.

## `data/mock/transactions.csv`

One row per buy or sell transaction in the mock brokerage export.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| date | Yes | ISO trade date | 2026-01-05 |
| account | Yes | Sanitized account label | main |
| symbol | Yes | Security symbol | AAPL |
| name | Yes | Mock security name | Apple Example Inc |
| side | Yes | `BUY` or `SELL` | BUY |
| quantity | Yes | Shares or units traded | 10 |
| price | Yes | Trade price in transaction currency | 180.00 |
| currency | Yes | ISO currency code | USD |
| fee | Yes | Explicit fee in transaction currency | 1.00 |
| tax | Yes | Explicit transaction tax in transaction currency | 0.00 |
| settlement_amount | Yes | Signed cash settlement amount | -1801.00 |

Validation notes:

- Required dates must parse as ISO `YYYY-MM-DD`.
- `side` must be `BUY` or `SELL` for the current deterministic sample script.
- Numeric fields must parse as numbers.
- Fees and taxes are source arithmetic fields only. Do not provide tax advice.
- Settlement amount signs should be documented before comparing to cash.

## `data/mock/positions_snapshot.csv`

One row per open security position at the app report date.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| as_of | Yes | ISO snapshot date | 2026-05-16 |
| account | Yes | Matches transaction account | main |
| symbol | Yes | Security symbol | AAPL |
| name | Yes | Mock security name | Apple Example Inc |
| quantity | Yes | App-reported open quantity | 6 |
| market_price | Yes | Snapshot market price | 188.50 |
| currency | Yes | ISO currency code | USD |
| market_value | Yes | Quantity times market price | 1131.00 |

Validation notes:

- `market_value` should equal `quantity * market_price` within rounding
  tolerance.
- Each symbol should have a calculated quantity from transactions.
- Missing positions can mean a fully sold security or missing snapshot row.

## `data/mock/app_report.csv`

One row for the app-level reported return being reconciled.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| as_of | Yes | ISO report date | 2026-05-16 |
| account | Yes | Sanitized account label | main |
| period | Yes | Display period label | YTD |
| app_total_pnl | Yes | App-reported total P&L in report currency | 257004 |
| app_return_pct | Yes | App-reported return in percent units | 5.47 |
| currency | Yes | ISO report currency | KRW |
| app_label | Yes | Source display label | total return shown in app |

Validation notes:

- `app_return_pct` is in percent units: `5.47` means `5.47%`.
- The sample script treats this row as the comparison target.
- Do not assert the app is wrong without evidence; report calculation
  differences and likely drivers.

## `data/mock/cash_ledger.csv`

One row per mock cash movement used for net contribution.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| date | Yes | ISO cash movement date | 2026-01-02 |
| account | Yes | Sanitized account label | main |
| type | Yes | Cash movement type | DEPOSIT |
| currency | Yes | ISO currency code | KRW |
| amount | Yes | Signed amount in cash currency | 5000000 |
| description | Yes | Sanitized description | Mock opening contribution |

Validation notes:

- The sample script sums `DEPOSIT` and `WITHDRAWAL` rows as net contribution.
- If withdrawals are negative, preserve the source sign and document the policy.
- Do not treat deposits or withdrawals as return drivers without method context.

## `data/mock/dividends.csv`

One row per dividend payment.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| pay_date | Yes | ISO pay date | 2026-02-15 |
| account | Yes | Sanitized account label | main |
| symbol | Yes | Security symbol | AAPL |
| gross_amount | Yes | Dividend before source tax | 12.00 |
| tax | Yes | Withholding or tax amount in source data | 1.80 |
| net_amount | Yes | Net dividend amount | 10.20 |
| currency | Yes | ISO currency code | USD |

Validation notes:

- Net dividends are included in the total-return candidate.
- Gross-versus-net dividend treatment is a common difference driver.
- Do not provide tax treatment or tax filing guidance.

## `data/mock/fx_rates.csv`

One row per date and base currency conversion into the report currency.

| Column | Required | Description | Example |
| --- | --- | --- | --- |
| date | Yes | ISO FX date | 2026-05-16 |
| base | Yes | Source currency | USD |
| quote | Yes | Report currency | KRW |
| rate | Yes | Conversion rate from base to quote | 1360.25 |

Validation notes:

- The current sample report uses KRW as base report currency.
- KRW rows can be treated as rate `1` by the script.
- Missing FX rows are blockers for consolidated KRW P&L.

## Minimal Mock Data Expectations

For a Skillathon demonstration, include enough rows to cover:

- At least one buy or sell
- At least one open position snapshot
- At least one dividend row
- At least one cash ledger contribution or withdrawal
- At least one app report row
- At least one non-KRW position requiring FX conversion

Mock data should use obviously synthetic ids such as `ACCT-MOCK-01` and
example names such as `Apple Example Inc`.
