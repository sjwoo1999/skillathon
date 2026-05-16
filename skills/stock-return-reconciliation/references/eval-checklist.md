# Evaluation Checklist

Use this checklist before submitting the skill output or rerunning the workflow.

## Skillathon Requirements

- [ ] `SKILL.md` gives a reusable workflow.
- [ ] Reference files explain schema, methodology, rules, output, validation,
  troubleshooting, and example prompts.
- [ ] The workflow can run on mock or sanitized data.
- [ ] Validation steps are explicit and repeatable.
- [ ] Safety guardrails are visible in the skill and report.
- [ ] The report does not provide investment, trading, tax, legal, or accounting
  advice.

## Input Validation

- [ ] All required input files are present or missing files are listed.
- [ ] Required columns from `data-schema.md` are present.
- [ ] Dates parse as ISO `YYYY-MM-DD`.
- [ ] Numeric fields parse consistently.
- [ ] Account, security, and period keys join across files.
- [ ] Holdings include period start and period end.
- [ ] Prices cover each held or traded security.
- [ ] Reported returns use the requested period or differences are flagged.

## Privacy and Safety

- [ ] Inputs are mock, public, or confirmed sanitized.
- [ ] No full account numbers, tax ids, API keys, passwords, or private URLs are
  copied into the report.
- [ ] Real client or household names are absent or masked.
- [ ] The output contains the required no-advice safety note.
- [ ] The output avoids future-performance claims.
- [ ] The output avoids trade-decision, allocation, or tax-treatment guidance.

## Methodology

- [ ] Return basis is identified as TWR, MWR, simple, source-reported, or
  unknown.
- [ ] External cash flow treatment is documented.
- [ ] Income, fees, taxes, and corporate actions are classified.
- [ ] Currency basis is documented.
- [ ] Price adjustment basis is documented.
- [ ] Rounding and tolerance are stated.
- [ ] Incompatible methods are marked `Not Comparable` instead of forced to pass
  or fail.

## Reconciliation Quality

- [ ] Share quantities reconcile from beginning to ending holdings, or breaks
  are listed.
- [ ] Market values reconcile to supplied prices, or breaks are listed.
- [ ] Portfolio-level calculated returns are compared with reported returns.
- [ ] Security-level calculated returns are compared where data supports it.
- [ ] Return differences are shown in basis points.
- [ ] Each break has a likely cause or `unknown` cause.
- [ ] Material missing data appears in the exception log.

## Output Quality

- [ ] The report follows `output-format.md`.
- [ ] Tables are readable in markdown.
- [ ] Assumptions and limitations are explicit.
- [ ] Skipped checks are listed.
- [ ] The executive summary does not overstate certainty.
- [ ] Calculations are auditable from source fields.

## Manual Validation Commands

This documentation change does not modify scripts, but the Skillathon package
includes deterministic validation and reconciliation scripts.

Useful manual checks:

```bash
find skills/stock-return-reconciliation -maxdepth 2 -type f | sort
python3 skills/stock-return-reconciliation/scripts/validate_sample.py
python3 skills/stock-return-reconciliation/scripts/reconcile_returns.py
```

## Pass Criteria

The skill output passes evaluation when:

- It can be run by another user with only the skill docs and mock input files.
- It produces a structured markdown reconciliation report.
- It identifies validation failures before relying on calculations.
- It distinguishes method differences from true data breaks.
- It includes safety notes and avoids prohibited advice.
