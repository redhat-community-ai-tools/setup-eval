"""Tests for multi-assistant setup discovery (Copilot, Gemini CLI, OpenCode)."""

from pathlib import Path

import pytest

from harness_eval_lab.core.setup import _detect_tools, discover_setup
from harness_eval_lab.core.types import ComponentType


@pytest.fixture
def copilot_setup_path():
    return str(Path(__file__).parent / "fixtures" / "sample-copilot-setup")


@pytest.fixture
def gemini_setup_path():
    return str(Path(__file__).parent / "fixtures" / "sample-gemini-setup")


@pytest.fixture
def opencode_setup_path():
    return str(Path(__file__).parent / "fixtures" / "sample-opencode-setup")


class TestCopilotDiscovery:
    def test_discovers_copilot_skills(self, copilot_setup_path):
        setup = discover_setup("test", copilot_setup_path)
        skills = setup.by_type(ComponentType.SKILL)
        assert any(s.source_tool == "copilot" for s in skills)

    def test_discovers_copilot_commands(self, copilot_setup_path):
        setup = discover_setup("test", copilot_setup_path)
        commands = setup.by_type(ComponentType.COMMAND)
        assert any(c.source_tool == "copilot" for c in commands)

    def test_discovers_copilot_agents(self, copilot_setup_path):
        setup = discover_setup("test", copilot_setup_path)
        agents = setup.by_type(ComponentType.AGENT)
        assert any(a.source_tool == "copilot" for a in agents)

    def test_source_tool_attribution(self, copilot_setup_path):
        setup = discover_setup("test", copilot_setup_path)
        copilot_components = [c for c in setup.components if c.source_tool == "copilot"]
        assert len(copilot_components) >= 3


class TestGeminiDiscovery:
    def test_discovers_gemini_instructions(self, gemini_setup_path):
        setup = discover_setup("test", gemini_setup_path)
        claude_mds = setup.by_type(ComponentType.CLAUDE_MD)
        assert any(c.source_tool == "gemini" for c in claude_mds)

    def test_discovers_gemini_commands(self, gemini_setup_path):
        setup = discover_setup("test", gemini_setup_path)
        commands = setup.by_type(ComponentType.COMMAND)
        assert any(c.source_tool == "gemini" for c in commands)


class TestOpenCodeDiscovery:
    def test_discovers_opencode_instructions(self, opencode_setup_path):
        setup = discover_setup("test", opencode_setup_path)
        claude_mds = setup.by_type(ComponentType.CLAUDE_MD)
        assert any(c.source_tool == "opencode" for c in claude_mds)

    def test_discovers_opencode_commands(self, opencode_setup_path):
        setup = discover_setup("test", opencode_setup_path)
        commands = setup.by_type(ComponentType.COMMAND)
        assert any(c.source_tool == "opencode" for c in commands)

    def test_discovers_opencode_agents(self, opencode_setup_path):
        setup = discover_setup("test", opencode_setup_path)
        agents = setup.by_type(ComponentType.AGENT)
        assert any(a.source_tool == "opencode" for a in agents)


class TestDetectToolsMulti:
    def test_detects_copilot(self, copilot_setup_path):
        tools = _detect_tools(Path(copilot_setup_path))
        assert "Copilot" in tools

    def test_detects_gemini(self, gemini_setup_path):
        tools = _detect_tools(Path(gemini_setup_path))
        assert "Gemini CLI" in tools

    def test_detects_opencode(self, opencode_setup_path):
        tools = _detect_tools(Path(opencode_setup_path))
        assert "OpenCode" in tools

    def test_does_not_detect_absent_tools(self, tmp_path):
        tools = _detect_tools(tmp_path)
        assert "Copilot" not in tools
        assert "Gemini CLI" not in tools
        assert "OpenCode" not in tools


class TestMultiAssistantInspection:
    def test_lint_runs_on_copilot_setup(self, copilot_setup_path):
        from harness_eval_lab.inspection.engine import inspect_setup

        setup = discover_setup("test", copilot_setup_path)
        results = inspect_setup(setup)
        assert len(results) >= 1
        # Should have results for skill, command, and agent
        target_types = {r.target_type for r in results}
        assert "skill" in target_types

    def test_lint_runs_on_opencode_setup(self, opencode_setup_path):
        from harness_eval_lab.inspection.engine import inspect_setup

        setup = discover_setup("test", opencode_setup_path)
        results = inspect_setup(setup)
        assert len(results) >= 1
