"""Report generation: structured output for assess results."""

from __future__ import annotations

import json
from collections import defaultdict

from harness_eval_lab.analysis.system import SystemReport
from harness_eval_lab.inspection.types import InspectionResult


def _get_type_display(detected_tools: tuple[str, ...] = ()) -> dict[str, str]:
    base = {
        "skill": "Skills",
        "command": "Commands",
        "hooks": "Hooks",
        "agent": "Agents",
        "rule": "Rules",
        "output_style": "Output Styles",
    }
    if "Cursor" in detected_tools and "Claude Code" not in detected_tools:
        base["claude_md"] = "Cursor Rules"
    elif "Claude Code" in detected_tools and "Cursor" not in detected_tools:
        base["claude_md"] = "CLAUDE.md"
    elif "Cursor" in detected_tools and "Claude Code" in detected_tools:
        base["claude_md"] = "System Instructions"
    else:
        base["claude_md"] = "CLAUDE.md"
    return base


_TYPE_ORDER = ["skill", "command", "hooks", "claude_md", "agent", "rule", "output_style"]


def _shorten_rule_id(rule_id: str) -> str:
    parts = rule_id.split("/", 1)
    return parts[1] if len(parts) > 1 else rule_id


def _compress_findings(diagnostics: list) -> list[str]:
    """Group identical rule findings into compressed lines."""
    by_rule: dict[str, list] = defaultdict(list)
    for d in diagnostics:
        by_rule[d.rule_id].append(d)

    compressed: list[str] = []
    for rule_id, findings in by_rule.items():
        severity = findings[0].severity.value
        label = "FAIL" if severity == "error" else "WARNING"
        short_id = _shorten_rule_id(rule_id)
        if len(findings) <= 2:
            for d in findings:
                compressed.append(f"  {label:<8} {short_id}: {d.message}")
        else:
            compressed.append(f"  {label:<8} {short_id}: {len(findings)} findings")
            for d in findings:
                compressed.append(f"           {d.message}")
    return compressed


def format_terminal(
    system: SystemReport,
    inspection_results: list[InspectionResult],
) -> str:
    """Format a full assessment report for terminal output."""
    lines: list[str] = []

    lines.append(f"{'=' * 60}")
    lines.append(f"Setup Assessment: {system.setup_name}")
    lines.append(f"{'=' * 60}")
    if system.detected_tools:
        lines.append(f"Detected tools: {', '.join(system.detected_tools)}")
    lines.append(f"Components: {system.component_count}")
    lines.append(f"Total tokens: {system.budget.total_tokens}")
    lines.append("")

    lines.append("Legend:")
    lines.append(f"{'─' * 60}")
    lines.append("  PASS     Rule checked, no issues found")
    lines.append("  FAIL     Rule checked, error found (must fix)")
    lines.append("  WARNING  Rule checked, potential issue (should review)")
    lines.append("  SKIP     Check was skipped (missing dependency or N/A)")
    lines.append("")

    if "Cursor" in system.detected_tools and "Claude Code" not in system.detected_tools:
        always_label = "cursor rules, hooks"
    else:
        always_label = "CLAUDE.md, hooks"

    lines.append("Token Budget:")
    lines.append(f"{'─' * 60}")
    lines.append(
        f"  Always-loaded ({always_label}): "
        f"{system.budget.always_loaded_tokens} tokens "
        f"({system.budget.always_loaded_ratio:.0%})"
    )
    lines.append(
        f"  On-demand (skills, commands, agents): "
        f"{system.budget.on_demand_tokens} tokens "
        f"({1 - system.budget.always_loaded_ratio:.0%})"
    )
    if system.budget.by_type:
        lines.append("  By type:")
        for type_name, tokens in sorted(
            system.budget.by_type.items(), key=lambda x: x[1], reverse=True
        ):
            pct = tokens / system.budget.total_tokens * 100 if system.budget.total_tokens else 0
            lines.append(f"    {type_name:<12} {tokens:>6} tokens ({pct:.0f}%)")

    if system.triggers.skill_count > 0:
        lines.append("")
        lines.append("Trigger Analysis:")
        lines.append(f"{'─' * 60}")
        lines.append(
            f"  {system.triggers.skills_with_description}/{system.triggers.skill_count} "
            f"skills have descriptions"
        )
        if system.triggers.missing_use_when:
            lines.append(
                f"  {len(system.triggers.missing_use_when)} skills lack "
                f"activation context ('use when' phrasing):"
            )
            for name in system.triggers.missing_use_when:
                lines.append(f"    - {name}")
        if system.triggers.overlap_pairs:
            lines.append(f"  {len(system.triggers.overlap_pairs)} trigger overlap(s) detected:")
            for name_a, name_b, sim in system.triggers.overlap_pairs:
                lines.append(f"    - {name_a} <-> {name_b} ({sim:.0%} similar)")

    if system.dependencies.broken_refs:
        lines.append("")
        lines.append("Dependencies:")
        lines.append(f"{'─' * 60}")
        lines.append(f"  {len(system.dependencies.broken_refs)} broken reference(s):")
        for edge in system.dependencies.broken_refs:
            lines.append(
                f"    - {edge.source_type}/{edge.source_name} "
                f"references missing {edge.target_type}/{edge.target_name}"
            )

    if system.findings:
        lines.append("")
        lines.append("Findings:")
        lines.append(f"{'─' * 60}")
        for finding in system.findings:
            lines.append(f"  WARNING  {finding}")

    total_errors = sum(r.error_count for r in inspection_results)
    total_warnings = sum(r.warning_count for r in inspection_results)
    if inspection_results:
        lines.append("")
        lines.append("Inspection Results:")
        lines.append(f"{'─' * 60}")
        lines.append(
            f"  {len(inspection_results)} components inspected, "
            f"{total_errors} errors, {total_warnings} warnings"
        )

        grouped: dict[str, list[InspectionResult]] = defaultdict(list)
        for r in inspection_results:
            grouped[r.target_type].append(r)

        all_type_keys = [k for k in _TYPE_ORDER if k in grouped]
        all_type_keys += [k for k in grouped if k not in _TYPE_ORDER]

        for type_key in all_type_keys:
            results = grouped[type_key]
            label = _get_type_display(system.detected_tools).get(type_key, type_key)
            lines.append("")
            lines.append(f"  {label} ({len(results)})")
            lines.append(f"  {'─' * 56}")
            for r in results:
                if not r.diagnostics:
                    if r.rules_run:
                        rule_names = ", ".join(_shorten_rule_id(rr.rule_id) for rr in r.rules_run)
                        lines.append(f"    {r.target_name:<40} PASS ({len(r.rules_run)} rules)")
                        lines.append(f"      checked: {rule_names}")
                    else:
                        lines.append(f"    {r.target_name:<40} PASS")
                else:
                    parts = []
                    if r.error_count:
                        parts.append(f"{r.error_count} error{'s' if r.error_count != 1 else ''}")
                    if r.warning_count:
                        parts.append(
                            f"{r.warning_count} warning{'s' if r.warning_count != 1 else ''}"
                        )
                    status = ", ".join(parts)
                    lines.append(f"    {r.target_name:<40} {status}")
                    for cline in _compress_findings(r.diagnostics):
                        lines.append(f"      {cline}")

    if system.uncategorized_files:
        lines.append("")
        lines.append("Uncategorized Files (discovered but no rules apply yet):")
        lines.append(f"{'─' * 60}")
        for f in system.uncategorized_files:
            lines.append(f"  {f}")

    lines.append("")
    return "\n".join(lines)


