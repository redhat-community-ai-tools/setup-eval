"""Cursor setup discoverer."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.discoverers.base import ToolDiscoverer, parse_file
from harness_eval_lab.core.types import ComponentType, ParsedComponent


class CursorDiscoverer(ToolDiscoverer):
    """Discovers Cursor setup components."""

    @property
    def tool_name(self) -> str:
        return "Cursor"

    @property
    def source_tool(self) -> str:
        return "cursor"

    def detect(self, root: Path) -> bool:
        return (root / ".cursor").is_dir() or (root / ".cursorrules").is_file()

    def discover(self, root: Path, user_config_dir: Path | None = None) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        results.extend(self._discover_rules(root))
        results.extend(self._discover_commands(root))
        results.extend(self._discover_skills(root))
        results.extend(self._discover_hooks(root))
        results.extend(self._discover_mcp(root))
        return results

    def collect_paths(self, root: Path, user_config_dir: Path | None = None) -> list[Path]:
        paths: list[Path] = []

        # Cursor rules
        cursor_rules_dir = root / ".cursor" / "rules"
        if cursor_rules_dir.is_dir():
            for f in sorted(cursor_rules_dir.rglob("*.mdc")):
                if f.is_file():
                    paths.append(f)

        for f in sorted(root.rglob(".cursorrules")):
            if f.is_file() and ".git" not in f.parts:
                paths.append(f)

        # Cursor commands
        cursor_commands = root / ".cursor" / "commands"
        if cursor_commands.is_dir():
            for f in sorted(cursor_commands.iterdir()):
                if f.is_file() and f.suffix == ".md":
                    paths.append(f)

        # Cursor skills
        cursor_skills = root / ".cursor" / "skills"
        if cursor_skills.is_dir():
            for f in sorted(cursor_skills.rglob("SKILL.md")):
                paths.append(f)

        # Cursor hooks
        cursor_hooks = root / ".cursor" / "hooks.json"
        if cursor_hooks.is_file():
            paths.append(cursor_hooks)

        # Cursor MCP
        cursor_mcp = root / ".cursor" / "mcp.json"
        if cursor_mcp.is_file():
            paths.append(cursor_mcp)

        return paths

    def _discover_rules(self, root: Path) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        seen_paths: set[str] = set()

        cursor_rules_dir = root / ".cursor" / "rules"
        if cursor_rules_dir.is_dir():
            for f in sorted(cursor_rules_dir.rglob("*.mdc")):
                if f.is_file():
                    resolved = str(f.resolve())
                    if resolved not in seen_paths:
                        seen_paths.add(resolved)
                        results.append(
                            parse_file(
                                f, ComponentType.CLAUDE_MD, name=f.stem, source_tool="cursor"
                            )
                        )

        for f in sorted(root.rglob(".cursorrules")):
            if f.is_file() and ".git" not in f.parts:
                resolved = str(f.resolve())
                if resolved not in seen_paths:
                    seen_paths.add(resolved)
                    rel = f.relative_to(root)
                    name = str(rel) if rel != Path(".cursorrules") else ".cursorrules"
                    results.append(
                        parse_file(f, ComponentType.CLAUDE_MD, name=name, source_tool="cursor")
                    )

        return results

    def _discover_commands(self, root: Path) -> list[ParsedComponent]:
        results = []
        commands_dir = root / ".cursor" / "commands"
        if not commands_dir.is_dir():
            return results
        for f in sorted(commands_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                results.append(
                    parse_file(f, ComponentType.COMMAND, name=f.stem, source_tool="cursor")
                )
        return results

    def _discover_skills(self, root: Path) -> list[ParsedComponent]:
        results = []
        seen_paths: set[str] = set()
        skills_dir = root / ".cursor" / "skills"
        if not skills_dir.is_dir():
            return results
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            resolved = str(skill_md.resolve())
            if resolved not in seen_paths:
                seen_paths.add(resolved)
                results.append(
                    parse_file(
                        skill_md,
                        ComponentType.SKILL,
                        name=skill_md.parent.name,
                        source_tool="cursor",
                    )
                )
        return results

    def _discover_hooks(self, root: Path) -> list[ParsedComponent]:
        hooks_file = root / ".cursor" / "hooks.json"
        if hooks_file.is_file():
            return [
                parse_file(hooks_file, ComponentType.HOOKS, name="hooks.json", source_tool="cursor")
            ]
        return []

    def _discover_mcp(self, root: Path) -> list[ParsedComponent]:
        mcp_file = root / ".cursor" / "mcp.json"
        if mcp_file.is_file():
            return [
                parse_file(
                    mcp_file,
                    ComponentType.MCP_CONFIG,
                    name=".cursor/mcp.json",
                    source_tool="cursor",
                )
            ]
        return []
