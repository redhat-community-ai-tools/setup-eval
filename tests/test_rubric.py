"""Tests for rubric issue detection with mocked LLM."""

from __future__ import annotations

import json
import textwrap

from setup_eval.rubric.scorer import RubricChecker


class MockLLMWithIssues:
    def generate(self, system: str, prompt: str) -> str:
        return (
            "ISSUE: Vague instructions in lines 5-8 | CATEGORY: specificity | EVIDENCE: 'be thorough and helpful' is generic advice | SUGGESTION: Replace with concrete patterns like 'always use raise from'\n"
            "ISSUE: Duplicates Claude default | CATEGORY: redundancy | EVIDENCE: 'write clean code' on line 3 | SUGGESTION: Remove this line\n"
            "SUMMARY: Skill has specificity and redundancy issues."
        )


class MockLLMClean:
    def generate(self, system: str, prompt: str) -> str:
        return "SUMMARY: Well-built skill with no issues."


def test_rubric_checker_finds_issues() -> None:
    checker = RubricChecker(MockLLMWithIssues())
    result = checker.check(
        component_type="skill",
        component_name="code-review",
        content="---\nname: code-review\ndescription: Review code\n---\n\nReview code.",
    )

    assert result.component_name == "code-review"
    assert result.component_type == "skill"
    assert len(result.issues) == 2
    assert result.issues[0].category == "specificity"
    assert result.issues[0].description == "Vague instructions in lines 5-8"
    assert result.issues[0].evidence
    assert result.issues[0].suggestion
    assert result.issues[1].category == "redundancy"
    assert result.summary


def test_rubric_checker_clean_component() -> None:
    checker = RubricChecker(MockLLMClean())
    result = checker.check(
        component_type="skill",
        component_name="good-skill",
        content="---\nname: good-skill\ndescription: Does something unique\n---\n\nSpecific instructions.",
    )

    assert result.issues == []
    assert "no issues" in result.summary.lower()


def test_rubric_checker_unknown_type() -> None:
    checker = RubricChecker(MockLLMClean())
    result = checker.check(
        component_type="unknown_thing",
        component_name="test",
        content="test content",
    )

    assert result.issues == []
    assert "No issue categories" in result.summary


def test_rubric_issue_fields() -> None:
    checker = RubricChecker(MockLLMWithIssues())
    result = checker.check(
        component_type="skill",
        component_name="test",
        content="test content",
    )

    for issue in result.issues:
        assert issue.category
        assert issue.description
        assert issue.evidence
        assert issue.suggestion
        assert issue.severity == "warning"


class MockLLMWithJSON:
    """Returns a JSON-formatted response with issues."""

    def generate(self, system: str, prompt: str) -> str:
        data = {
            "issues": [
                {
                    "description": "Vague instructions in lines 5-8",
                    "category": "specificity",
                    "severity": "warning",
                    "evidence": "'be thorough and helpful' is generic advice",
                    "suggestion": "Replace with concrete patterns",
                },
                {
                    "description": "References nonexistent script",
                    "category": "script_integrity",
                    "severity": "error",
                    "evidence": "Run ./scripts/deploy.sh but file does not exist",
                    "suggestion": "Create the script or remove the reference",
                },
            ],
            "summary": "Component has two fixable issues.",
            "verdict": "REVIEW",
        }
        return "```json\n" + json.dumps(data, indent=2) + "\n```"


class MockLLMWithRawJSON:
    """Returns a raw JSON object (no fences)."""

    def generate(self, system: str, prompt: str) -> str:
        data = {
            "issues": [],
            "summary": "Well-structured skill with no issues.",
            "verdict": "KEEP",
        }
        return json.dumps(data, indent=2)


def test_json_response_parsed_correctly() -> None:
    """JSON responses should be parsed as the primary format."""
    checker = RubricChecker(MockLLMWithJSON())
    result = checker.check(
        component_type="skill",
        component_name="json-skill",
        content="---\nname: json-skill\n---\nSome content.",
    )

    assert result.component_name == "json-skill"
    assert len(result.issues) == 2
    assert result.issues[0].category == "specificity"
    assert result.issues[0].severity == "warning"
    assert result.issues[0].description == "Vague instructions in lines 5-8"
    assert result.issues[0].evidence == "'be thorough and helpful' is generic advice"
    assert result.issues[0].suggestion == "Replace with concrete patterns"
    assert result.issues[1].category == "script_integrity"
    assert result.issues[1].severity == "error"
    assert result.summary == "Component has two fixable issues."
    assert result.verdict == "REVIEW"


def test_raw_json_response_parsed_correctly() -> None:
    """Raw JSON (without fences) should also be parsed."""
    checker = RubricChecker(MockLLMWithRawJSON())
    result = checker.check(
        component_type="skill",
        component_name="raw-json-skill",
        content="---\nname: raw-json\n---\nContent.",
    )

    assert result.issues == []
    assert result.summary == "Well-structured skill with no issues."
    assert result.verdict == "KEEP"


def test_text_response_still_works() -> None:
    """Text (regex) responses should still be parsed correctly (backward compat)."""
    checker = RubricChecker(MockLLMWithIssues())
    result = checker.check(
        component_type="skill",
        component_name="text-skill",
        content="---\nname: text-skill\n---\nContent.",
    )

    assert len(result.issues) == 2
    assert result.issues[0].category == "specificity"
    assert result.issues[1].category == "redundancy"
    assert result.summary


def test_invalid_json_falls_back_to_regex() -> None:
    """If the response contains broken JSON, regex parsing should kick in."""

    class MockLLMBrokenJSON:
        def generate(self, system: str, prompt: str) -> str:
            return textwrap.dedent("""\
                ```json
                {this is not valid json}
                ```
                ISSUE: Some problem | CATEGORY: redundancy | SEVERITY: warning | EVIDENCE: line 3 | SUGGESTION: Fix it
                VERDICT: REVIEW
                SUMMARY: Fallback worked.
            """)

    checker = RubricChecker(MockLLMBrokenJSON())
    result = checker.check(
        component_type="skill",
        component_name="fallback-skill",
        content="content",
    )

    assert len(result.issues) == 1
    assert result.issues[0].category == "redundancy"
    assert result.verdict == "REVIEW"
    assert result.summary == "Fallback worked."
