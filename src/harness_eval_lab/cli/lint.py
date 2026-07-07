"""setup-eval-lint command."""

from __future__ import annotations

import json as json_mod
import time
from pathlib import Path

import click

from harness_eval_lab.cli import cli
from harness_eval_lab.cli._helpers import emit_output
from harness_eval_lab.core.setup import discover_setup
from harness_eval_lab.output.metadata import EvalMetadata


@cli.command("setup-eval-lint")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--preset",
    type=click.Choice(["recommended", "strict", "security", "pre-workflow"]),
    default="recommended",
)
@click.option(
    "--format", "fmt", type=click.Choice(["terminal", "json", "sarif"]), default="terminal"
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(),
    default=None,
    help="Write output to file instead of stdout.",
)
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
    output_path: str | None,
    fix: bool,
    fail_on_error: bool,
    watch: bool,
    user_config: str | None,
) -> None:
    """Lint: 58 rules + system analysis. No LLM, deterministic, fast."""
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

        if fmt == "sarif":
            from harness_eval_lab.output.sarif import format_sarif

            sarif_doc = format_sarif(results, metadata)
            emit_output(json_mod.dumps(sarif_doc, indent=2), output_path)
        elif fmt == "json":
            json_out = format_json(system, results)
            data = json_mod.loads(json_out)
            data["metadata"] = metadata.to_dict()
            emit_output(json_mod.dumps(data, indent=2), output_path)
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

        if fmt == "sarif":
            from harness_eval_lab.output.sarif import format_sarif

            sarif_doc = format_sarif(results, metadata)
            emit_output(json_mod.dumps(sarif_doc, indent=2), output_path)
        elif fmt == "json":
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
            emit_output(json_mod.dumps(output, indent=2), output_path)
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
                f"\n{len(results)} components scanned, "
                f"{total_errors} errors, {total_warnings} warnings"
            )
            click.echo(metadata.format_terminal())

    if fix:
        all_findings = [d for r in results for d in r.diagnostics]
        fix_results = apply_fixes(all_findings, project_root=Path(path).resolve())
        for fr in fix_results:
            click.echo(f"Fixed {fr.fixes_applied} issues in {fr.file_path}")

    if fail_on_error:
        total_errors = sum(r.error_count for r in results)
        if total_errors > 0:
            raise SystemExit(1)


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
