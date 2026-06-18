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
    components.extend(_discover_rules(root))
    components.extend(_discover_output_styles(root))
    components.extend(_discover_cursor_rules(root))
    components.extend(_discover_cursor_commands(root))
    components.extend(_discover_cursor_skills(root))
    components.extend(_discover_cursor_hooks(root))
    components.extend(_discover_cursor_mcp(root))

    components = _deduplicate_components(components)
    components.extend(_discover_uncategorized(root, components))

    detected = _detect_tools(root)
    fp = fingerprint_setup(path, user_config_dir=user_config_dir)
    total = sum(c.token_count for c in components)

    return Setup(
        name=name,
        path=path,
        fingerprint=fp,
        components=list(components),
        total_tokens=total,
        detected_tools=detected,
    )


def _parse_file(
    filepath: Path,
    component_type: ComponentType,
    name: str | None = None,
    scope: ComponentScope = ComponentScope.PROJECT,
    source_tool: str | None = None,
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
        source_tool=source_tool,
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
                    results.append(_parse_file(f, ComponentType.CLAUDE_MD, source_tool="claude"))

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
                    source_tool="claude",
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
                            source_tool="claude",
                        )
                    )

    return results


def _discover_skills(root: Path) -> list[ParsedComponent]:
    results = []
    seen_paths: set[str] = set()
    for skills_dir in [root / "skills", root / ".claude" / "skills"]:
        if not skills_dir.is_dir():
            continue
        tool = "claude" if ".claude" in skills_dir.parts else None
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            resolved = str(skill_md.resolve())
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            skill_dir = skill_md.parent
            results.append(
                _parse_file(skill_md, ComponentType.SKILL, name=skill_dir.name, source_tool=tool)
            )
    return results


def _discover_commands(root: Path) -> list[ParsedComponent]:
    results = []
    for commands_dir in [root / "commands", root / ".claude" / "commands"]:
        if not commands_dir.is_dir():
            continue
        tool = "claude" if ".claude" in commands_dir.parts else None
        for item in sorted(commands_dir.iterdir()):
            if item.is_file() and item.suffix == ".md":
                results.append(_parse_file(item, ComponentType.COMMAND, source_tool=tool))
            elif item.is_dir():
                cmd_md = item / "command.md"
                if cmd_md.is_file():
                    results.append(
                        _parse_file(cmd_md, ComponentType.COMMAND, name=item.name, source_tool=tool)
                    )
    return results


def _discover_hooks(root: Path) -> list[ParsedComponent]:
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        return [
            _parse_file(settings, ComponentType.HOOKS, name="settings.json", source_tool="claude")
        ]
    return []


def _discover_agents(root: Path) -> list[ParsedComponent]:
    results = []
    agents_dir = root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return results
    for f in sorted(agents_dir.glob("*.md")):
        if f.is_file():
            results.append(_parse_file(f, ComponentType.AGENT, source_tool="claude"))
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


def _discover_rules(root: Path) -> list[ParsedComponent]:
    results = []
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return results
    for f in sorted(rules_dir.rglob("*")):
        if f.is_file() and f.suffix in (".md", ".yaml", ".yml"):
            results.append(_parse_file(f, ComponentType.RULE, name=f.stem, source_tool="claude"))
    return results


def _discover_output_styles(root: Path) -> list[ParsedComponent]:
    results = []
    styles_dir = root / ".claude" / "output-styles"
    if not styles_dir.is_dir():
        return results
    for f in sorted(styles_dir.rglob("*")):
        if f.is_file() and f.suffix in (".md", ".yaml", ".yml"):
            results.append(
                _parse_file(f, ComponentType.OUTPUT_STYLE, name=f.stem, source_tool="claude")
            )
    return results


def _discover_cursor_rules(root: Path) -> list[ParsedComponent]:
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
                        _parse_file(f, ComponentType.CLAUDE_MD, name=f.stem, source_tool="cursor")
                    )

    for f in sorted(root.rglob(".cursorrules")):
        if f.is_file() and ".git" not in f.parts:
            resolved = str(f.resolve())
            if resolved not in seen_paths:
                seen_paths.add(resolved)
                rel = f.relative_to(root)
                name = str(rel) if rel != Path(".cursorrules") else ".cursorrules"
                results.append(
                    _parse_file(f, ComponentType.CLAUDE_MD, name=name, source_tool="cursor")
                )

    return results


def _discover_cursor_commands(root: Path) -> list[ParsedComponent]:
    results = []
    commands_dir = root / ".cursor" / "commands"
    if not commands_dir.is_dir():
        return results
    for f in sorted(commands_dir.iterdir()):
        if f.is_file() and f.suffix == ".md":
            results.append(_parse_file(f, ComponentType.COMMAND, name=f.stem, source_tool="cursor"))
    return results


def _discover_cursor_skills(root: Path) -> list[ParsedComponent]:
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
                _parse_file(
                    skill_md, ComponentType.SKILL, name=skill_md.parent.name, source_tool="cursor"
                )
            )
    return results


