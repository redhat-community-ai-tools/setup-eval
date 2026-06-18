"""Token budget analysis for the setup as a whole."""

from __future__ import annotations

from dataclasses import dataclass, field

from harness_eval_lab.core.types import ComponentType, ParsedComponent, Setup


@dataclass
class BudgetReport:
    """Token budget breakdown for a setup."""

    total_tokens: int = 0
    always_loaded_tokens: int = 0
    on_demand_tokens: int = 0
    always_loaded_ratio: float = 0.0
    by_type: dict[str, int] = field(default_factory=dict)
    by_component: list[tuple[str, str, int]] = field(default_factory=list)
    heaviest_component_name: str = ""
    heaviest_component_ratio: float = 0.0


_EXCLUDED_FROM_BUDGET = {ComponentType.UNCATEGORIZED}


def _is_always_loaded(comp: ParsedComponent) -> bool:
    if comp.component_type == ComponentType.HOOKS:
        return True
    if comp.component_type != ComponentType.CLAUDE_MD:
        return False
    if comp.source_tool != "cursor":
        return True
    return bool(comp.frontmatter and comp.frontmatter.get("alwaysApply") is True)


def analyze_budget(setup: Setup) -> BudgetReport:
    """Analyze token budget distribution across a setup."""
    by_type: dict[str, int] = {}
    by_component: list[tuple[str, str, int]] = []
    always_loaded = 0
    on_demand = 0
    heaviest_name = ""
    heaviest_tokens = 0

    for comp in setup.components:
        if comp.component_type in _EXCLUDED_FROM_BUDGET:
            continue
        type_key = comp.component_type.value
        by_type[type_key] = by_type.get(type_key, 0) + comp.token_count
        by_component.append((type_key, comp.name, comp.token_count))

        if _is_always_loaded(comp):
            always_loaded += comp.token_count
        else:
            on_demand += comp.token_count

        if comp.token_count > heaviest_tokens:
            heaviest_tokens = comp.token_count
            heaviest_name = f"{type_key}/{comp.name}"

    total = always_loaded + on_demand
    by_component.sort(key=lambda x: x[2], reverse=True)

    return BudgetReport(
        total_tokens=total,
        always_loaded_tokens=always_loaded,
        on_demand_tokens=on_demand,
        always_loaded_ratio=always_loaded / total if total else 0.0,
        by_type=by_type,
        by_component=by_component,
        heaviest_component_name=heaviest_name,
        heaviest_component_ratio=heaviest_tokens / total if total else 0.0,
    )
