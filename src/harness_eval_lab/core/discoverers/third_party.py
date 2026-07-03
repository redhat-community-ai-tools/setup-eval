"""Third-party module discoverer (.lola/modules/)."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.discoverers.base import ToolDiscoverer, parse_file
from harness_eval_lab.core.types import ComponentType, ParsedComponent


class ThirdPartyDiscoverer(ToolDiscoverer):
    """Discovers third-party module components from .lola/modules/."""

    @property
    def tool_name(self) -> str:
        return "Third-party modules"

    @property
    def source_tool(self) -> str:
        return "third-party"

    def detect(self, root: Path) -> bool:
        return (root / ".lola" / "modules").is_dir()

    def discover(self, root: Path, user_config_dir: Path | None = None) -> list[ParsedComponent]:
        results: list[ParsedComponent] = []
        modules_dir = root / ".lola" / "modules"
        if not modules_dir.is_dir():
            return results

        for module_dir in sorted(modules_dir.iterdir()):
            if not module_dir.is_dir():
                continue

            skills_dir = module_dir / "skills"
            if skills_dir.is_dir():
                for skill_md in sorted(skills_dir.rglob("SKILL.md")):
                    results.append(
                        parse_file(
                            skill_md,
                            ComponentType.SKILL,
                            name=skill_md.parent.name,
                            source_tool="third-party",
                        )
                    )

            commands_dir = module_dir / "commands"
            if commands_dir.is_dir():
                for f in sorted(commands_dir.iterdir()):
                    if f.is_file() and f.suffix == ".md":
                        results.append(
                            parse_file(f, ComponentType.COMMAND, source_tool="third-party")
                        )

            agents_dir = module_dir / "agents"
            if agents_dir.is_dir():
                for f in sorted(agents_dir.glob("*.md")):
                    if f.is_file():
                        results.append(
                            parse_file(f, ComponentType.AGENT, source_tool="third-party")
                        )

        return results

    def collect_paths(self, root: Path, user_config_dir: Path | None = None) -> list[Path]:
        paths: list[Path] = []
        modules_dir = root / ".lola" / "modules"
        if not modules_dir.is_dir():
            return paths

        for module_dir in sorted(modules_dir.iterdir()):
            if not module_dir.is_dir():
                continue
            skills_dir = module_dir / "skills"
            if skills_dir.is_dir():
                for f in sorted(skills_dir.rglob("SKILL.md")):
                    paths.append(f)
            commands_dir = module_dir / "commands"
            if commands_dir.is_dir():
                for f in sorted(commands_dir.iterdir()):
                    if f.is_file() and f.suffix == ".md":
                        paths.append(f)
            agents_dir = module_dir / "agents"
            if agents_dir.is_dir():
                for f in sorted(agents_dir.glob("*.md")):
                    if f.is_file():
                        paths.append(f)

        return paths
