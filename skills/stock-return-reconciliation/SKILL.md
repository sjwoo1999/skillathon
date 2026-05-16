---
name: stock-return-reconciliation
description: Use this skill when a user needs to understand current return against net cash contributed using supplied mock or sanitized holdings, transactions, dividends, fees, taxes, FX, prices, and reported app returns. Do not use it to give investment, tax, legal, accounting, trading, or trade-decision guidance.
---

# Stock Return Reconciliation

## When To Use

Use this skill to calculate current return against net cash contributed and
compare that view with reported app returns using user-provided or mock data.

Good use cases:
- Reconciling brokerage-reported period returns against transaction-level data
- Checking whether deposits, withdrawals, dividends, fees, splits, and taxes were
  handled consistently
- Producing an auditable markdown report from sanitized CSV inputs
- Stress-testing a return methodology with mock data

Do not use this skill for:
- Investment, trading, tax, legal, or accounting guidance
- Predicting future performance or telling the user what action to take
- Working with private account data unless the user confirms it is sanitized
- Fetching live market prices unless the user explicitly requests it and approves
  the source

## Required Input

- Transactions CSV, for example `data/mock/transactions.csv`
- Positions snapshot CSV, for example `data/mock/positions_snapshot.csv`
- App report CSV, for example `data/mock/app_report.csv`
- Cash ledger CSV, for example `data/mock/cash_ledger.csv`
- Dividends CSV, for example `data/mock/dividends.csv`
- FX rates CSV, for example `data/mock/fx_rates.csv`
- Output paths, usually `outputs/reconciliation-report.md`,
  `outputs/return-candidates.csv`, and `outputs/reconciliation-summary.json`

Ask for missing paths, date ranges, currency choices, or basis choices before
calculating. Use sample paths only for this Skillathon repository.

## Output

Generate a markdown `Stock Return Reconciliation Report` with:
- Scope and data sources
- Input validation summary
- Return methodology
- Portfolio-level reconciliation
- Security-level reconciliation
- Return candidates
- Difference drivers
- Data quality warnings
- Manual checks and skipped checks
- Limitations and safety notes

## Workflow

1. Confirm the data is mock, public, or sanitized.
2. Validate required files and columns using `references/data-schema.md`.
3. Confirm return basis, period dates, currency handling, and tolerance rules.
4. Calculate returns using `references/return-methodology.md`.
5. Apply reconciliation checks from `references/reconciliation-rules.md`.
6. Draft the report using `references/output-format.md`.
7. Validate the result using `references/eval-checklist.md`.
8. List unresolved breaks, assumptions, skipped checks, and limitations.

## Guardrails

- Do not provide trade-decision, allocation, tax, or legal guidance.
- Treat calculated returns as reconciliation outputs, not performance promises.
- Use supplied prices and transactions unless the user approves another source.
- Do not expose account numbers, tax ids, credentials, or unsanitized personal data.
- Mark estimates, missing data, stale prices, and unresolved breaks clearly.
- Stop and ask for sanitized mock data if private or unsafe data appears.

## References

- `references/data-schema.md`
- `references/return-methodology.md`
- `references/reconciliation-rules.md`
- `references/output-format.md`
- `references/eval-checklist.md`
- `references/troubleshooting.md`
- `references/example-prompts.md`
