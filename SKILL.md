---
name: skillathon-submission-skill
description: Use this skill to turn a repeated workflow into a reusable Skillathon submission with mock data, clear inputs, outputs, guardrails, and validation criteria. Do not use it with private production data or secrets.
---

# Skillathon Submission Skill

## When To Use
Use this skill when a repeated task needs to be documented so another person can run it again with similar inputs.

## Required Input
- A short problem statement
- A target user
- Mock data or a sample input file
- Expected output format
- Validation criteria

## Output
- A reusable workflow description
- A generated or example output
- A validation checklist
- Notes about limitations and human approval points

## Workflow
1. Confirm the task is narrow enough to run with mock data.
2. Inspect the input file and required fields.
3. Summarize the expected output before making changes.
4. Generate or update the output.
5. Validate the result using `references/eval-checklist.md`.
6. Report changed files, validation results, skipped checks, and remaining risks.

## Guardrails
- Do not use private customer data, company internal data, API keys, tokens, or webhook URLs.
- Use environment variable names only when secrets are required.
- Do not make external requests, commit, push, or submit without user approval.
- If input data looks sensitive, stop and ask for sanitized mock data.

## Validation Checklist
- The input is mock or sanitized data.
- The output matches the expected format.
- Required fields are present.
- Assumptions are listed.
- Skipped checks are documented.
- No secrets or sensitive data are included.

## References
- `references/data-schema.md`
- `references/eval-checklist.md`
- `references/example-prompts.md`
- `references/troubleshooting.md`
