"""GitHub Copilot setup discoverer."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.discoverers.base import ToolDiscoverer, parse_file
from harness_eval_lab.core.types import ComponentType, ParsedComponent


class CopilotDiscoverer(ToolDiscoverer):
    """Discovers GitHub Copilot setup components."""

    @property
    def tool_name(self) -> str:
        return "Copilot"

    @property
    def source_tool(self) -> str:
        return "copilot"

    def detect(self, root: Path) -> bool:
        return (
            (root / ".github" / "prompts").is_dir()
            or (root / ".github" / "agents").is_dir()
            or (root / ".github" / "skills").is_dir()
        )

    def discover(self, root: Path, user_config_dir: Path | None = None) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        results.extend(self._discover_skills(root))
        results.extend(self._discover_commands(root))
        results.extend(self._discover_agents(root))
        return results

    def collect_paths(self, root: Path, user_config_dir: Path | None = None) -> list[Path]:
        paths: list[Path] = []

        # Copilot skills
        copilot_skills = root / ".github" / "skills"
        if copilot_skills.is_dir():
            for f in sorted(copilot_skills.rglob("SKILL.md")):
                paths.append(f)

        # Copilot commands (prompts)
        copilot_commands = root / ".github" / "prompts"
        if copilot_commands.is_dir():
            for f in sorted(copilot_commands.iterdir()):
                if f.is_file() and f.suffix == ".md":
                    paths.append(f)

        # Copilot agents
        copilot_agents = root / ".github" / "agents"
        if copilot_agents.is_dir():
            for f in sorted(copilot_agents.glob("*.md")):
                if f.is_file():
                    paths.append(f)

        return paths

    def _discover_skills(self, root: Path) -> list[ParsedComponent]:
        results = []
        skills_dir = root / ".github" / "skills"
        if not skills_dir.is_dir():
            return results
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            results.append(
                parse_file(
                    skill_md,
                    ComponentType.SKILL,
                    name=skill_md.parent.name,
                    source_tool="copilot",
                )
            )
        return results

    def _discover_commands(self, root: Path) -> list[ParsedComponent]:
        results = []
        commands_dir = root / ".github" / "prompts"
        if not commands_dir.is_dir():
            return results
        for f in sorted(commands_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                results.append(
                    parse_file(f, ComponentType.COMMAND, name=f.stem, source_tool="copilot")
                )
        return results

    def _discover_agents(self, root: Path) -> list[ParsedComponent]:
        results = []
        agents_dir = root / ".github" / "agents"
        if not agents_dir.is_dir():
            return results
        for f in sorted(agents_dir.glob("*.md")):
            if f.is_file():
                results.append(parse_file(f, ComponentType.AGENT, source_tool="copilot"))
        return results
