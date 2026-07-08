"""Tests for system-level analysis."""

from __future__ import annotations

from pathlib import Path

from setup_eval.analysis.budget import analyze_budget
from setup_eval.analysis.context_utilization import (
    DEFAULT_MODELS,
    ModelSpec,
    analyze_context_utilization,
)
from setup_eval.analysis.dependencies import analyze_dependencies
from setup_eval.analysis.system import analyze_system
from setup_eval.analysis.triggers import analyze_triggers
from setup_eval.core.setup import discover_setup

FIXTURES = Path(__file__).parent / "fixtures"


class TestBudgetAnalysis:
    def test_budget_totals(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        assert budget.total_tokens > 0
        assert budget.always_loaded_tokens + budget.on_demand_tokens == budget.total_tokens

    def test_always_loaded_ratio(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        assert 0.0 <= budget.always_loaded_ratio <= 1.0

    def test_by_type_sums_to_total(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        assert sum(budget.by_type.values()) == budget.total_tokens

    def test_heaviest_component(self, setup_b_path: str) -> None:
        setup = discover_setup("b", setup_b_path)
        budget = analyze_budget(setup)
        assert budget.heaviest_component_name
        assert budget.heaviest_component_ratio > 0

    def test_setup_b_has_more_tokens(
        self,
        setup_a_path: str,
        setup_b_path: str,
    ) -> None:
        a = analyze_budget(discover_setup("a", setup_a_path))
        b = analyze_budget(discover_setup("b", setup_b_path))
        assert b.total_tokens > a.total_tokens


class TestTriggerAnalysis:
    def test_skill_counts(self, setup_b_path: str) -> None:
        setup = discover_setup("b", setup_b_path)
        triggers = analyze_triggers(setup)
        assert triggers.skill_count == 2
        assert triggers.skills_with_description == 2

    def test_missing_use_when(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        triggers = analyze_triggers(setup)
        assert "code-review" in triggers.missing_use_when

    def test_no_overlap_in_distinct_skills(self, setup_b_path: str) -> None:
        setup = discover_setup("b", setup_b_path)
        triggers = analyze_triggers(setup)
        for _, _, sim in triggers.overlap_pairs:
            assert sim >= 0.50


class TestDependencyAnalysis:
    def test_no_broken_refs_in_fixtures(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        deps = analyze_dependencies(setup)
        assert len(deps.broken_refs) == 0

    def test_finds_components(self, setup_b_path: str) -> None:
        setup = discover_setup("b", setup_b_path)
        deps = analyze_dependencies(setup)
        assert isinstance(deps.edges, list)
        assert isinstance(deps.orphan_components, list)


class TestContextUtilization:
    def test_produces_report(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        report = analyze_context_utilization(setup, budget)
        assert report.always_loaded_tokens == budget.always_loaded_tokens
        assert report.peak_tokens == budget.total_tokens
        assert len(report.models) == len(DEFAULT_MODELS)

    def test_percentages_consistent(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        report = analyze_context_utilization(setup, budget)
        for mu in report.models:
            assert 0.0 <= mu.always_loaded_pct <= 1.0
            assert 0.0 <= mu.peak_load_pct <= 1.0
            assert mu.remaining_pct >= 0.0
            assert abs(mu.peak_load_pct + mu.remaining_pct - 1.0) < 0.001

    def test_custom_models(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        custom = [ModelSpec("tiny-model", 100)]
        report = analyze_context_utilization(setup, budget, models=custom)
        assert len(report.models) == 1
        assert report.models[0].model == "tiny-model"
        assert report.models[0].peak_load_pct > 0.0

    def test_warning_flag(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        small = [ModelSpec("small", budget.total_tokens * 2)]
        report = analyze_context_utilization(setup, budget, models=small)
        assert report.models[0].warning is True

    def test_no_warning_for_large_window(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        budget = analyze_budget(setup)
        large = [ModelSpec("huge", 10_000_000)]
        report = analyze_context_utilization(setup, budget, models=large)
        assert report.models[0].warning is False


class TestSystemAnalysis:
    def test_analyze_produces_report(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        report = analyze_system(setup)
        assert report.setup_name == "a"
        assert report.component_count == len(setup.components)
        assert report.budget.total_tokens > 0
        assert len(report.context_utilization.models) > 0

    def test_findings_generated(self, setup_a_path: str) -> None:
        setup = discover_setup("a", setup_a_path)
        report = analyze_system(setup)
        assert isinstance(report.findings, list)


class TestReportOutput:
    def test_terminal_format(self, setup_a_path: str) -> None:
        from setup_eval.analysis.system import analyze_system
        from setup_eval.output.report import format_terminal

        setup = discover_setup("a", setup_a_path)
        system = analyze_system(setup)
        output = format_terminal(system, [])
        assert "Setup Assessment" in output
        assert "Token Budget" in output

    def test_json_format(self, setup_a_path: str) -> None:
        import json

        from setup_eval.analysis.system import analyze_system
        from setup_eval.output.report import format_json

        setup = discover_setup("a", setup_a_path)
        system = analyze_system(setup)
        output = format_json(system, [])
        parsed = json.loads(output)
        assert "budget" in parsed
        assert parsed["setup"] == "a"
