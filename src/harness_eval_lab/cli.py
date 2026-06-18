"""CLI entry point for setup-eval."""

from __future__ import annotations

import json as json_mod
import time
from pathlib import Path

import click

from harness_eval_lab.core.setup import discover_setup
from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.output.metadata import EvalMetadata
from harness_eval_lab.rubric.types import RubricResult


@click.group()
@click.version_option(package_name="setup-eval")
def cli() -> None:
    """Evaluate AI agent setups."""


@cli.command("setup-eval-lint")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--preset",
    type=click.Choice(["recommended", "strict", "security", "pre-workflow"]),
    default="recommended",
)
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option("--fix", is_flag=True, help="Apply auto-fixes.")
@click.option(
    "--fail-on-error",
    is_flag=True,
    help="Exit with code 1 if any errors found. Useful for CI and hooks.",
)
@click.option(
    "--watch",
    is_flag=True,
    help="Watch files for changes and re-run lint automatically.",
)
@click.option(
    "--user-config",
    type=click.Path(),
    default=None,
    help="Path to ~/.claude directory for user-level CLAUDE.md discovery.",
)
def eval_setup_lint(
    path: str,
    preset: str,
    fmt: str,
    fix: bool,
    fail_on_error: bool,
    watch: bool,
    user_config: str | None,
) -> None:
    """Lint: 39 rules + system analysis. No LLM, deterministic, fast."""
    if watch:
        from harness_eval_lab.watch import run_watch

        if fix:
            click.echo("Warning: --fix is ignored in watch mode.", err=True)
        if fail_on_error:
            click.echo("Warning: --fail-on-error is ignored in watch mode.", err=True)
        run_watch(path=path, preset=preset, fmt=fmt, user_config=user_config)
        return

    t0 = time.monotonic()
    from harness_eval_lab.analysis.system import analyze_system
    from harness_eval_lab.config.presets import PRESETS
    from harness_eval_lab.inspection.engine import inspect_setup
    from harness_eval_lab.inspection.fixer import apply_fixes
    from harness_eval_lab.output.report import format_json, format_terminal

    config_rules = PRESETS.get(preset, {})
    target = Path(path)

    if target.is_dir():
        setup = discover_setup(name=target.name, path=path, user_config_dir=user_config)
        results = inspect_setup(setup, config_rules)
        system = analyze_system(setup)

        metadata = EvalMetadata(
            version=EvalMetadata.get_version(),
            duration_seconds=time.monotonic() - t0,
            components_scanned=len(results),
            rules_checked=sum(len(r.rules_run) for r in results),
            invocation_source="cli",
        )

        if fmt == "json":
            json_out = format_json(system, results)
            data = json_mod.loads(json_out)
            data["metadata"] = metadata.to_dict()
            click.echo(json_mod.dumps(data, indent=2))
        else:
            click.echo(format_terminal(system, results))
            click.echo(metadata.format_terminal())
    else:
        results = _inspect_single_file(target, config_rules)

        metadata = EvalMetadata(
            version=EvalMetadata.get_version(),
            duration_seconds=time.monotonic() - t0,
            components_scanned=len(results),
            rules_checked=sum(len(r.rules_run) for r in results),
            invocation_source="cli",
        )

        if fmt == "json":
            output = {
                "results": [
                    {
                        "target": f"{r.target_type}/{r.target_name}",
                        "tokens": r.tokens,
                        "errors": r.error_count,
                        "warnings": r.warning_count,
                        "findings": [
                            {"rule": d.rule_id, "severity": d.severity.value, "message": d.message}
                            for d in r.diagnostics
                        ],
                    }
                    for r in results
                ],
                "metadata": metadata.to_dict(),
            }
            click.echo(json_mod.dumps(output, indent=2))
        else:
            total_errors = sum(r.error_count for r in results)
            total_warnings = sum(r.warning_count for r in results)
            for r in results:
                if r.diagnostics:
                    click.echo(f"\n{r.target_type}/{r.target_name} ({r.tokens} tokens):")
                    for d in r.diagnostics:
                        icon = "X" if d.severity.value == "error" else "!"
                        click.echo(f"  [{icon}] {d.rule_id}: {d.message}")
            click.echo(
                f"\n{len(results)} components scanned, {total_errors} errors, {total_warnings} warnings"
            )
            click.echo(metadata.format_terminal())

    if fix:
        all_findings = [d for r in results for d in r.diagnostics]
        fix_results = apply_fixes(all_findings)
        for fr in fix_results:
            click.echo(f"Fixed {fr.fixes_applied} issues in {fr.file_path}")

    if fail_on_error:
        total_errors = sum(r.error_count for r in results)
        if total_errors > 0:
            raise SystemExit(1)


