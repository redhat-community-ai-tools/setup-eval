"""Gemini CLI setup discoverer."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.discoverers.base import ToolDiscoverer, parse_file
from harness_eval_lab.core.types import ComponentType, ParsedComponent


class GeminiDiscoverer(ToolDiscoverer):
    """Discovers Gemini CLI setup components."""

    @property
    def tool_name(self) -> str:
        return "Gemini CLI"

    @property
    def source_tool(self) -> str:
        return "gemini"

    def detect(self, root: Path) -> bool:
        return (root / "GEMINI.md").is_file() or (root / ".gemini").is_dir()

    def discover(self, root: Path, user_config_dir: Path | None = None) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        results.extend(self._discover_instructions(root))
        results.extend(self._discover_commands(root))
        return results

    def collect_paths(self, root: Path, user_config_dir: Path | None = None) -> list[Path]:
        paths: list[Path] = []

        # Gemini instructions
        gemini_md = root / "GEMINI.md"
        if gemini_md.is_file():
            paths.append(gemini_md)

        # Gemini commands
        gemini_commands = root / ".gemini" / "commands"
        if gemini_commands.is_dir():
            for f in sorted(gemini_commands.iterdir()):
                if f.is_file() and (f.suffix == ".toml" or f.suffix == ".md"):
                    paths.append(f)

        return paths

    def _discover_instructions(self, root: Path) -> list[ParsedComponent]:
        gemini_md = root / "GEMINI.md"
        if gemini_md.is_file():
            return [parse_file(gemini_md, ComponentType.CLAUDE_MD, source_tool="gemini")]
        return []

    def _discover_commands(self, root: Path) -> list[ParsedComponent]:
        results = []
        commands_dir = root / ".gemini" / "commands"
        if not commands_dir.is_dir():
            return results
        for f in sorted(commands_dir.iterdir()):
            if f.is_file() and (f.suffix == ".toml" or f.suffix == ".md"):
                results.append(
                    parse_file(f, ComponentType.COMMAND, name=f.stem, source_tool="gemini")
                )
        return results
