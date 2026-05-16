# Troubleshooting

Use this guide when reconciliation cannot be completed or the calculated return
does not match the reported return.

## Missing Input Files

Symptoms:

- Required CSV path does not exist.
- User supplied positions but no transactions, app report, cash ledger,
  dividends, or FX rates.

Response:

- Ask for the missing file or an equivalent mapped file.
- Offer a limited report only if the user wants validation without full return
  calculation.
- Mark unsupported sections as `Not Calculated`.

Do not invent transactions, prices, or reported returns.

## Required Columns Are Missing

Symptoms:

- `security_id`, `account_id`, dates, market values, or reported returns are
  absent.
- Columns have different names than the schema.

Response:

- Ask the user to map source columns to the required schema.
- If the mapping is obvious, state the mapping before using it.
- Treat unmapped required fields as blockers.

## Calculated Return Is Far From Reported Return

Common causes:

- App method is undisclosed but calculated candidate uses explicit sample rules.
- Deposits or withdrawals were treated as internal activity.
- Dividends were excluded from a total return calculation.
- Fees or withholding taxes were treated differently.
- FX date policy differs from the app's internal policy.

Response:

- Compare method basis before concluding there is a break.
- Reconcile quantities and market values before reconciling returns.
- Move unexplained items to the exception log.

## Quantity Does Not Reconcile

Common causes:

- Missing purchase, sale, transfer, or reinvestment row
- Corporate action outside the MVP script
- Fractional shares rounded by the source
- Security id changed after a merger or symbol change

Response:

- Show beginning quantity, transaction quantity changes, corporate action
  effects, and ending quantity.
- Flag the exact security and account.
- Avoid changing source data unless the user explicitly asks for a corrected mock
  data example.

## Market Value Does Not Reconcile

Common causes:

- Price mismatch
- Currency mismatch
- FX conversion mismatch
- App uses a different snapshot price
- Option or futures multiplier missing
- Rounding precision too low

Response:

- Calculate `quantity * price` and compare with supplied market value.
- Check `currency` and `price_date`.
- If the instrument requires a multiplier and none is supplied, mark it
  unsupported.

## Reported Method Is Unknown

Symptoms:

- `reported_method` is `unknown`.
- App return cannot be identified as price-only, total return, TWR, MWR, or
  another basis.

Response:

- Calculate a candidate return only if the inputs support it.
- Label the comparison `Not Comparable` unless the basis can be inferred with
  evidence.
- Explain what additional source fields would make the comparison valid.

## Mixed Currencies

Symptoms:

- Holdings, prices, cash, or reported returns use different currencies.
- No FX table or source-converted values are supplied.

Response:

- Produce local-currency security checks if useful.
- Do not consolidate into one portfolio return without a conversion basis.
- Ask for supplied FX rates or source-converted market values.

## Corporate Actions

Symptoms:

- Share quantities change without buy or sell activity.
- A split, spinoff, merger, or ticker change appears in notes.
- Adjusted prices and unadjusted transactions are mixed.

Response:

- Identify the event and affected securities.
- Confirm whether prices are adjusted.
- Mark unsupported corporate actions as breaks or blockers depending on
  materiality.

## Privacy or Unsafe Data Appears

Symptoms:

- Full account numbers, tax ids, credentials, private URLs, or real client names
  appear.

Response:

- Stop processing the sensitive fields.
- Ask for sanitized mock data.
- Do not reproduce sensitive identifiers in the report.

## User Asks For Advice

Examples:

- A request for a trade decision about a security
- A request for a specific tax classification
- A request for portfolio allocation guidance

Response:

- Decline the advice portion briefly.
- Offer to continue with factual reconciliation only.
- Keep the report limited to historical arithmetic and supplied source data.
