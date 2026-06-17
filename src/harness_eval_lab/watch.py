"""Watch mode for setup-eval-lint: monitor files and re-run lint on changes."""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from collections.abc import Callable

    from watchfiles import Change

# Debounce window in milliseconds
DEBOUNCE_MS = 300


def _collect_watch_paths(root: Path) -> list[Path]:
    """Collect all paths that discover_setup() would scan."""
    paths: list[Path] = []

    # CLAUDE.md files
    for pattern in ["CLAUDE.md", "**/CLAUDE.md"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                paths.append(f)

    # Skills
    for skills_dir in [root / "skills", root / ".claude" / "skills"]:
        if skills_dir.is_dir():
            for f in sorted(skills_dir.rglob("SKILL.md")):
                paths.append(f)

    # Commands
    for commands_dir in [root / "commands", root / ".claude" / "commands"]:
        if commands_dir.is_dir():
            for f in sorted(commands_dir.rglob("*.md")):
                paths.append(f)

    # Settings / hooks
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        paths.append(settings)

    # Agents
    agents_dir = root / ".claude" / "agents"
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.md")):
            paths.append(f)

    # MCP configs
    for pattern in [".mcp.json", "**/.mcp.json"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                paths.append(f)

    # Cursor rules / commands
    cursor_rules = root / ".cursor" / "rules"
    if cursor_rules.is_dir():
        for f in sorted(cursor_rules.rglob("*.mdc")):
            paths.append(f)

    for f in sorted(root.rglob(".cursorrules")):
        if f.is_file() and ".git" not in f.parts:
            paths.append(f)

    cursor_commands = root / ".cursor" / "commands"
    if cursor_commands.is_dir():
        for f in sorted(cursor_commands.iterdir()):
            if f.is_file() and f.suffix == ".md":
                paths.append(f)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        resolved = str(p.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(p)

    return unique


def _get_watch_directories(paths: list[Path]) -> set[Path]:
    """Get unique parent directories to watch."""
    dirs: set[Path] = set()
    for p in paths:
        dirs.add(p.parent)
    return dirs


def _build_filter(
    watch_paths: list[Path],
) -> Callable[[Change, str], bool]:
    """Build a filter function for watchfiles that only passes watched files."""
    resolved = {str(p.resolve()) for p in watch_paths}

    def _filter(change: Change, path: str) -> bool:
        return path in resolved

    return _filter


def _clear_terminal() -> None:
    """Clear the terminal screen."""
    click.echo("\033[2J\033[H", nl=False)


def run_watch(
    path: str,
    preset: str,
    fmt: str,
    user_config: str | None,
    debounce_ms: int = DEBOUNCE_MS,
) -> None:
    """Run lint in watch mode, re-running on file changes.

    Args:
        path: Directory to lint and watch.
        preset: Lint preset name.
        fmt: Output format ('terminal' or 'json').
        user_config: Optional user config directory.
        debounce_ms: Debounce window in milliseconds.
    """
    try:
        from watchfiles import watch
    except ImportError as err:
        raise click.ClickException(
            "Watch mode requires the 'watchfiles' package. Install it with: pip install watchfiles"
        ) from err

    from harness_eval_lab.analysis.system import analyze_system
    from harness_eval_lab.config.presets import PRESETS
    from harness_eval_lab.core.setup import discover_setup
    from harness_eval_lab.inspection.engine import inspect_setup
    from harness_eval_lab.output.report import format_json, format_terminal

    root = Path(path)
    config_rules = PRESETS.get(preset, {})

    watch_paths = _collect_watch_paths(root)
    watch_dirs = _get_watch_directories(watch_paths)

    if not watch_dirs:
        raise click.ClickException(f"No agent setup files found in '{path}'.")

    def _run_lint() -> None:
        """Run lint and display results."""
        setup = discover_setup(name=root.name, path=path, user_config_dir=user_config)
        results = inspect_setup(setup, config_rules)
        system = analyze_system(setup)

        if fmt == "json":
            click.echo(format_json(system, results))
        else:
            click.echo(format_terminal(system, results))

    # Initial run
    _clear_terminal()
    click.echo(f"👀 Watching {len(watch_paths)} files for changes... (Ctrl+C to stop)\n")
    _run_lint()

    # Watch loop
    watch_filter = _build_filter(watch_paths)

    try:
        for changes in watch(
            *watch_dirs,
            watch_filter=watch_filter,
            debounce=debounce_ms,
            rust_timeout=0,
        ):
            # Identify which files changed
            changed_files = [Path(p).name for _, p in changes]
            changed_list = ", ".join(changed_files)

            _clear_terminal()
            timestamp = time.strftime("%H:%M:%S")
            click.echo(f"👀 [{timestamp}] Change detected: {changed_list}\n")

            # Refresh watch paths in case new files were added
            watch_paths = _collect_watch_paths(root)

            try:
                _run_lint()
            except Exception as e:
                click.echo(f"\nError during lint: {e}", err=True)

            click.echo("\nWatching for changes... (Ctrl+C to stop)")
    except KeyboardInterrupt:
        click.echo("\n\nWatch mode stopped.")
