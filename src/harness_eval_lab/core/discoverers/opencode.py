"""OpenCode setup discoverer."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.discoverers.base import ToolDiscoverer, parse_file
from harness_eval_lab.core.types import ComponentType, ParsedComponent


class OpenCodeDiscoverer(ToolDiscoverer):
    """Discovers OpenCode setup components."""

    @property
    def tool_name(self) -> str:
        return "OpenCode"

    @property
    def source_tool(self) -> str:
        return "opencode"

    def detect(self, root: Path) -> bool:
        return (root / "AGENTS.md").is_file() or (root / ".opencode").is_dir()

    def discover(self, root: Path, user_config_dir: Path | None = None) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        results.extend(self._discover_instructions(root))
        results.extend(self._discover_commands(root))
        results.extend(self._discover_agents(root))
        return results

    def collect_paths(self, root: Path, user_config_dir: Path | None = None) -> list[Path]:
        paths: list[Path] = []

        # OpenCode instructions
        agents_md = root / "AGENTS.md"
        if agents_md.is_file():
            paths.append(agents_md)

        # OpenCode commands
        opencode_commands = root / ".opencode" / "commands"
        if opencode_commands.is_dir():
            for f in sorted(opencode_commands.iterdir()):
                if f.is_file() and f.suffix == ".md":
                    paths.append(f)

        # OpenCode agents
        opencode_agents = root / ".opencode" / "agents"
        if opencode_agents.is_dir():
            for f in sorted(opencode_agents.glob("*.md")):
                if f.is_file():
                    paths.append(f)

        return paths

    def _discover_instructions(self, root: Path) -> list[ParsedComponent]:
        agents_md = root / "AGENTS.md"
        if agents_md.is_file():
            return [parse_file(agents_md, ComponentType.CLAUDE_MD, source_tool="opencode")]
        return []

    def _discover_commands(self, root: Path) -> list[ParsedComponent]:
        results = []
        commands_dir = root / ".opencode" / "commands"
        if not commands_dir.is_dir():
            return results
        for f in sorted(commands_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                results.append(
                    parse_file(f, ComponentType.COMMAND, name=f.stem, source_tool="opencode")
                )
        return results

    def _discover_agents(self, root: Path) -> list[ParsedComponent]:
        results = []
        agents_dir = root / ".opencode" / "agents"
        if not agents_dir.is_dir():
            return results
        for f in sorted(agents_dir.glob("*.md")):
            if f.is_file():
                results.append(parse_file(f, ComponentType.AGENT, source_tool="opencode"))
        return results