@cli.command("setup-eval-review")
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option("--provider", type=click.Choice(["gemini", "anthropic"]), default="gemini")
@click.option("--model", default=None, help="LLM model for rubric scoring.")
@click.option(
    "--user-config",
    type=click.Path(),
    default=None,
    help="Path to ~/.claude directory for user-level CLAUDE.md discovery.",
)
def eval_setup_review(
    path: str, fmt: str, provider: str, model: str | None, user_config: str | None
) -> None:
    """Review: LLM rubric scoring per component. Requires API key in environment."""
    t0 = time.monotonic()
    from harness_eval_lab.rubric.scorer import RubricChecker
    from harness_eval_lab.utils.llm import create_client

    setup = discover_setup(name=Path(path).name, path=path, user_config_dir=user_config)

    client = create_client(provider, model)
    checker = RubricChecker(client)

    context_parts = [
        f"[{c.component_type.value}] {c.name}: {c.content[:200]}" for c in setup.components
    ]
    context_text = "\n".join(context_parts)

    component_type_map = {
        ComponentType.SKILL: "skill",
        ComponentType.COMMAND: "command",
        ComponentType.CLAUDE_MD: "claude_md",
        ComponentType.HOOKS: "hooks",
        ComponentType.AGENT: "agent",
    }

    from concurrent.futures import ThreadPoolExecutor, as_completed

    from harness_eval_lab.utils.tokens import count_tokens

    reviewable = []
    for comp in setup.components:
        comp_type_str = component_type_map.get(comp.component_type)
        if comp_type_str:
            reviewable.append((comp_type_str, comp.name, comp.content))

    small: list[tuple[str, str, str]] = []
    large: list[tuple[str, str, str]] = []
    for item in reviewable:
        if count_tokens(item[2]) < 500:
            small.append(item)
        else:
            large.append(item)

    batches: list[list[tuple[str, str, str]]] = []
    for i in range(0, len(small), 3):
        batches.append(small[i : i + 3])
    for item in large:
        batches.append([item])

    checker._ensure_client_safe()
    click.echo(f"  Reviewing {len(reviewable)} components ({len(batches)} batches)...", err=True)

    rubric_results: list[RubricResult] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {}
        for batch in batches:
            if len(batch) == 1:
                ct, cn, cc = batch[0]
                future = executor.submit(checker.check, ct, cn, cc, context_text)
            else:
                future = executor.submit(checker.check_batch, batch, context_text)  # type: ignore[arg-type]
            future_map[future] = batch

        for future in as_completed(future_map):
            result = future.result()
            if isinstance(result, list):
                rubric_results.extend(result)
            else:
                rubric_results.append(result)

    comp_order = {comp.name: i for i, comp in enumerate(setup.components)}
    rubric_results.sort(key=lambda r: comp_order.get(r.component_name, 999))

    metadata = EvalMetadata(
        version=EvalMetadata.get_version(),
        duration_seconds=time.monotonic() - t0,
        components_scanned=len(rubric_results),
        invocation_source="cli",
        provider=provider,
        model=client.model,  # type: ignore[attr-defined]
        llm_calls_total=client.calls_total,  # type: ignore[attr-defined]
        llm_calls_succeeded=client.calls_succeeded,  # type: ignore[attr-defined]
    )

    if fmt == "json":
        output = {
            "setup": setup.name,
            "component_count": len(setup.components),
            "rubric": [
                {
                    "component": rr.component_name,
                    "type": rr.component_type,
                    "issues": [
                        {
                            "category": i.category,
                            "description": i.description,
                            "evidence": i.evidence,
                            "suggestion": i.suggestion,
                            "impact": i.impact,
                        }
                        for i in rr.issues
                    ],
                    "summary": rr.summary,
                    "verdict": rr.verdict,
                }
                for rr in rubric_results
            ],
            "metadata": metadata.to_dict(),
        }
        click.echo(json_mod.dumps(output, indent=2))
    else:
        click.echo(f"\n{'=' * 60}")
        click.echo(f"Setup Review: {setup.name}")
        click.echo(f"{'=' * 60}")
        click.echo(f"Components: {len(setup.components)}")
        click.echo(f"Provider: {provider} | Model: {model or 'default'}")
        click.echo("")

        for rr in rubric_results:
            if rr.issues:
                click.echo(f"  {rr.component_type}/{rr.component_name}:")
                for issue in rr.issues:
                    click.echo(f"    [{issue.category}] {issue.description}")
                    click.echo(f"      Evidence: {issue.evidence}")
                    click.echo(f"      Fix: {issue.suggestion}")
                    if issue.impact:
                        click.echo(f"      Impact: {issue.impact}")
            else:
                click.echo(f"  {rr.component_type}/{rr.component_name}: no issues")
            if rr.summary:
                click.echo(f"    Summary: {rr.summary}")
            click.echo("")

        total_issues = sum(len(rr.issues) for rr in rubric_results)
        click.echo(f"{len(rubric_results)} components reviewed, {total_issues} rubric issues found")
        click.echo(metadata.format_terminal())
        click.echo("")


