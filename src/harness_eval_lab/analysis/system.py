"""System-level analysis: evaluate the setup as a whole, not component-by-component."""

from __future__ import annotations

from dataclasses import dataclass, field

from harness_eval_lab.analysis.budget import BudgetReport, analyze_budget
from harness_eval_lab.analysis.context_utilization import (
    ALWAYS_LOADED_WARNING_THRESHOLD,
    PEAK_CRITICAL_THRESHOLD,
    PEAK_WARNING_THRESHOLD,
    ContextUtilizationReport,
    analyze_context_utilization,
)
from harness_eval_lab.analysis.dependencies import DependencyReport, analyze_dependencies
from harness_eval_lab.analysis.triggers import TriggerReport, analyze_triggers
from harness_eval_lab.core.types import Setup


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

    if "Cursor" in setup.detected_tools and "Claude Code" not in setup.detected_tools:
        always_label = "cursor rules"
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

    seen_windows: dict[int, list[str]] = {}
    for mu in context_utilization.models:
        seen_windows.setdefault(mu.context_window, []).append(mu.model)

    for window, names in sorted(seen_windows.items()):
        representative = next(
            mu for mu in context_utilization.models if mu.context_window == window
        )
        label = names[0] if len(names) == 1 else f"{names[0]} and {len(names) - 1} others"
        if representative.peak_load_pct > PEAK_CRITICAL_THRESHOLD:
            findings.append(
                f"Context critical: setup uses {representative.peak_load_pct:.0%} "
                f"of {label}'s {window:,}-token window."
            )
        elif representative.peak_load_pct > PEAK_WARNING_THRESHOLD:
            findings.append(
                f"Context pressure: setup uses {representative.peak_load_pct:.0%} "
                f"of {label}'s {window:,}-token window."
            )
        if representative.always_loaded_pct > ALWAYS_LOADED_WARNING_THRESHOLD:
            findings.append(
                f"Always-loaded pressure on {label}: "
                f"{representative.always_loaded_pct:.0%} of context consumed "
                f"before any skill loads."
            )

    from harness_eval_lab.core.types import ComponentType as CT

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
