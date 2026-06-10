"""Lint orchestration for inspection. Runs rules against parsed components."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.parsers import (
    parse_agent,
    parse_claude_md,
    parse_command,
    parse_hooks,
    parse_skill,
)
from harness_eval_lab.inspection.registry import get_all_rules
from harness_eval_lab.inspection.suppression import is_suppressed, parse_suppressions
from harness_eval_lab.inspection.types import (
    Finding,
    InspectionResult,
    Location,
    ParsedCommand,
    ParsedSkill,
    ReportDescriptor,
    Rule,
    RuleCategory,
    RuleContext,
    Severity,
)

_INTERPOLATION_RE = re.compile(r"\{\{(\w+)\}\}")


def _is_nested_repo(child: Path, scan_root: Path) -> bool:
    """True if any directory between scan_root and child is a separate git repo."""
    current = child if child.is_dir() else child.parent
    scan_root = scan_root.resolve()
    current = current.resolve()
    while current != scan_root and len(current.parts) > len(scan_root.parts):
        if (current / ".git").exists():
            return True
        current = current.parent
    return False


def _interpolate(template: str, data: dict[str, str | int] | None) -> str:
    if not data:
        return template
    return _INTERPOLATION_RE.sub(lambda m: str(data.get(m.group(1), m.group(0))), template)


def _resolve_severity(
    rule: Rule,
    config_rules: dict[str, str | list[Any]],
) -> tuple[Severity, list[Any]] | None:
    """Determine effective severity and options for a rule.

    Returns (severity, options), or None if the rule should be skipped.
    """
    severity_config = config_rules.get(rule.meta.id)
    if severity_config == "off":
        return None

    if isinstance(severity_config, list) and len(severity_config) > 0:
        sev_str = severity_config[0]
        options = severity_config[1:]
    elif isinstance(severity_config, str):
        sev_str = severity_config
        options = []
    else:
        sev_str = rule.meta.default_severity.value
        options = []

    if sev_str == "off":
        return None

    try:
        severity = Severity(sev_str)
    except ValueError:
        severity = rule.meta.default_severity

    return severity, options


def _make_report_fn(
    rule_id: str,
    severity: Severity,
    meta_messages: dict[str, str],
    category: RuleCategory,
    fixable: bool,
    file_path: str,
    suppressions: dict[int | None, set[str]],
    findings: list[Finding],
    suppression_counter: list[int],
) -> Callable[[ReportDescriptor], None]:
    """Build a report callback for a single rule.

    Uses a mutable list for the suppression counter so the caller can read
    the updated value after all rules have run.
    """

    def report(descriptor: ReportDescriptor) -> None:
        loc = descriptor.location or Location(file=file_path)
        if is_suppressed(suppressions, rule_id, loc.start_line):
            suppression_counter[0] += 1
            return
        template = meta_messages.get(descriptor.message_id, descriptor.message_id)
        message = _interpolate(template, descriptor.data)
        effective_severity = descriptor.severity_override or severity
        findings.append(
            Finding(
                rule_id=rule_id,
                severity=effective_severity,
                message=message,
                location=loc,
                category=category,
                fix=descriptor.fix if fixable else None,
            )
        )

    return report


def _parse_errors_to_findings(
    parse_errors: list[str],
    file_path: str,
    category: RuleCategory | str = "structural",
) -> list[Finding]:
    """Convert parse errors into Finding objects."""
    return [
        Finding(
            rule_id="parser",
            severity=Severity.ERROR,
            message=error,
            location=Location(file=file_path),
            category=category,  # type: ignore[arg-type]
        )
        for error in parse_errors
    ]


def _run_rules(
    target_type: ComponentType,
    file_path: str,
    raw_content: str,
    skill: ParsedSkill | None,
    target: Any,
    config_rules: dict[str, str | list[Any]] | None,
    all_skills: list[ParsedSkill] | None = None,
    all_commands: list[ParsedCommand] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> tuple[list[Finding], int]:
    """Run rules for a given target type. Returns (findings, suppression_count)."""
    findings: list[Finding] = []
    suppression_counter = [0]
    suppressions = parse_suppressions(raw_content) if raw_content else {}
    config_rules = config_rules or {}
    scan_state = scan_state if scan_state is not None else {}

    dummy_skill = skill or ParsedSkill(
        dir_path="",
        dir_name="",
        skill_md_path=file_path,
        raw_content="",
        frontmatter={},
        raw_frontmatter="",
        frontmatter_start_line=0,
        body="",
        body_start_line=0,
        files=[],
    )

    rules = get_all_rules()

    for rule in rules:
        if rule.meta.target_type != target_type:
            continue

        resolved = _resolve_severity(rule, config_rules)
        if resolved is None:
            continue
        severity, options = resolved

        context = RuleContext(
            skill=dummy_skill,
            report=_make_report_fn(
                rule.meta.id,
                severity,
                rule.meta.messages,
                rule.meta.category,
                rule.meta.fixable,
                file_path,
                suppressions,
                findings,
                suppression_counter,
            ),
            severity=severity,
            options=options,
            target=target,
            all_skills=all_skills or [],
            all_commands=all_commands or [],
            scan_state=scan_state,
        )
        rule.create(context)

    return findings, suppression_counter[0]


def _build_result(
    target_path: str,
    target_name: str,
    tokens: int,
    target_type: str,
    diagnostics: list[Finding],
    suppression_count: int,
) -> InspectionResult:
    return InspectionResult(
        target_path=target_path,
        target_name=target_name,
        tokens=tokens,
        target_type=target_type,
        diagnostics=diagnostics,
        error_count=sum(1 for d in diagnostics if d.severity == Severity.ERROR),
        warning_count=sum(1 for d in diagnostics if d.severity == Severity.WARNING),
        info_count=sum(1 for d in diagnostics if d.severity == Severity.INFO),
        fixable_count=sum(1 for d in diagnostics if d.fix is not None),
        suppression_count=suppression_count,
    )


def lint(
    skill_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> InspectionResult:
    """Lint a single skill directory or SKILL.md file."""
    skill = parse_skill(skill_path)
    diagnostics = _parse_errors_to_findings(
        skill.parse_errors,
        skill.skill_md_path,
        category=skill.parse_errors[0] if skill.parse_errors else "structural",
    )

    rule_diags, suppression_count = _run_rules(
        ComponentType.SKILL,
        skill.skill_md_path,
        skill.raw_content,
        skill=skill,
        target=skill,
        config_rules=config_rules,
        scan_state=scan_state,
    )
    diagnostics.extend(rule_diags)

    return _build_result(
        skill_path,
        skill.dir_name,
        skill.tokens,
        "skill",
        diagnostics,
        suppression_count,
    )


def lint_command(
    command_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
    all_skills: list[ParsedSkill] | None = None,
    all_commands: list[ParsedCommand] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> InspectionResult:
    """Lint a single command directory."""
    cmd = parse_command(command_path)
    diagnostics = _parse_errors_to_findings(cmd.parse_errors, cmd.command_md_path)

    rule_diags, suppression_count = _run_rules(
        ComponentType.COMMAND,
        cmd.command_md_path,
        cmd.raw_content,
        skill=None,
        target=cmd,
        config_rules=config_rules,
        all_skills=all_skills,
        all_commands=all_commands,
        scan_state=scan_state,
    )
    diagnostics.extend(rule_diags)

    return _build_result(
        command_path,
        cmd.dir_name,
        cmd.tokens,
        "command",
        diagnostics,
        suppression_count,
    )


def lint_claude_md(
    file_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
    all_skills: list[ParsedSkill] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> InspectionResult:
    """Lint a CLAUDE.md file."""
    claude_md = parse_claude_md(file_path)
    diagnostics = _parse_errors_to_findings(claude_md.parse_errors, file_path)

    rule_diags, suppression_count = _run_rules(
        ComponentType.CLAUDE_MD,
        file_path,
        claude_md.raw_content,
        skill=None,
        target=claude_md,
        config_rules=config_rules,
        all_skills=all_skills,
        scan_state=scan_state,
    )
    diagnostics.extend(rule_diags)

    return _build_result(
        file_path,
        Path(file_path).name,
        claude_md.tokens,
        "claude_md",
        diagnostics,
        suppression_count,
    )


def lint_hooks(
    settings_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> InspectionResult:
    """Lint hooks from settings.json."""
    hooks = parse_hooks(settings_path)
    diagnostics = _parse_errors_to_findings(hooks.parse_errors, settings_path)

    rule_diags, suppression_count = _run_rules(
        ComponentType.HOOKS,
        settings_path,
        hooks.raw_content,
        skill=None,
        target=hooks,
        config_rules=config_rules,
        scan_state=scan_state,
    )
    diagnostics.extend(rule_diags)

    return _build_result(
        settings_path,
        "hooks",
        0,
        "hooks",
        diagnostics,
        suppression_count,
    )


def lint_agent(
    agent_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
    all_skills: list[ParsedSkill] | None = None,
    scan_state: dict[str, Any] | None = None,
) -> InspectionResult:
    """Lint a single agent .md file."""
    agent = parse_agent(agent_path)
    diagnostics = _parse_errors_to_findings(agent.parse_errors, agent.agent_md_path)

    rule_diags, suppression_count = _run_rules(
        ComponentType.AGENT,
        agent.agent_md_path,
        agent.raw_content,
        skill=None,
        target=agent,
        config_rules=config_rules,
        all_skills=all_skills,
        scan_state=scan_state,
    )
    diagnostics.extend(rule_diags)

    return _build_result(
        agent_path,
        agent.file_name.removesuffix(".md"),
        agent.tokens,
        "agent",
        diagnostics,
        suppression_count,
    )


def inspect_setup(
    setup: Any,
    config_rules: dict[str, str | list[Any]] | None = None,
) -> list[InspectionResult]:
    """Run inspection on all components in a setup."""
    from harness_eval_lab.core.types import ComponentType as CT

    scan_state: dict[str, Any] = {}
    results: list[InspectionResult] = []
    for comp in setup.by_type(CT.SKILL):
        results.append(lint(str(Path(comp.path).parent), config_rules, scan_state=scan_state))
    for comp in setup.by_type(CT.COMMAND):
        cmd_path = Path(comp.path)
        if cmd_path.is_file() and cmd_path.name != "command.md":
            results.append(lint_command(str(cmd_path), config_rules, scan_state=scan_state))
        else:
            results.append(lint_command(str(cmd_path.parent), config_rules, scan_state=scan_state))
    for comp in setup.by_type(CT.CLAUDE_MD):
        results.append(lint_claude_md(comp.path, config_rules, scan_state=scan_state))
    for comp in setup.by_type(CT.HOOKS):
        results.append(lint_hooks(comp.path, config_rules, scan_state=scan_state))
    for comp in setup.by_type(CT.AGENT):
        results.append(lint_agent(comp.path, config_rules, scan_state=scan_state))
    return results


def lint_directory(
    scan_path: str,
    config_rules: dict[str, str | list[Any]] | None = None,
) -> list[InspectionResult]:
    """Lint all skills found under a directory."""
    path = Path(scan_path)
    results = []

    if path.is_file() and path.name.lower() == "skill.md":
        results.append(lint(str(path.parent), config_rules))
        return results

    if not path.is_dir():
        return results

    excluded = {".git", ".venv", "node_modules", "__pycache__", "tests"}
    skill_dirs: list[Path] = []
    for p in sorted(path.rglob("SKILL.md")):
        relative_parts = p.relative_to(path).parts
        if excluded.isdisjoint(relative_parts) and not _is_nested_repo(p, path):
            skill_dirs.append(p.parent)

    if not skill_dirs and (path / "SKILL.md").exists():
        skill_dirs = [path]

    seen: set[str] = set()
    for skill_dir in skill_dirs:
        resolved = str(skill_dir.resolve())
        if resolved not in seen:
            seen.add(resolved)
            results.append(lint(str(skill_dir), config_rules))

    return results
