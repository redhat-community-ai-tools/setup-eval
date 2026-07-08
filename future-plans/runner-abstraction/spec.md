# Setup Discoverer Abstraction: Multi-Tool Evaluation

**Status:** built
**Created:** 2026-06-10
**Implemented:** 2026-07-03 (v3.8.0, `core/discoverers/` package with `ToolDiscoverer` ABC)

## Problem

setup-eval is hardcoded to Claude Code's setup format. The `discover_setup()` function in `src/setup_eval/core/setup.py` searches for Claude-specific file paths (`CLAUDE.md`, `.claude/settings.json`, `.claude/agents/*.md`, `skills/*/SKILL.md`). The fingerprinter in `core/fingerprint.py` has its own hardcoded `RELEVANT_PATTERNS` list matching the same Claude-specific paths.

But the evaluation rules themselves are largely tool-agnostic. Redundancy detection, prompt injection scanning, token budget analysis, structural quality checks: these apply to any AI coding tool's setup files. The tool-specific part is only _where the files live and how they map to concepts_ like "system instructions," "skills/rules," and "tool configuration."

Other AI coding tools have their own setup formats:

- **Cursor:** `.cursor/rules/*.mdc` files, legacy `.cursorrules` in project root
- **GitHub Copilot:** `.github/copilot-instructions.md`, plus per-repo config
- **Windsurf:** `.windsurfrules` in project root
- **Agent Skills spec (agentskills.io):** `skills/*/SKILL.md` (cross-tool, already partially supported)

Without an abstraction, supporting each new tool means forking the discovery code, duplicating the fingerprinter, and threading tool-specific conditionals through the entire codebase.

## Proposal

Introduce a `SetupDiscoverer` abstract base class that decouples file discovery from the evaluation engine. Each supported tool gets a concrete discoverer that knows where its setup files live and how to map them to the existing `ComponentType` enum and `ParsedComponent` model.

### Architecture

```
src/setup_eval/core/
    discoverer.py         # ABC + registry
    discoverers/
        __init__.py
        claude.py         # Extracts current logic from setup.py
        cursor.py
        copilot.py
        windsurf.py
```

### Base class (in `discoverer.py`)

```python
from abc import ABC, abstractmethod
from harness_eval_lab.core.types import ParsedComponent, Setup


class SetupDiscoverer(ABC):
    """Discovers and parses setup files for a specific AI coding tool."""

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Human-readable name, e.g. 'Claude Code', 'Cursor'."""

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Machine identifier, e.g. 'claude', 'cursor'."""

    @property
    @abstractmethod
    def file_patterns(self) -> list[str]:
        """Glob patterns for all files this tool considers setup-relevant.

        Used by the fingerprinter to compute change hashes.
        """

    @abstractmethod
    def discover(self, root: Path, **kwargs) -> list[ParsedComponent]:
        """Walk root and return parsed components in the common model."""

    def detect(self, root: Path) -> bool:
        """Return True if this tool's setup files exist under root.

        Default implementation checks if any file_patterns match.
        """
        for pattern in self.file_patterns:
            if any(root.glob(pattern)):
                return True
        return False
```

### How it works

1. **Discovery:** `discover_setup()` accepts an optional `tool` parameter. If omitted, it calls `detect()` on each registered discoverer to auto-detect the tool. If multiple tools are detected, it evaluates all of them (one `Setup` per tool) or the user specifies which one.

2. **Mapping:** Each discoverer maps its tool-specific files to the existing `ComponentType` enum. For example, Cursor's `.cursor/rules/*.mdc` files map to `ComponentType.CLAUDE_MD` (system instructions). This reuse means the entire inspection engine, analysis pipeline, and report generation work unchanged.

3. **Fingerprinting:** The fingerprinter reads `file_patterns` from the active discoverer instead of using a hardcoded list. This keeps fingerprint computation accurate per tool.

4. **CLI integration:** The `--tool` flag lets users specify the tool explicitly. Without it, auto-detection runs. The output report includes the detected tool name.

### ComponentType mapping by tool

| Concept | Claude Code | Cursor | GitHub Copilot | Windsurf |
|---|---|---|---|---|
| System instructions | `CLAUDE.md` | `.cursor/rules/*.mdc`, `.cursorrules` | `.github/copilot-instructions.md` | `.windsurfrules` |
| Skills / rules | `skills/*/SKILL.md` | (rules with frontmatter in `.mdc`) | n/a | n/a |
| Commands | `commands/*.md` | n/a | n/a | n/a |
| Hooks / settings | `.claude/settings.json` | `.cursor/settings.json` | n/a | n/a |
| MCP config | `.mcp.json` | `.cursor/mcp.json` | n/a | n/a |
| Agents | `.claude/agents/*.md` | n/a | n/a | n/a |

### ComponentType enum changes

