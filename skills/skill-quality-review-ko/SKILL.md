---
name: skill-quality-review-ko
description: Use this skill to review Korean Codex Skill drafts before sharing or submission. Evaluate reproducibility, safety, validation strength, clarity, and extensibility; identify blocker risks; propose prioritized small edits; and include break-test questions without rewriting the skill unless requested.
---

# Skill 품질 평가하기

## 사용 시점

Use this skill when a user asks to review, score, or improve a Korean Codex
Skill draft, `SKILL.md`, or skill folder before sharing or submission.

Good use cases:
- Checking whether another person can reproduce the same workflow from the
  draft.
- Reviewing safety boundaries for secrets, personal data, external requests,
  and human judgment.
- Checking whether success, failure, mock data, and revalidation are observable.
- Producing a prioritized improvement plan before editing the Skill.

Do not use this skill for:
- General document editing unrelated to Codex Skills.
- Code review where the main target is application behavior, not Skill quality.
- Running external services, webhooks, deployments, or live data calls.
- Rewriting the full Skill unless the user explicitly asks for a rewrite.

## Required Context

Read `references/input-contract.md` before evaluating completeness. If required
input is missing, mark the result as a limited evaluation instead of inventing
details.

Minimum useful input:
- Skill name or purpose
- Full `SKILL.md` text or draft
- Intended user and use case
- At least one trigger or usage example
- Expected output, success criteria, or validation method

Optional context:
- `references/`, `scripts/`, and `assets/` file list
- Mock inputs, expected outputs, or failing examples
- Existing validation commands or test results
- Known constraints, submission rules, or sensitive-data policy

## Workflow

1. Confirm input completeness.
   - If core input is missing, state what is missing and continue only as a
     limited evaluation.

2. Run a safety preflight.
   - Use `references/safety-guardrails.md`.
   - Do not echo suspected secrets, credentials, webhook URLs, private URLs, or
     personal data.
   - If unsafe data appears, classify it as a Blocker and request sanitized
     input.

3. Check trigger and scope.
   - Evaluate whether `description` alone explains when to use the Skill, when
     not to use it, and what output to expect.

4. Check the execution path.
   - Confirm that required input, user confirmation points, ordered workflow,
     references, scripts, and stopping conditions are visible.

5. Check validation strength.
   - Look for mock data, deterministic commands, expected results, failure
     criteria, skipped-check reporting, and a revalidation loop.

6. Apply the rubric.
   - Use `references/quality-rubric.md`.
   - Rate each category as `강함`, `보통`, or `위험` using observable evidence.
   - Separate confirmed findings from inference and unknowns.

7. Prioritize changes.
   - Lead with Blockers, then High, Medium, and Low improvements.
   - Keep suggestions as small edits that preserve the Skill's intended purpose.

8. Add break-test questions.
   - Use `references/break-test-questions.md`.
   - Include questions for missing input, vague triggers, sensitive data,
     external requests, human judgment, missing validation, and overbroad
     rewrites.

9. Write the final review.
   - Follow `references/output-template.md`.
   - Always include remaining risks and items that a human must verify.

## References

- `references/input-contract.md`: read first to classify complete vs limited
  evaluations.
- `references/quality-rubric.md`: read before assigning `강함`, `보통`, or
  `위험`.
- `references/safety-guardrails.md`: read during safety preflight and when the
  draft mentions secrets, personal data, external requests, or expert judgment.
- `references/output-template.md`: read before writing the final review.
- `references/break-test-questions.md`: read before proposing adversarial test
  questions.
- `references/examples.md`: read when the user needs examples of good and weak
  Skill patterns.

## Validation

If this Skill package is being changed, run:

```sh
python3 skills/skill-quality-review-ko/scripts/validate_skill_review_pack.py
```

Report the command result, skipped checks, and any remaining manual review items.
