"""Setup discovery: walk a directory and parse all agent components."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.core.fingerprint import fingerprint_setup
from harness_eval_lab.core.types import (
    ComponentScope,
    ComponentType,
    ParsedComponent,
    Setup,
)
from harness_eval_lab.utils.parsing import parse_frontmatter
from harness_eval_lab.utils.tokens import count_tokens


def discover_setup(
    name: str,
    path: str,
    user_config_dir: str | None = None,
) -> Setup:
    """Walk a directory and discover all agent-relevant components."""
    root = Path(path)
    if not root.is_dir():
        raise FileNotFoundError(f"Setup path does not exist: {path}")

    user_dir = Path(user_config_dir) if user_config_dir else None

    components: list[ParsedComponent] = []

    components.extend(_discover_claude_md(root, user_dir))
    components.extend(_discover_skills(root))
    components.extend(_discover_commands(root))
    components.extend(_discover_hooks(root))
    components.extend(_discover_agents(root))
    components.extend(_discover_mcp_configs(root))

    fp = fingerprint_setup(path, user_config_dir=user_config_dir)
    total = sum(c.token_count for c in components)

    return Setup(
        name=name,
        path=path,
        fingerprint=fp,
        components=list(components),
        total_tokens=total,
    )


def _parse_file(
    filepath: Path,
    component_type: ComponentType,
    name: str | None = None,
    scope: ComponentScope = ComponentScope.PROJECT,
) -> ParsedComponent:
    content = filepath.read_text(encoding="utf-8", errors="replace")
    frontmatter, _ = parse_frontmatter(content)
    return ParsedComponent(
        component_type=component_type,
        name=name or filepath.stem,
        path=str(filepath),
        content=content,
        frontmatter=frontmatter,
        token_count=count_tokens(content),
        scope=scope,
    )


def _discover_claude_md(
    root: Path,
    user_config_dir: Path | None = None,
) -> list[ParsedComponent]:
    results: list[ParsedComponent] = []
    seen_paths: set[str] = set()

    # Project-local CLAUDE.md files
    for pattern in ["CLAUDE.md", "**/CLAUDE.md"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                resolved = str(f.resolve())
                if resolved not in seen_paths:
                    seen_paths.add(resolved)
                    results.append(_parse_file(f, ComponentType.CLAUDE_MD))

    if user_config_dir is None:
        return results

    # User-global CLAUDE.md
    user_global = user_config_dir / "CLAUDE.md"
    if user_global.is_file():
        resolved = str(user_global.resolve())
        if resolved not in seen_paths:
            seen_paths.add(resolved)
            results.append(
                _parse_file(
                    user_global,
                    ComponentType.CLAUDE_MD,
                    name="CLAUDE.md (user-global)",
                    scope=ComponentScope.USER_GLOBAL,
                )
            )

    # User-project CLAUDE.md files
    projects_dir = user_config_dir / "projects"
    if projects_dir.is_dir():
        for project_dir in sorted(projects_dir.iterdir()):
            if not project_dir.is_dir():
                continue
            project_claude = project_dir / "CLAUDE.md"
            if project_claude.is_file():
                resolved = str(project_claude.resolve())
                if resolved not in seen_paths:
                    seen_paths.add(resolved)
                    results.append(
                        _parse_file(
                            project_claude,
                            ComponentType.CLAUDE_MD,
                            name=f"CLAUDE.md (user-project: {project_dir.name})",
                            scope=ComponentScope.USER_PROJECT,
                        )
                    )

    return results


def _discover_skills(root: Path) -> list[ParsedComponent]:
    results = []
    seen_paths: set[str] = set()
    for skills_dir in [root / "skills", root / ".claude" / "skills"]:
        if not skills_dir.is_dir():
            continue
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            resolved = str(skill_md.resolve())
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            skill_dir = skill_md.parent
            results.append(_parse_file(skill_md, ComponentType.SKILL, name=skill_dir.name))
    return results


def _discover_commands(root: Path) -> list[ParsedComponent]:
    results = []
    for commands_dir in [root / "commands", root / ".claude" / "commands"]:
        if not commands_dir.is_dir():
            continue
        for item in sorted(commands_dir.iterdir()):
            if item.is_file() and item.suffix == ".md":
                results.append(_parse_file(item, ComponentType.COMMAND))
            elif item.is_dir():
                cmd_md = item / "command.md"
                if cmd_md.is_file():
                    results.append(_parse_file(cmd_md, ComponentType.COMMAND, name=item.name))
    return results


def _discover_hooks(root: Path) -> list[ParsedComponent]:
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        return [_parse_file(settings, ComponentType.HOOKS, name="settings.json")]
    return []


def _discover_agents(root: Path) -> list[ParsedComponent]:
    results = []
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return results
    for f in sorted(agents_dir.glob("*.md")):
        if f.is_file():
            results.append(_parse_file(f, ComponentType.AGENT))
    return results


def _discover_mcp_configs(root: Path) -> list[ParsedComponent]:
    results = []
    for pattern in [".mcp.json", "**/.mcp.json"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                results.append(_parse_file(f, ComponentType.MCP_CONFIG))
    seen_paths: set[str] = set()
    deduped = []
    for c in results:
        if c.path not in seen_paths:
            seen_paths.add(c.path)
            deduped.append(c)
    return deduped
