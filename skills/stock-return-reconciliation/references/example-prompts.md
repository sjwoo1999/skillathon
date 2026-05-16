# Example Prompts

These prompts are designed for mock or sanitized data. They should not include
private account data, credentials, or requests for investment, trading, tax,
legal, or accounting advice.

## Full Reconciliation

```text
Use the stock-return-reconciliation skill on these mock files:
- transactions: data/mock/transactions.csv
- positions: data/mock/positions_snapshot.csv
- app report: data/mock/app_report.csv
- cash ledger: data/mock/cash_ledger.csv
- dividends: data/mock/dividends.csv
- FX rates: data/mock/fx_rates.csv

Period: YTD through 2026-05-16.
Return basis: compare price-only and total-return candidates against the app
reported return. Write the report to outputs/reconciliation-report.md.
```

## Validate Only

```text
Validate the mock stock return reconciliation inputs against the skill schema.
Do not calculate returns yet. List missing columns, date coverage issues,
currency issues, and privacy concerns.
```

## Method Comparison

```text
Using sanitized mock data, compare the price-only net-of-fees candidate and the
total-return-with-dividends candidate. Explain why they differ. Do not provide
investment advice.
```

## Investigate A Break

```text
The reported portfolio return is 4.82%, but the calculated return is 4.35%.
Use the reconciliation rules to identify whether cash flows, dividends, fees,
prices, or corporate actions explain the difference. Keep the output factual and
include an exception log.
```

## Security-Level Check

```text
Reconcile quantity, market value, income, and reported return for
SEC-ABC-MOCK only. Use supplied prices and transactions. Mark unsupported
comparisons as Not Comparable.
```

## Mixed-Currency Limitation

```text
The mock portfolio has USD and EUR holdings, but no FX table. Produce only the
checks that are valid without FX conversion and list what data is needed for a
consolidated portfolio return.
```

## Corporate Action Diagnostic

```text
Check whether the mock 2-for-1 split for SEC-SPLIT-MOCK explains the share
quantity and return difference. Confirm whether the prices are adjusted before
comparing returns.
```

## Unsafe Request Boundary

```text
I want a reconciliation report, but do not include account numbers or client
names in the output. If the files contain sensitive fields, stop and ask for a
sanitized version.
```

## Advice Boundary

```text
Reconcile the historical return calculations only. Do not tell me whether to buy,
sell, hold, rebalance, or take any tax position.
```
