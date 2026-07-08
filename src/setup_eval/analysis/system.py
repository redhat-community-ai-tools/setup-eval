"""System-level analysis: evaluate the setup as a whole, not component-by-component."""

from __future__ import annotations

from dataclasses import dataclass, field

from setup_eval.analysis.budget import BudgetReport, analyze_budget
from setup_eval.analysis.context_utilization import (
    ContextUtilizationReport,
    analyze_context_utilization,
)
from setup_eval.analysis.dependencies import DependencyReport, analyze_dependencies
from setup_eval.analysis.triggers import TriggerReport, analyze_triggers
from setup_eval.core.types import Setup


@dataclass
class SystemReport:
    """Complete system-level analysis of a setup."""

    setup_name: str
    component_count: int
    budget: BudgetReport
    triggers: TriggerReport
    dependencies: DependencyReport
    context_utilization: ContextUtilizationReport
    findings: list[str] = field(default_factory=list)
    uncategorized_files: list[str] = field(default_factory=list)
    detected_tools: tuple[str, ...] = ()


def analyze_system(setup: Setup) -> SystemReport:
    """Run all system-level analyses on a setup."""
    budget = analyze_budget(setup)
    triggers = analyze_triggers(setup)
    dependencies = analyze_dependencies(setup)
    context_utilization = analyze_context_utilization(setup, budget)

    findings: list[str] = []

    tool_set = set(setup.detected_tools)
    tool_set.discard("Third-party modules")
    if not tool_set:
        always_label = "system instructions"
    elif tool_set == {"Cursor"}:
        always_label = "cursor rules"
    elif len(tool_set) > 1:
        always_label = "system instructions"
    elif "Gemini CLI" in tool_set:
        always_label = "GEMINI.md"
    elif "OpenCode" in tool_set:
        always_label = "AGENTS.md"
    elif "Copilot" in tool_set:
        always_label = "system instructions"
    else:
        always_label = "CLAUDE.md"

    if budget.always_loaded_ratio > 0.7:
        findings.append(
            f"Inverted budget: {budget.always_loaded_ratio:.0%} of tokens are "
            f"always-loaded ({always_label}). Most content should be in on-demand skills."
        )
    elif budget.always_loaded_ratio > 0.5:
        findings.append(
            f"Heavy always-loaded ratio: {budget.always_loaded_ratio:.0%} of tokens "
            f"are always-loaded. Consider moving content to on-demand skills."
        )

    if budget.heaviest_component_ratio > 0.5:
        findings.append(
            f"One component ({budget.heaviest_component_name}) uses "
            f"{budget.heaviest_component_ratio:.0%} of the total token budget."
        )

    for pair in triggers.overlap_pairs:
        findings.append(
            f"Trigger overlap: '{pair[0]}' and '{pair[1]}' have "
            f"{pair[2]:.0%} description similarity, may load together."
        )

    from setup_eval.core.types import ComponentType as CT

    uncategorized = [c.name for c in setup.by_type(CT.UNCATEGORIZED)]

    return SystemReport(
        setup_name=setup.name,
        component_count=len([c for c in setup.components if c.component_type != CT.UNCATEGORIZED]),
        budget=budget,
        triggers=triggers,
        dependencies=dependencies,
        context_utilization=context_utilization,
        findings=findings,
        uncategorized_files=uncategorized,
        detected_tools=setup.detected_tools,
    )