@cli.command("setup-eval-security")
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option(
    "--review",
    is_flag=True,
    help="Also run LLM-based semantic security review (requires API key).",
)
@click.option("--provider", type=click.Choice(["gemini", "anthropic"]), default="gemini")
@click.option("--model", default=None, help="LLM model for semantic security review.")
@click.option(
    "--fail-on-error",
    is_flag=True,
    help="Exit with code 1 if any errors found.",
)
@click.option(
    "--user-config",
    type=click.Path(),
    default=None,
    help="Path to ~/.claude directory for user-level CLAUDE.md discovery.",
)
def eval_setup_security(
    path: str,
    fmt: str,
    review: bool,
    provider: str,
    model: str | None,
    fail_on_error: bool,
    user_config: str | None,
) -> None:
    """Deep security audit: all deterministic security rules + optional LLM review."""
    t0 = time.monotonic()
    from harness_eval_lab.config.presets import SECURITY
    from harness_eval_lab.inspection.engine import inspect_setup

    target = Path(path)
    setup = discover_setup(name=target.name, path=path, user_config_dir=user_config)
    results = inspect_setup(setup, SECURITY)

    skip_rules = {"security/yara-signatures", "security/cve-lookup"}
    skip_notices: list[str] = []
    seen_skip: set[str] = set()
    for r in results:
        for d in r.diagnostics:
            if (
                d.rule_id in skip_rules
                and d.severity.value == "info"
                and d.message not in seen_skip
            ):
                seen_skip.add(d.message)
                skip_notices.append(d.message)

    from harness_eval_lab.inspection.types import InspectionResult

    cleaned_results: list[InspectionResult] = []
    for r in results:
        filtered = [
            d for d in r.diagnostics if not (d.rule_id in skip_rules and d.severity.value == "info")
        ]
        cleaned_results.append(
            InspectionResult(
                target_path=r.target_path,
                target_name=r.target_name,
                tokens=r.tokens,
                target_type=r.target_type,
                diagnostics=filtered,
                rules_run=r.rules_run,
                error_count=sum(1 for d in filtered if d.severity.value == "error"),
                warning_count=sum(1 for d in filtered if d.severity.value == "warning"),
                info_count=sum(1 for d in filtered if d.severity.value == "info"),
                fixable_count=sum(1 for d in filtered if d.fix is not None),
                suppression_count=r.suppression_count,
            )
        )
    results = cleaned_results

    rubric_results = []
    if review:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from harness_eval_lab.rubric.dimensions import SECURITY_REVIEW_CATEGORIES
        from harness_eval_lab.rubric.scorer import RubricChecker
        from harness_eval_lab.utils.llm import create_client

        client = create_client(provider, model)
        checker = RubricChecker(client)
        checker._ensure_client_safe()

        context_parts = [
            f"[{c.component_type.value}] {c.name}: {c.content[:200]}" for c in setup.components
        ]
        context_text = "\n".join(context_parts)

        click.echo(f"  Security review: {len(setup.components)} components...", err=True)

        all_sec_results: list[RubricResult] = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    checker.check,
                    comp.component_type.value,
                    comp.name,
                    comp.content,
                    context_text,
                    SECURITY_REVIEW_CATEGORIES,
                ): comp
                for comp in setup.components
            }
            for future in as_completed(futures):
                all_sec_results.append(future.result())

        for rr in all_sec_results:
            if rr.issues:
                rubric_results.append(rr)

    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    total_semantic = sum(len(rr.issues) for rr in rubric_results)
    components_with_findings = [r for r in results if r.diagnostics]
    clean_count = len(results) - len(components_with_findings)

    if total_errors == 0 and total_warnings == 0 and total_semantic == 0:
        risk = "SAFE"
    elif total_errors == 0:
        risk = "CAUTION"
    else:
        risk = "UNSAFE"

    sec_metadata = EvalMetadata(
        version=EvalMetadata.get_version(),
        duration_seconds=time.monotonic() - t0,
        components_scanned=len(results),
        invocation_source="cli",
    )
    if review:
        sec_metadata.provider = provider
        sec_metadata.model = client.model  # type: ignore[attr-defined]
        sec_metadata.llm_calls_total = client.calls_total  # type: ignore[attr-defined]
        sec_metadata.llm_calls_succeeded = client.calls_succeeded  # type: ignore[attr-defined]

    if fmt == "json":
        output = {
            "security_scan": True,
            "setup": setup.name,
            "risk_assessment": risk,
            "components_scanned": len(results),
            "errors": total_errors,
            "warnings": total_warnings,
            "semantic_issues": total_semantic,
            "findings": [
                {
                    "component": f"{r.target_type}/{r.target_name}",
                    "errors": r.error_count,
                    "warnings": r.warning_count,
                    "details": [
                        {
                            "rule": d.rule_id,
                            "severity": d.severity.value,
                            "message": d.message,
                        }
                        for d in r.diagnostics
                    ],
                }
                for r in components_with_findings
            ],
        }
        output["metadata"] = sec_metadata.to_dict()
        if skip_notices:
            output["skipped_checks"] = skip_notices
        if rubric_results:
            output["semantic_review"] = [
                {
                    "component": rr.component_name,
                    "type": rr.component_type,
                    "issues": [
                        {
                            "category": i.category,
                            "description": i.description,
                            "evidence": i.evidence,
                            "suggestion": i.suggestion,
                            "impact": i.impact,
                        }
                        for i in rr.issues
                    ],
                }
                for rr in rubric_results
            ]
        click.echo(json_mod.dumps(output, indent=2))
    else:
        click.echo(f"\n{'=' * 60}")
        click.echo(f"Security Audit: {setup.name}")
        click.echo(f"{'=' * 60}")
        click.echo(f"Components scanned: {len(results)}")
        click.echo(f"Risk Assessment: {risk}")
        click.echo(f"Errors: {total_errors} | Warnings: {total_warnings}")
        click.echo("")

        if components_with_findings:
            click.echo("Security Findings:")
            click.echo(f"{'─' * 60}")
            for r in components_with_findings:
                parts = []
                if r.error_count:
                    parts.append(f"{r.error_count} error{'s' if r.error_count != 1 else ''}")
                if r.warning_count:
                    parts.append(f"{r.warning_count} warning{'s' if r.warning_count != 1 else ''}")
                status = ", ".join(parts)
                click.echo(f"  {r.target_type}/{r.target_name:<36} {status}")
                for d in r.diagnostics:
                    sev = "FAIL" if d.severity.value == "error" else "WARNING"
                    short_rule = d.rule_id.split("/", 1)[-1]
                    click.echo(f"    {sev:<8} {short_rule}: {d.message}")
            click.echo("")

        if clean_count > 0:
            click.echo(f"{clean_count}/{len(results)} components passed all security checks.")
            click.echo("")

        if rubric_results:
            click.echo("Semantic Security Review:")
            click.echo(f"{'─' * 60}")
            for rr in rubric_results:
                click.echo(f"  {rr.component_type}/{rr.component_name}:")
                for issue in rr.issues:
                    click.echo(f"    [{issue.category}] {issue.description}")
                    click.echo(f"      Evidence: {issue.evidence}")
                    click.echo(f"      Fix: {issue.suggestion}")
                    if issue.impact:
                        click.echo(f"      Impact: {issue.impact}")
            click.echo("")

        if skip_notices:
            click.echo("Skipped Checks:")
            click.echo(f"{'─' * 60}")
            for notice in skip_notices:
                click.echo(f"  {notice}")
            click.echo("")

        click.echo(sec_metadata.format_terminal())
        click.echo("")

    if fail_on_error and total_errors > 0:
        raise SystemExit(1)


