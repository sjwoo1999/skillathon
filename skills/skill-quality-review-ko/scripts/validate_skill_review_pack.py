#!/usr/bin/env python3
"""Validate the Korean skill quality review pack structure."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_REFERENCES = (
    "references/break-test-questions.md",
    "references/examples.md",
    "references/input-contract.md",
    "references/output-template.md",
    "references/quality-rubric.md",
    "references/safety-guardrails.md",
)

REQUIRED_SKILL_HEADINGS = (
    "사용 시점",
    "Required Context",
    "Workflow",
    "References",
    "Validation",
)

REQUIRED_SKILL_KEYWORD_GROUPS = (
    ("초안", "draft"),
    ("description",),
    ("비밀", "secret", "민감정보"),
    ("승인", "approval", "confirmation"),
    ("판단", "judgment", "human"),
    ("검증", "validation"),
    ("재작성", "rewrite"),
)

BREAK_TEST_KEYWORDS = (
    "missing draft",
    "vague description",
    "secret leak",
    "external request without approval",
    "human judgment",
    "missing validation",
    "overbroad rewrite",
)

EXAMPLE_KEYWORDS = (
    "좋은 예",
    "나쁜 예",
    "기대 판단",
    "description",
    "승인",
    "검증",
    "비밀",
)

INPUT_CONTRACT_KEYWORDS = (
    "필수 입력",
    "선택 입력",
    "입력이 부족",
    "제한 평가",
    "증거",
    "추론",
)

OUTPUT_TEMPLATE_KEYWORDS = (
    "총평",
    "루브릭",
    "Blocker",
    "Warning",
    "Improvement",
    "재검증",
    "사람",
)

QUALITY_RUBRIC_KEYWORDS = (
    "사용 조건",
    "입력 계약",
    "작업 절차",
    "안전성",
    "검증 가능성",
    "명확성",
    "확장성",
    "강함",
    "보통",
    "위험",
)

SAFETY_GUARDRAIL_KEYWORDS = (
    "Secret",
    "PII",
    "외부 요청",
    "인간 판단",
    "중단",
    "재노출 금지",
)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"Missing required file: {path}")
    except UnicodeDecodeError as exc:
        errors.append(f"File is not valid UTF-8: {path} ({exc})")
    except OSError as exc:
        errors.append(f"Could not read file: {path} ({exc})")
    return ""


def parse_frontmatter(text: str, skill_path: Path, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        errors.append(f"{skill_path}: missing YAML frontmatter starting with ---")
        return {}

    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{skill_path}: missing closing --- for frontmatter")
        return {}

    frontmatter: dict[str, str] = {}
    for line_number, line in enumerate(text[4:end].splitlines(), start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            errors.append(f"{skill_path}:{line_number}: invalid frontmatter line: {line}")
            continue
        key, value = stripped.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip("\"'")
    return frontmatter


def require_nonempty_frontmatter(
    frontmatter: dict[str, str], skill_path: Path, errors: list[str]
) -> None:
    for key in ("name", "description"):
        value = frontmatter.get(key, "")
        if not value:
            errors.append(f"{skill_path}: frontmatter field '{key}' is required")
            continue
        if key == "description" and len(value.split()) < 8:
            errors.append(f"{skill_path}: frontmatter description is too short or vague")


def require_links(text: str, skill_path: Path, errors: list[str]) -> None:
    for relative_path in REQUIRED_REFERENCES:
        if relative_path not in text:
            errors.append(f"{skill_path}: must link to {relative_path}")


def require_markdown_headings(
    text: str, path: Path, required_headings: tuple[str, ...], errors: list[str]
) -> None:
    headings = set()
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE):
        headings.add(match.group(1).strip().lower())

    for heading in required_headings:
        if heading.lower() not in headings:
            errors.append(f"{path}: missing required heading '{heading}'")


def require_keywords(
    text: str, path: Path, keywords: tuple[str, ...], errors: list[str]
) -> None:
    lowered = text.lower()
    for keyword in keywords:
        if keyword.lower() not in lowered:
            errors.append(f"{path}: missing required keyword '{keyword}'")


def require_keyword_groups(
    text: str, path: Path, keyword_groups: tuple[tuple[str, ...], ...], errors: list[str]
) -> None:
    lowered = text.lower()
    for group in keyword_groups:
        if not any(keyword.lower() in lowered for keyword in group):
            joined = " or ".join(repr(keyword) for keyword in group)
            errors.append(f"{path}: missing required keyword {joined}")


def validate_pack(root: Path) -> list[str]:
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    skill_text = read_text(skill_path, errors)

    for relative_path in REQUIRED_REFERENCES:
        read_text(root / relative_path, errors)

    if skill_text:
        frontmatter = parse_frontmatter(skill_text, skill_path, errors)
        require_nonempty_frontmatter(frontmatter, skill_path, errors)
        require_links(skill_text, skill_path, errors)
        require_markdown_headings(skill_text, skill_path, REQUIRED_SKILL_HEADINGS, errors)
        require_keyword_groups(
            skill_text, skill_path, REQUIRED_SKILL_KEYWORD_GROUPS, errors
        )

    break_test_path = root / "references/break-test-questions.md"
    break_test_text = read_text(break_test_path, errors)
    if break_test_text:
        require_keywords(break_test_text, break_test_path, BREAK_TEST_KEYWORDS, errors)

    examples_path = root / "references/examples.md"
    examples_text = read_text(examples_path, errors)
    if examples_text:
        require_keywords(examples_text, examples_path, EXAMPLE_KEYWORDS, errors)

    input_contract_path = root / "references/input-contract.md"
    input_contract_text = read_text(input_contract_path, errors)
    if input_contract_text:
        require_keywords(
            input_contract_text, input_contract_path, INPUT_CONTRACT_KEYWORDS, errors
        )

    output_template_path = root / "references/output-template.md"
    output_template_text = read_text(output_template_path, errors)
    if output_template_text:
        require_keywords(
            output_template_text, output_template_path, OUTPUT_TEMPLATE_KEYWORDS, errors
        )

    quality_rubric_path = root / "references/quality-rubric.md"
    quality_rubric_text = read_text(quality_rubric_path, errors)
    if quality_rubric_text:
        require_keywords(
            quality_rubric_text, quality_rubric_path, QUALITY_RUBRIC_KEYWORDS, errors
        )

    safety_guardrails_path = root / "references/safety-guardrails.md"
    safety_guardrails_text = read_text(safety_guardrails_path, errors)
    if safety_guardrails_text:
        require_keywords(
            safety_guardrails_text,
            safety_guardrails_path,
            SAFETY_GUARDRAIL_KEYWORDS,
            errors,
        )

    return errors


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the skill-quality-review-ko pack."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=default_root(),
        help="Skill pack root directory. Defaults to this script's parent skill directory.",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    errors = validate_pack(root)
    if errors:
        print("Skill review pack validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Skill review pack validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