The existing `ComponentType` values are generic enough to work across tools. `CLAUDE_MD` is the only name that implies a specific tool; renaming it to `SYSTEM_INSTRUCTIONS` would make the model truly tool-neutral. This rename is optional and could be deferred to avoid a breaking change in the first iteration.

Alternatively, keep `CLAUDE_MD` as-is and treat it as "the component type for system-level instructions, regardless of tool." Document this decision.

## User stories

### Story 1: Evaluate a Cursor project

**Given** a developer has a project with `.cursor/rules/coding-standards.mdc` and `.cursorrules`
**When** they run `setup-eval lint .`
**Then** the tool auto-detects Cursor, discovers both rule files as system-instruction components, runs the 26 deterministic rules against them (redundancy, injection, token budget), and reports findings in the same format as a Claude Code evaluation.

### Story 2: Evaluate a multi-tool project

**Given** a project contains both `CLAUDE.md` and `.github/copilot-instructions.md`
**When** they run `setup-eval lint . --tool claude`
**Then** only Claude Code setup files are evaluated. Running without `--tool` detects both tools and produces separate evaluation sections, one per tool.

### Story 3: Add support for a new tool

**Given** a contributor wants to add evaluation support for a new AI coding tool (e.g., Aider)
**When** they create a new file at `src/setup_eval/core/discoverers/aider.py` implementing `SetupDiscoverer`
**Then** the tool automatically discovers Aider setups with no changes to the inspection engine, analysis pipeline, CLI, or report generation. Only the new discoverer file and a registration call are needed.

## Requirements

1. Define `SetupDiscoverer` ABC in `src/setup_eval/core/discoverer.py` with `tool_name`, `tool_id`, `file_patterns`, `discover()`, and `detect()`.
2. Extract current Claude Code discovery logic from `setup.py` into `src/setup_eval/core/discoverers/claude.py` as the first concrete implementation.
3. Create a discoverer registry (dictionary or entry-point based) in `src/setup_eval/core/discoverers/__init__.py` so new tools can be registered without modifying core code.
4. Update `discover_setup()` to accept a `tool: str | None` parameter. When `None`, iterate registered discoverers and call `detect()`. When specified, use that discoverer directly.
5. Update `fingerprint_setup()` to accept `file_patterns` from the active discoverer instead of using `RELEVANT_PATTERNS`.
6. Add `--tool` CLI option to `lint` and `review` commands (choices populated from the registry).
7. Add a `CursorDiscoverer` as the second implementation to validate the abstraction works for a tool with meaningfully different file layouts.
8. Ensure all 26 existing lint rules work on components discovered by any discoverer, with no tool-specific branching in the rule logic.
9. Update the report output to include the detected tool name (e.g., "Tool: Cursor") in both terminal and JSON formats.
10. Preserve full backward compatibility: running without `--tool` on a Claude Code project produces identical results to the current behavior.

## Success criteria

- `discover_setup()` with no `--tool` flag auto-detects Claude Code and produces the same `Setup` object (same components, same fingerprint) as the current implementation.
- At least two discoverers (Claude Code and Cursor) are implemented and pass tests.
- Adding a third discoverer (e.g., Copilot) requires only one new file and a registry entry; zero changes to the engine, analysis, or output modules.
- Existing test suite passes without modification (backward compatibility).
- A new test validates auto-detection when multiple tools' files are present.

## Open questions

1. **ComponentType naming:** Should `CLAUDE_MD` be renamed to `SYSTEM_INSTRUCTIONS`? This improves clarity but is a breaking change for anyone depending on the enum value in JSON output. Could be gated behind a major version bump or kept as an alias.

2. **Cursor `.mdc` frontmatter:** Cursor rule files use a frontmatter format with fields like `alwaysApply`, `globs`, and `description`. Should discoverers parse tool-specific frontmatter into a common schema, or pass it through as-is in the existing `frontmatter: dict` field on `ParsedComponent`?

3. **Cross-tool redundancy detection:** If a project has both `CLAUDE.md` and `.github/copilot-instructions.md` with overlapping content, should the tool flag cross-tool redundancy? This could be valuable (catch copy-paste drift) but adds complexity to the analysis pipeline.

4. **Tool-specific rules:** Some rules only make sense for certain tools (e.g., Claude Code hook validation). Should rules declare which `tool_id` values they apply to, or should they operate on `ComponentType` alone and let the discoverer handle the mapping?

5. **Agent Skills spec overlap:** The Agent Skills spec (`skills/*/SKILL.md`) is already cross-tool by design. Should skills discovered via the Agent Skills spec be attributed to a specific tool, or treated as tool-neutral? If a project has both Claude Code and Cursor setups, should shared skills appear in both evaluations?

6. **User-level config paths:** Claude Code uses `~/.claude/` for user-global config. Cursor uses `~/.cursor/`. How should `user_config_dir` generalize? Should each discoverer define its own default user config path?