def _discover_cursor_hooks(root: Path) -> list[ParsedComponent]:
    hooks_file = root / ".cursor" / "hooks.json"
    if hooks_file.is_file():
        return [
            _parse_file(hooks_file, ComponentType.HOOKS, name="hooks.json", source_tool="cursor")
        ]
    return []


def _discover_cursor_mcp(root: Path) -> list[ParsedComponent]:
    mcp_file = root / ".cursor" / "mcp.json"
    if mcp_file.is_file():
        return [
            _parse_file(
                mcp_file, ComponentType.MCP_CONFIG, name=".cursor/mcp.json", source_tool="cursor"
            )
        ]
    return []


def collect_setup_file_paths(
    root: Path,
    user_config_dir: Path | None = None,
) -> list[Path]:
    """Return deduplicated file paths that ``discover_setup`` would scan.

    This is the single source of truth for which files constitute an agent
    setup.  Both ``discover_setup`` (for parsing) and watch mode (for
    monitoring) consume this list so they stay in sync automatically.
    """
    paths: list[Path] = []

    # CLAUDE.md — project-local
    for pattern in ["CLAUDE.md", "**/CLAUDE.md"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                paths.append(f)

    # CLAUDE.md — user-config (global + per-project)
    if user_config_dir is not None:
        user_global = user_config_dir / "CLAUDE.md"
        if user_global.is_file():
            paths.append(user_global)
        projects_dir = user_config_dir / "projects"
        if projects_dir.is_dir():
            for project_dir in sorted(projects_dir.iterdir()):
                if project_dir.is_dir():
                    project_claude = project_dir / "CLAUDE.md"
                    if project_claude.is_file():
                        paths.append(project_claude)

    # Skills
    for skills_dir in [root / "skills", root / ".claude" / "skills"]:
        if skills_dir.is_dir():
            for f in sorted(skills_dir.rglob("SKILL.md")):
                paths.append(f)

    # Commands
    for commands_dir in [root / "commands", root / ".claude" / "commands"]:
        if commands_dir.is_dir():
            for item in sorted(commands_dir.iterdir()):
                if item.is_file() and item.suffix == ".md":
                    paths.append(item)
                elif item.is_dir():
                    cmd_md = item / "command.md"
                    if cmd_md.is_file():
                        paths.append(cmd_md)

    # Settings / hooks
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        paths.append(settings)

    # Agents
    agents_dir = root / ".claude" / "agents"
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.md")):
            if f.is_file():
                paths.append(f)

    # MCP configs
    for pattern in [".mcp.json", "**/.mcp.json"]:
        for f in sorted(root.glob(pattern)):
            if f.is_file():
                paths.append(f)

    # Rules
    rules_dir = root / ".claude" / "rules"
    if rules_dir.is_dir():
        for f in sorted(rules_dir.rglob("*")):
            if f.is_file() and f.suffix in (".md", ".yaml", ".yml"):
                paths.append(f)

    # Output styles
    styles_dir = root / ".claude" / "output-styles"
    if styles_dir.is_dir():
        for f in sorted(styles_dir.rglob("*")):
            if f.is_file() and f.suffix in (".md", ".yaml", ".yml"):
                paths.append(f)

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

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        resolved = str(p.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(p)

    return unique


def _detect_tools(root: Path) -> tuple[str, ...]:
    tools = []
    has_claude = (root / "CLAUDE.md").is_file() or (root / ".claude").is_dir()
    has_cursor = (root / ".cursor").is_dir() or (root / ".cursorrules").is_file()
    if has_claude:
        tools.append("Claude Code")
    if has_cursor:
        tools.append("Cursor")
    return tuple(tools)


def _deduplicate_components(components: list[ParsedComponent]) -> list[ParsedComponent]:
    seen: set[str] = set()
    deduped: list[ParsedComponent] = []
    for c in components:
        resolved = str(Path(c.path).resolve())
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(c)
    return deduped


def _discover_uncategorized(
    root: Path, known_components: list[ParsedComponent]
) -> list[ParsedComponent]:
    known_paths = {str(Path(c.path).resolve()) for c in known_components}
    results = []

    skill_dirs = set()
    for c in known_components:
        if c.component_type == ComponentType.SKILL:
            skill_dirs.add(str(Path(c.path).parent.resolve()))

    scan_dirs = [root / ".claude", root / ".cursor", root / "skills", root / "commands"]

    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            continue
        for f in sorted(scan_dir.rglob("*")):
            if not f.is_file():
                continue
            if ".git" in f.parts or "__pycache__" in f.parts:
                continue
            resolved = str(f.resolve())
            if resolved in known_paths:
                continue
            if f.name.startswith("."):
                continue
            if any(resolved.startswith(sd + "/") for sd in skill_dirs):
                continue
            results.append(
                _parse_file(f, ComponentType.UNCATEGORIZED, name=str(f.relative_to(root)))
            )

    return results