@cli.command("eval-skill")
@click.argument("skill_path", type=click.Path(exists=True))
@click.option(
    "--context",
    "context_path",
    type=click.Path(exists=True),
    default=None,
    help="Setup directory for contextual evaluation.",
)
@click.option(
    "--preset",
    type=click.Choice(["recommended", "strict", "security", "pre-workflow"]),
    default="recommended",
)
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option(
    "--rubric", "run_rubric", is_flag=True, help="Also run LLM rubric scoring (requires API key)."
)
@click.option("--provider", type=click.Choice(["gemini", "anthropic"]), default="gemini")
@click.option("--model", default=None, help="LLM model for rubric scoring.")
@click.option(
    "--user-config",
    type=click.Path(),
    default=None,
    help="Path to ~/.claude directory for user-level CLAUDE.md discovery.",
)
def eval_skill(
    skill_path: str,
    context_path: str | None,
    preset: str,
    fmt: str,
    run_rubric: bool,
    provider: str,
    model: str | None,
    user_config: str | None,
) -> None:
    """Deep-evaluate a single skill, individually and in context of the setup."""
    t0 = time.monotonic()
    from harness_eval_lab.config.presets import PRESETS
    from harness_eval_lab.inspection.engine import lint
    from harness_eval_lab.inspection.parsers import parse_skill

    config_rules = PRESETS.get(preset, {})
    target = Path(skill_path)
    if target.is_file() and target.name.lower() == "skill.md":
        target = target.parent

    skill = parse_skill(str(target))
    result = lint(str(target), config_rules)

    context_findings: list[str] = []
    if context_path:
        context_findings = _contextual_skill_analysis(str(target), context_path, config_rules)

    rubric_result = None
    if run_rubric:
        from harness_eval_lab.rubric.scorer import RubricChecker
        from harness_eval_lab.utils.llm import create_client

        client = create_client(provider, model)
        checker = RubricChecker(client)

        context_text = None
        if context_path:
            ctx_setup = discover_setup(
                name="context", path=context_path, user_config_dir=user_config
            )
            parts = [
                f"[{c.component_type.value}] {c.name}: {c.content[:200]}"
                for c in ctx_setup.components
            ]
            context_text = "\n".join(parts)

        rubric_result = checker.check(
            component_type="skill",
            component_name=skill.dir_name,
            content=skill.raw_content,
            context=context_text,
        )

    skill_metadata = EvalMetadata(
        version=EvalMetadata.get_version(),
        duration_seconds=time.monotonic() - t0,
        components_scanned=1,
        rules_checked=len(result.rules_run),
        invocation_source="cli",
    )
    if run_rubric and rubric_result:
        skill_metadata.provider = provider
        skill_metadata.model = client.model  # type: ignore[attr-defined]
        skill_metadata.llm_calls_total = client.calls_total  # type: ignore[attr-defined]
        skill_metadata.llm_calls_succeeded = client.calls_succeeded  # type: ignore[attr-defined]

    if fmt == "json":
        output: dict = {
            "skill": skill.dir_name,
            "tokens": skill.tokens,
            "errors": result.error_count,
            "warnings": result.warning_count,
            "findings": [
                {"rule": d.rule_id, "severity": d.severity.value, "message": d.message}
                for d in result.diagnostics
            ],
        }
        output["metadata"] = skill_metadata.to_dict()
        if context_findings:
            output["context_findings"] = context_findings
        if rubric_result:
            output["rubric"] = {
                "issues": [
                    {
                        "category": i.category,
                        "description": i.description,
                        "evidence": i.evidence,
                        "suggestion": i.suggestion,
                        "severity": i.severity,
                        "impact": i.impact,
                    }
                    for i in rubric_result.issues
                ],
                "summary": rubric_result.summary,
                "verdict": rubric_result.verdict,
            }
        click.echo(json_mod.dumps(output, indent=2))
    else:
        click.echo(f"\n{'=' * 60}")
        click.echo(f"Skill Evaluation: {skill.dir_name}")
        click.echo(f"{'=' * 60}")
        click.echo(f"Tokens: {skill.tokens}")
        click.echo(f"Files: {len(skill.files)}")

        if skill.frontmatter:
            desc = skill.frontmatter.get("description", "(none)")
            click.echo(f"Description: {desc}")

        click.echo(f"\nInspection: {result.error_count} errors, {result.warning_count} warnings")
        click.echo(f"{'─' * 60}")
        if result.diagnostics:
            for d in result.diagnostics:
                icon = "X" if d.severity.value == "error" else "!"
                click.echo(f"  [{icon}] {d.rule_id}: {d.message}")
        else:
            click.echo("  No issues found.")

        if context_findings:
            click.echo("\nContextual Analysis (in setup):")
            click.echo(f"{'─' * 60}")
            for finding in context_findings:
                click.echo(f"  [~] {finding}")

        if rubric_result:
            if rubric_result.issues:
                click.echo(f"\nRubric Issues ({len(rubric_result.issues)} found):")
                click.echo(f"{'─' * 60}")
                for issue in rubric_result.issues:
                    click.echo(f"  [{issue.category}] {issue.description}")
                    click.echo(f"    Evidence: {issue.evidence}")
                    click.echo(f"    Fix: {issue.suggestion}")
                    if issue.impact:
                        click.echo(f"    Impact: {issue.impact}")
            else:
                click.echo("\nRubric: No issues found.")
            if rubric_result.summary:
                click.echo(f"\n  Summary: {rubric_result.summary}")

        click.echo(skill_metadata.format_terminal())
        click.echo("")