def _build_json_inspection(inspection_results: list[InspectionResult]) -> dict:
    total_errors = sum(r.error_count for r in inspection_results)
    total_warnings = sum(r.warning_count for r in inspection_results)

    grouped: dict[str, list[InspectionResult]] = defaultdict(list)
    for r in inspection_results:
        grouped[r.target_type].append(r)

    result: dict = {
        "summary": {
            "total": len(inspection_results),
            "errors": total_errors,
            "warnings": total_warnings,
        },
    }

    all_type_keys = [k for k in _TYPE_ORDER if k in grouped]
    all_type_keys += [k for k in grouped if k not in _TYPE_ORDER]

    for type_key in all_type_keys:
        result[type_key] = [
            {
                "name": r.target_name,
                "status": "pass" if not r.diagnostics else "fail",
                "errors": r.error_count,
                "warnings": r.warning_count,
                "rules": [
                    {
                        "rule": rr.rule_id,
                        "result": "pass" if rr.passed else "fail",
                    }
                    for rr in r.rules_run
                ],
                "findings": [
                    {
                        "rule": d.rule_id,
                        "severity": d.severity.value,
                        "message": d.message,
                    }
                    for d in r.diagnostics
                ],
            }
            for r in grouped[type_key]
        ]

    return result


def format_json(
    system: SystemReport,
    inspection_results: list[InspectionResult],
) -> str:
    """Format a full assessment report as JSON."""
    output = {
        "setup": system.setup_name,
        "detected_tools": list(system.detected_tools),
        "component_count": system.component_count,
        "budget": {
            "total_tokens": system.budget.total_tokens,
            "always_loaded": system.budget.always_loaded_tokens,
            "on_demand": system.budget.on_demand_tokens,
            "always_loaded_ratio": round(system.budget.always_loaded_ratio, 2),
            "by_type": system.budget.by_type,
            "heaviest": system.budget.heaviest_component_name,
        },
        "triggers": {
            "skill_count": system.triggers.skill_count,
            "with_description": system.triggers.skills_with_description,
            "missing_use_when": system.triggers.missing_use_when,
            "overlaps": [
                {"a": a, "b": b, "similarity": round(s, 2)}
                for a, b, s in system.triggers.overlap_pairs
            ],
        },
        "dependencies": {
            "total_edges": len(system.dependencies.edges),
            "broken": [
                {
                    "source": f"{e.source_type}/{e.source_name}",
                    "target": f"{e.target_type}/{e.target_name}",
                }
                for e in system.dependencies.broken_refs
            ],
        },
        "findings": system.findings,
        "inspection": _build_json_inspection(inspection_results),
    }
    if system.uncategorized_files:
        output["uncategorized_files"] = system.uncategorized_files
    return json.dumps(output, indent=2)
