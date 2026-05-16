# Reconciliation Rules

Apply these rules after schema validation and methodology selection. Rules are
designed to explain differences; they are not investment, tax, legal, or
accounting advice.

## Severity Levels

| Severity | Meaning | Output Treatment |
| --- | --- | --- |
| Info | Expected difference or documented assumption | Include in validation notes |
| Warning | Potential data issue that may affect results | Include in exception log |
| Break | Difference exceeds tolerance or blocks reconciliation | Highlight in summary and exception log |
| Blocker | Missing or unsafe data prevents responsible output | Stop or produce limited output only |

## Rule Order

Run checks in this order:

1. File availability
2. Required columns
3. Date range coverage
4. Currency consistency
5. Holdings quantity reconciliation
6. Position market value checks
7. Cash ledger classification
8. Dividend, fee, and tax totals
9. FX conversion checks
10. Return candidate comparison

## File and Column Checks

Create a blocker if:

- A required input file is missing and no equivalent mapping is supplied.
- A required column is absent.
- Required dates cannot be parsed.
- Required numeric fields contain non-numeric values that cannot be excluded.

Create a warning if:

- Optional columns needed for richer explanations are missing.
- Duplicate transaction ids appear.
- Blank tickers exist but `security_id` is present.

## Date Range Coverage

Create a break if:

- Holdings do not include the period start or period end.
- Prices do not cover securities held or traded during the period.
- Reported returns use period dates that differ from the requested period.

Create a warning if:

- Settlement dates fall outside the period while trade dates fall inside it.
- Price dates are nearest available dates rather than exact dates.

Document whether calculations use trade date or settlement date.

## Currency Checks

Create a blocker if:

- Multiple currencies are present and no conversion basis is supplied, but the
  user asks for one consolidated return.

Create a warning if:

- Securities, prices, and reported returns use different currency codes.
- Cash is held in a different currency than portfolio reporting currency.

Allowed limited output:

- Local-currency security-level checks
- Share reconciliation
- Missing FX exception log

## Holdings and Quantity Reconciliation

For each `account_id` and `security_id`:

```text
expected_ending_quantity =
  beginning_quantity
  + BUY quantity
  - SELL quantity
  +/- split_or_corporate_action_quantity_effect
```

Create a break if expected quantity differs from ending quantity beyond share
tolerance.

Common explanations:

- Missing transaction
- Split or corporate action outside the sample script
- Fractional share rounding
- Dividend reinvestment omitted or duplicated

## Market Value Reconciliation

For each position:

```text
expected_market_value = ending_quantity * ending_price
market_value_break = supplied_ending_market_value - expected_market_value
```

Create a break if the difference exceeds market value tolerance.

Common explanations:

- Stale or missing price
- Price currency mismatch
- Accrued income included in source value
- Option multiplier not supplied
- Rounding or fractional quantity precision

## Cash Flow Classification

Classify each transaction into one of:

- BUY or SELL trade from `transactions.csv`
- DEPOSIT or WITHDRAWAL from `cash_ledger.csv`
- Dividend from `dividends.csv`
- Explicit fee or tax fields from source rows
- Unsupported or unknown source activity

Create a warning if `other` or `journal` transactions materially affect return.
Create a break if a material unclassified cash flow prevents matching the
reported method.

## Income, Fee, and Tax Checks

Compare calculated totals to reported totals when reported fields are supplied:

```text
income_break = reported_income - calculated_income
fee_break = reported_fees - calculated_fees
```

Create a warning if taxes are present but the reported return does not specify
whether returns are gross or net of withholding. Do not advise on tax treatment.

## Corporate Action Checks

Create a break if:

- Split ratios do not reconcile share quantities.
- Adjusted prices are mixed with unadjusted quantities.
- Spinoff or merger rows are present but no valuation treatment is supplied.

Create an info note if:

- The corporate action fully reconciles shares and market value.

## Return Comparison

For each reported return row:

```text
return_break_bps = (calculated_return_pct - reported_return_pct) * 100
```

Because `reported_return_pct` is in percent units, a difference of `0.05` equals
5 basis points.

Default tolerance:

- Portfolio return: 5 basis points
- Security return: 10 basis points
- Simple diagnostic return: label as diagnostic, not pass/fail, unless the
  reported method is also simple

Status labels:

- `Matched`: within tolerance and method basis aligns
- `Explained Difference`: outside tolerance but attributable to documented
  method, timing, price, income, fee, or corporate action basis
- `Unresolved Break`: outside tolerance without enough evidence
- `Not Comparable`: methods, currencies, or data coverage are incompatible

## Safety and Privacy Rules

Stop and ask for sanitized data if inputs contain:

- Full account numbers
- Social Security numbers, tax ids, or national ids
- API keys, tokens, passwords, or private URLs
- Client names where consent is not clear

Remove or mask sensitive identifiers in the report. Do not include investment,
trading, tax, legal, or accounting guidance.