def _inspect_single_file(target, config_rules):
    """Inspect a single file, auto-detecting its type."""
    from harness_eval_lab.inspection.engine import (
        lint,
        lint_agent,
        lint_claude_md,
        lint_command,
        lint_hooks,
    )

    name = target.name.lower()
    if name == "skill.md":
        return [lint(str(target.parent), config_rules)]
    elif name == "command.md":
        return [lint_command(str(target.parent), config_rules)]
    elif name == "claude.md":
        return [lint_claude_md(str(target), config_rules)]
    elif name in ("settings.json", "hooks.json"):
        return [lint_hooks(str(target), config_rules)]
    elif target.suffix == ".mdc" or name == ".cursorrules":
        return [lint_claude_md(str(target), config_rules)]
    elif target.suffix == ".md":
        return [lint_agent(str(target), config_rules)]
    click.echo(
        f"Warning: could not detect component type for '{target.name}'. "
        f"Expected: SKILL.md, command.md, CLAUDE.md, .mdc, .cursorrules, "
        f"settings.json, hooks.json, or an agent .md file.",
        err=True,
    )
    return []


def _contextual_skill_analysis(skill_path, context_path, config_rules):
    """Analyze a skill in context of its parent setup."""
    from harness_eval_lab.analysis.triggers import analyze_triggers
    from harness_eval_lab.inspection.parsers import parse_skill
    from harness_eval_lab.utils.similarity import tfidf_similarity

    findings = []
    skill = parse_skill(skill_path)
    setup = discover_setup(name="context", path=context_path)

    for comp in setup.by_type(ComponentType.SKILL):
        if comp.name == skill.dir_name:
            continue
        sim = tfidf_similarity(skill.body, comp.content)
        if sim >= 0.60:
            findings.append(f"Content overlap: {sim:.0%} similar to skill '{comp.name}'")

    for comp in setup.by_type(ComponentType.CLAUDE_MD):
        for section_text in comp.content.split("\n#"):
            if len(section_text.split()) < 20:
                continue
            sim = tfidf_similarity(skill.body, section_text)
            if sim >= 0.50:
                findings.append(f"Overlaps with CLAUDE.md content ({sim:.0%} similar)")
                break

    triggers = analyze_triggers(setup)
    for name_a, name_b, sim in triggers.overlap_pairs:
        if skill.dir_name in (name_a, name_b):
            other = name_b if name_a == skill.dir_name else name_a
            findings.append(f"Trigger overlap with '{other}' ({sim:.0%} similar descriptions)")

    if skill.frontmatter:
        desc = skill.frontmatter.get("description", "")
        if isinstance(desc, str):
            desc_lower = desc.lower()
            if not any(
                p in desc_lower for p in ["use when", "use for", "applies to", "relevant for"]
            ):
                findings.append(
                    "Missing activation context in description (no 'use when' phrasing)"
                )

    return findings
