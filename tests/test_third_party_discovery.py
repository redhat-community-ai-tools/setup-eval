"""Tests for third-party module discovery (.lola/modules/)."""

from __future__ import annotations

from pathlib import Path

import pytest

from harness_eval_lab.core.setup import _detect_tools, discover_setup
from harness_eval_lab.core.types import ComponentType


@pytest.fixture
def third_party_setup_path():
    return str(Path(__file__).parent / "fixtures" / "sample-third-party-setup")


class TestThirdPartyDiscovery:
    def test_discovers_skills(self, third_party_setup_path):
        setup = discover_setup("test", third_party_setup_path)
        skills = setup.by_type(ComponentType.SKILL)
        assert len(skills) >= 1
        assert any(s.name == "lint-check" for s in skills)

    def test_discovers_commands(self, third_party_setup_path):
        setup = discover_setup("test", third_party_setup_path)
        commands = setup.by_type(ComponentType.COMMAND)
        assert len(commands) >= 1
        assert any(c.name == "lint" for c in commands)

    def test_discovers_agents(self, third_party_setup_path):
        setup = discover_setup("test", third_party_setup_path)
        agents = setup.by_type(ComponentType.AGENT)
        assert len(agents) >= 1
        assert any(a.name == "linter" for a in agents)


class TestThirdPartySourceTool:
    def test_source_tool_attribution(self, third_party_setup_path):
        setup = discover_setup("test", third_party_setup_path)
        third_party = [c for c in setup.components if c.source_tool == "third-party"]
        assert len(third_party) >= 3

    def test_all_components_are_third_party(self, third_party_setup_path):
        setup = discover_setup("test", third_party_setup_path)
        for comp in setup.components:
            if comp.component_type != ComponentType.UNCATEGORIZED:
                assert comp.source_tool == "third-party"


class TestThirdPartyDetection:
    def test_detects_third_party_modules(self, third_party_setup_path):
        tools = _detect_tools(Path(third_party_setup_path))
        assert "Third-party modules" in tools

    def test_no_detection_without_modules(self, tmp_path):
        tools = _detect_tools(tmp_path)
        assert "Third-party modules" not in tools


class TestThirdPartyInspection:
    def test_lint_runs_on_third_party_skills(self, third_party_setup_path):
        from harness_eval_lab.inspection.engine import inspect_setup

        setup = discover_setup("test", third_party_setup_path)
        results = inspect_setup(setup)
        assert len(results) >= 1
