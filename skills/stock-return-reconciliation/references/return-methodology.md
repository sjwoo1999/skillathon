# Return Methodology

This reference defines calculation choices for reconciliation. It is not
investment, tax, legal, or accounting advice.

## Required Method Choices

Before calculating, identify or ask for:

- Reporting period start date
- Reporting period end date
- Return basis: app-reported, price-only candidate, total-return candidate,
  `twr`, `mwr`, or simple diagnostic
- Currency basis: supplied FX into KRW for the Skillathon sample
- Price basis: adjusted or unadjusted
- Cash flow classification
- Rounding and tolerance

If the reported method is unknown, calculate clearly labeled candidates and avoid
claiming the source is wrong solely because methods differ.

## Core Terms

| Term | Meaning |
| --- | --- |
| Beginning market value | Portfolio or security value at period start |
| Ending market value | Portfolio or security value at period end |
| External flow | Deposit, withdrawal, transfer in, transfer out, or journal classified as outside investor activity |
| Internal flow | Buy, sell, dividend reinvestment, interest, fee, tax, split, or cash movement inside the account |
| Income | Dividends and interest supplied in transactions |
| Fees and taxes | Explicit charges supplied in transactions; listed for reconciliation, not advice |
| Return break | Difference between calculated and reported returns beyond tolerance |

## Skillathon Sample Calculation

The included deterministic sample script calculates reconciliation candidates
from:

- `data/mock/transactions.csv`
- `data/mock/positions_snapshot.csv`
- `data/mock/app_report.csv`
- `data/mock/cash_ledger.csv`
- `data/mock/dividends.csv`
- `data/mock/fx_rates.csv`

Sample policies:

- Base report currency is KRW.
- USD values are converted to KRW using supplied mock FX rates.
- Position cost uses weighted-average cost.
- Buy fees and taxes are included in cost.
- Sell fees and taxes reduce proceeds.
- Net dividends are included only in the total-return candidate.
- App-reported return is treated as a comparison target, not as advice or a
  guaranteed source of truth.

The sample script writes:

- `outputs/reconciliation-report.md`
- `outputs/return-candidates.csv`
- `outputs/reconciliation-summary.json`

## Simple Return

Use simple return only when there are no material external flows, or when the
user asks for a rough diagnostic.

Formula:

```text
simple_return = (ending_value - beginning_value - external_net_flow) / beginning_value
```

Where:

```text
external_net_flow = deposits + transfer_ins - withdrawals - transfer_outs
```

Limitations:

- Timing of flows is ignored.
- It can materially differ from time-weighted or money-weighted returns.
- It should not be used to judge manager performance when external flows exist.

## Time-Weighted Return

Use time-weighted return when reconciling performance that should remove the
effect of external flow timing.

Workflow:

1. Sort valuation points from period start through period end.
2. Create a subperiod boundary at each external flow date.
3. Value the portfolio immediately before and after each external flow when data
   supports it.
4. Calculate each subperiod return.
5. Chain subperiod returns geometrically.

Formula:

```text
subperiod_return = (ending_value_before_next_flow - beginning_value_after_flow) / beginning_value_after_flow
time_weighted_return = product(1 + subperiod_return_i) - 1
```

If only daily closing prices are available, document that the result is an
approximation and state whether flows are assumed at start of day, end of day, or
midday.

## Money-Weighted Return

Use money-weighted return when reconciling investor experience with actual cash
flow timing.

Recommended implementation:

- Treat beginning value as a negative cash flow at period start.
- Treat external deposits as negative flows from the investor perspective.
- Treat external withdrawals as positive flows.
- Treat ending value as a positive cash flow at period end.
- Solve for IRR using dated cash flows, if the tooling supports XIRR.

Sign convention must be documented because source files vary.

Limitations:

- Multiple valid IRR roots can occur with unusual cash-flow patterns.
- Missing flow dates can materially change the result.
- MWR can differ from TWR without indicating an error.

## Security-Level Return

For security-level reconciliation:

1. Isolate opening position, transactions, income, and closing position for each
   `security_id`.
2. Use snapshot prices from `data/mock/positions_snapshot.csv` and supplied FX
   rates from `data/mock/fx_rates.csv`.
3. Include dividends and corporate actions based on the reported method.
4. Reconcile shares first, then market value, then return.

Security-level return should be labeled as one of:

- Price return: price change only
- Total return: price change plus dividends or distributions
- Source-method candidate: method inferred from reported fields

Do not compare a price return to a total return without highlighting the basis
difference.

## Income, Fees, and Taxes

Classify source transactions as follows:

- `dividend` and `interest`: income
- `fee`: explicit expense
- `tax`: explicit withholding or transaction tax from source data
- `buy` and `sell`: trading activity
- `deposit`, `withdrawal`, `transfer_in`, `transfer_out`: external flows unless
  the user specifies otherwise

Do not provide tax treatment or deductibility guidance. Only report how source
amounts affect reconciliation arithmetic.

## Corporate Actions

Splits, spinoffs, mergers, and symbol changes must be treated as reconciliation
events, not performance claims.

Minimum handling:

- Verify quantity changes reconcile after splits.
- Confirm whether prices are split-adjusted.
- Separate market value changes caused by spinoffs or mergers from unexplained
  return breaks.
- Flag unsupported corporate actions as exceptions.

## Currency Handling

Default to single-currency reconciliation. If multiple currencies appear:

- Check whether all reported returns are in a shared base currency.
- Require supplied FX rates or source-converted market values.
- Avoid fetching FX rates unless explicitly approved.
- If FX is unavailable, produce a limited local-currency reconciliation and flag
  cross-currency return comparisons as unsupported.

## Rounding

Recommended defaults:

- Currency: round display to 2 decimals
- Shares: round display to 6 decimals
- Returns: round display to 2 basis points or 0.01 percentage points
- Reconciliation tolerance: configurable, default 5 basis points for returns and
  the greater of 1.00 currency unit or 0.01% of value for market values

Always calculate from unrounded values when available, then round only for
display.
