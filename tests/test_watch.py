"""Tests for watch mode functionality."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from harness_eval_lab.cli import cli
from harness_eval_lab.watch import (
    _collect_watch_paths,
    _get_watch_directories,
    run_watch,
)


class TestCollectWatchPaths:
    def test_finds_claude_md(self, tmp_path: Path) -> None:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Instructions")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(claude_md.resolve()) in resolved

    def test_finds_skills(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: my-skill\n---\nBody")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(skill_md.resolve()) in resolved

    def test_finds_settings_json(self, tmp_path: Path) -> None:
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        settings = claude_dir / "settings.json"
        settings.write_text("{}")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(settings.resolve()) in resolved

    def test_finds_agents(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        agent_md = agents_dir / "reviewer.md"
        agent_md.write_text("# Reviewer agent")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(agent_md.resolve()) in resolved

    def test_finds_mcp_config(self, tmp_path: Path) -> None:
        mcp = tmp_path / ".mcp.json"
        mcp.write_text("{}")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(mcp.resolve()) in resolved

    def test_finds_commands(self, tmp_path: Path) -> None:
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir()
        cmd_md = cmd_dir / "review.md"
        cmd_md.write_text("# Review command")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        assert str(cmd_md.resolve()) in resolved

    def test_deduplicates_paths(self, tmp_path: Path) -> None:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# Instructions")

        paths = _collect_watch_paths(tmp_path)
        resolved = [str(p.resolve()) for p in paths]
        # Each path should appear only once
        assert len(resolved) == len(set(resolved))

    def test_empty_directory(self, tmp_path: Path) -> None:
        paths = _collect_watch_paths(tmp_path)
        assert paths == []


class TestGetWatchDirectories:
    def test_returns_parent_dirs(self, tmp_path: Path) -> None:
        paths = [
            tmp_path / "CLAUDE.md",
            tmp_path / "skills" / "foo" / "SKILL.md",
        ]
        dirs = _get_watch_directories(paths)
        assert tmp_path in dirs
        assert tmp_path / "skills" / "foo" in dirs


class TestCLIWatchFlag:
    def test_cli_accepts_watch_flag(self) -> None:
        """The --watch flag is accepted by setup-eval-lint without error."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("CLAUDE.md").write_text("# Test")
            # Mock run_watch to avoid actually starting the watcher
            with patch("harness_eval_lab.watch.run_watch") as mock_watch:
                result = runner.invoke(cli, ["setup-eval-lint", ".", "--watch"])
                assert result.exit_code == 0
                mock_watch.assert_called_once()

    def test_watch_flag_passes_options(self) -> None:
        """The --watch flag forwards preset and format options."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("CLAUDE.md").write_text("# Test")
            with patch("harness_eval_lab.watch.run_watch") as mock_watch:
                result = runner.invoke(
                    cli,
                    ["setup-eval-lint", ".", "--watch", "--preset", "strict"],
                )
                assert result.exit_code == 0
                mock_watch.assert_called_once_with(
                    path=".",
                    preset="strict",
                    fmt="terminal",
                    user_config=None,
                )


class TestRunWatch:
    def test_raises_without_watchfiles(self, tmp_path: Path) -> None:
        """run_watch raises ClickException when watchfiles is not installed."""
        import click

        (tmp_path / "CLAUDE.md").write_text("# Test")
        with (
            patch.dict("sys.modules", {"watchfiles": None}),
            pytest.raises(click.exceptions.ClickException, match="watchfiles"),
        ):
            run_watch(
                path=str(tmp_path),
                preset="recommended",
                fmt="terminal",
                user_config=None,
            )

    def test_raises_on_empty_directory(self, tmp_path: Path) -> None:
        """run_watch raises ClickException when no setup files are found."""
        import click

        with pytest.raises(click.exceptions.ClickException, match="No agent setup files found"):
            run_watch(
                path=str(tmp_path),
                preset="recommended",
                fmt="terminal",
                user_config=None,
            )
