"""Tests for SARIF v2.1.0 output format."""

from __future__ import annotations

from setup_eval.inspection.types import (
    Finding,
    FixSuggestion,
    InspectionResult,
    Location,
    RuleCategory,
    Severity,
)
from setup_eval.output.metadata import EvalMetadata
from setup_eval.output.sarif import SARIF_SCHEMA, SARIF_VERSION, format_sarif


def _make_finding(
    rule_id: str = "test/rule",
    severity: Severity = Severity.WARNING,
    message: str = "test message",
    file: str = "CLAUDE.md",
    line: int | None = 1,
    category: RuleCategory = RuleCategory.CONTENT,
    fix: FixSuggestion | None = None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        location=Location(file=file, start_line=line),
        category=category,
        fix=fix,
    )


def _make_result(findings: list[Finding]) -> list[InspectionResult]:
    return [
        InspectionResult(
            target_path="test",
            target_name="test",
            tokens=0,
            diagnostics=findings,
            error_count=sum(1 for f in findings if f.severity == Severity.ERROR),
            warning_count=sum(1 for f in findings if f.severity == Severity.WARNING),
        )
    ]


class TestSarifStructure:
    def test_empty_results(self) -> None:
        sarif = format_sarif([], None)
        assert sarif["$schema"] == SARIF_SCHEMA
        assert sarif["version"] == SARIF_VERSION
        assert len(sarif["runs"]) == 1
        assert sarif["runs"][0]["results"] == []
        assert sarif["runs"][0]["tool"]["driver"]["rules"] == []

    def test_schema_and_version(self) -> None:
        findings = [_make_finding()]
        sarif = format_sarif(_make_result(findings))
        assert sarif["$schema"] == SARIF_SCHEMA
        assert sarif["version"] == SARIF_VERSION

    def test_tool_driver_info(self) -> None:
        meta = EvalMetadata(version="1.2.3")
        sarif = format_sarif([], meta)
        driver = sarif["runs"][0]["tool"]["driver"]
        assert driver["name"] == "setup-eval"
        assert driver["version"] == "1.2.3"
        assert "setup-eval" in driver["informationUri"]

    def test_version_defaults_to_dev(self) -> None:
        sarif = format_sarif([], None)
        assert sarif["runs"][0]["tool"]["driver"]["version"] == "dev"


class TestSeverityMapping:
    def test_error_maps_to_error(self) -> None:
        findings = [_make_finding(severity=Severity.ERROR)]
        sarif = format_sarif(_make_result(findings))
        assert sarif["runs"][0]["results"][0]["level"] == "error"

    def test_warning_maps_to_warning(self) -> None:
        findings = [_make_finding(severity=Severity.WARNING)]
        sarif = format_sarif(_make_result(findings))
        assert sarif["runs"][0]["results"][0]["level"] == "warning"

    def test_info_maps_to_note(self) -> None:
        findings = [_make_finding(severity=Severity.INFO)]
        sarif = format_sarif(_make_result(findings))
        assert sarif["runs"][0]["results"][0]["level"] == "note"


class TestResultFields:
    def test_rule_id_and_message(self) -> None:
        findings = [_make_finding(rule_id="security/injection", message="bad pattern")]
        sarif = format_sarif(_make_result(findings))
        result = sarif["runs"][0]["results"][0]
        assert result["ruleId"] == "security/injection"
        assert result["message"]["text"] == "bad pattern"

    def test_location(self) -> None:
        findings = [_make_finding(file="skills/my-skill/SKILL.md", line=42)]
        sarif = format_sarif(_make_result(findings))
        loc = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"] == "skills/my-skill/SKILL.md"
        assert loc["region"]["startLine"] == 42

    def test_location_defaults_line_to_1(self) -> None:
        findings = [_make_finding(line=None)]
        sarif = format_sarif(_make_result(findings))
        loc = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
        assert loc["region"]["startLine"] == 1

    def test_fix_included_when_present(self) -> None:
        fix = FixSuggestion(description="Add description field")
        findings = [_make_finding(fix=fix)]
        sarif = format_sarif(_make_result(findings))
        result = sarif["runs"][0]["results"][0]
        assert result["fixes"][0]["description"]["text"] == "Add description field"

    def test_no_fix_key_when_absent(self) -> None:
        findings = [_make_finding(fix=None)]
        sarif = format_sarif(_make_result(findings))
        result = sarif["runs"][0]["results"][0]
        assert "fixes" not in result


class TestRuleDescriptors:
    def test_rules_deduplicated(self) -> None:
        findings = [
            _make_finding(rule_id="a/rule", message="first"),
            _make_finding(rule_id="a/rule", message="second"),
            _make_finding(rule_id="b/rule", message="third"),
        ]
        sarif = format_sarif(_make_result(findings))
        rules = sarif["runs"][0]["tool"]["driver"]["rules"]
        assert len(rules) == 2
        assert rules[0]["id"] == "a/rule"
        assert rules[1]["id"] == "b/rule"

    def test_rule_index_matches(self) -> None:
        findings = [
            _make_finding(rule_id="first/rule"),
            _make_finding(rule_id="second/rule"),
        ]
        sarif = format_sarif(_make_result(findings))
        results = sarif["runs"][0]["results"]
        assert results[0]["ruleIndex"] == 0
        assert results[1]["ruleIndex"] == 1

    def test_category_in_tags(self) -> None:
        findings = [_make_finding(category=RuleCategory.SECURITY)]
        sarif = format_sarif(_make_result(findings))
        rule = sarif["runs"][0]["tool"]["driver"]["rules"][0]
        assert "security" in rule["properties"]["tags"]


class TestMultipleInspectionResults:
    def test_findings_from_multiple_results_merged(self) -> None:
        results = [
            InspectionResult(
                target_path="a",
                target_name="a",
                tokens=0,
                diagnostics=[_make_finding(rule_id="rule/a")],
                error_count=0,
                warning_count=1,
            ),
            InspectionResult(
                target_path="b",
                target_name="b",
                tokens=0,
                diagnostics=[_make_finding(rule_id="rule/b")],
                error_count=0,
                warning_count=1,
            ),
        ]
        sarif = format_sarif(results)
        assert len(sarif["runs"][0]["results"]) == 2
        assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == 2
