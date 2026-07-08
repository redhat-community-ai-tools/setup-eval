# Multi-Tool Expansion: Codex, Cline, Gemini CLI, Windsurf

**Status:** in progress
**Created:** 2026-06-17
**Depends on:** runner-abstraction (SetupDiscoverer ABC) - implemented in v3.8.0
**Partially implemented:** 2026-07-03 (v3.8.0: Copilot, Gemini CLI, OpenCode added. Windsurf and Cline remain future.)

## Problem

setup-eval currently supports Claude Code and Cursor. Other AI coding tools have growing adoption but their setups cannot be evaluated. Each tool stores configuration in different locations with different file formats, but the evaluation rules (redundancy, injection, token budget, quality) are largely tool-agnostic.

The runner-abstraction plan (`future-plans/runner-abstraction/spec.md`) defines the `SetupDiscoverer` ABC. This plan extends it with concrete discoverers for 4 additional tools.

## Tool file patterns and ComponentType mapping

| Tool | Config file(s) | Maps to | Notes |
|------|----------------|---------|-------|
| Windsurf | `.windsurfrules` | CLAUDE_MD | Plain markdown, similar to `.cursorrules` |
| Windsurf | `.windsurf/rules/*.md` | CLAUDE_MD | Per-topic rule files |
| Cline | `.clinerules` (single file) | CLAUDE_MD | Plain markdown |
| Cline | `.clinerules/*.md` (directory) | CLAUDE_MD | Per-topic rule files |
| Codex | `AGENTS.md` | CLAUDE_MD | Markdown with optional frontmatter |
| Codex | `.codex/config.toml` | HOOKS | TOML config, maps to settings/hooks |
| Codex | `.codex/hooks.json` | HOOKS | Hook definitions |
| Gemini CLI | `GEMINI.md` | CLAUDE_MD | Plain markdown context file |

## Priority order

1. **Windsurf** (simplest): `.windsurfrules` is nearly identical to `.cursorrules`. The existing Cursor parser can be reused with minimal changes. `.windsurf/rules/*.md` follows the same pattern as `.cursor/rules/*.mdc` but uses plain markdown instead of MDC format.

2. **Cline** (simple): `.clinerules` can be a single file or a directory of `.md` files. Both map directly to CLAUDE_MD. No frontmatter parsing needed.

3. **Codex** (moderate): `AGENTS.md` maps to CLAUDE_MD. The `.codex/` directory contains `config.toml` and `hooks.json` which need new parsers for TOML and JSON hook formats.

4. **Gemini CLI** (simple, low priority): `GEMINI.md` maps to CLAUDE_MD. Single file, plain markdown. Low priority because Gemini CLI adoption is smaller.

## Implementation effort estimates

| Tool | Effort | New code | Reuses |
|------|--------|----------|--------|
| Windsurf | 1-2 hours | WindsurfDiscoverer class | Cursor parser logic |
| Cline | 1-2 hours | ClineDiscoverer class | CLAUDE_MD parser |
| Codex | 3-4 hours | CodexDiscoverer, TOML parser | CLAUDE_MD parser for AGENTS.md |
| Gemini CLI | 1 hour | GeminiDiscoverer class | CLAUDE_MD parser |

## User stories

### Story 1: Evaluate a Windsurf project

**Given** a project with `.windsurfrules` and `.windsurf/rules/coding.md`
**When** `setup-eval lint .` is run
**Then** the tool auto-detects Windsurf, discovers both rule files, runs all applicable rules, and reports findings.

### Story 2: Evaluate a Codex project

**Given** a project with `AGENTS.md` and `.codex/hooks.json`
**When** `setup-eval lint .` is run
**Then** the tool discovers AGENTS.md as system instructions and hooks.json as hook config, applies rules to both.

### Story 3: Multi-tool project

**Given** a project with `CLAUDE.md`, `.windsurfrules`, and `AGENTS.md`
**When** `setup-eval lint .` is run without `--tool`
**Then** the tool detects all three tools and evaluates all setup files, deduplicating shared components (e.g., `skills/` used by both Claude Code and Windsurf).

## Requirements

1. Each discoverer must implement the `SetupDiscoverer` ABC from the runner-abstraction plan.
2. Detection must be based on file existence (glob patterns), not heuristics.
3. All 43 existing lint rules must work on components from any discoverer without tool-specific branching in rule logic.
4. File format differences (MDC vs plain markdown, TOML vs JSON) must be handled in the discoverer/parser layer, not in rules.
5. Shared components (e.g., `skills/*/SKILL.md` used by multiple tools) must be deduplicated.
6. Tests must include fixture directories for each new tool with representative config files.

## Success criteria

- At least Windsurf and Cline discoverers are implemented and pass tests.
- Adding a new tool requires only a new discoverer file and registry entry.
- `setup-eval lint .` on a multi-tool project produces correct, deduplicated results.
- Existing Claude Code and Cursor tests pass unchanged.

## Open questions

1. **Cline directory vs file**: `.clinerules` can be a single file or a directory. Should the discoverer handle both? (Probably yes, check if path is file or directory.)

2. **Codex TOML parsing**: Should we add `tomllib` (stdlib in 3.11+) as a dependency, or use a TOML regex parser? `tomllib` is the right choice since we already require Python 3.11+.

3. **AGENTS.md ownership**: Multiple tools use `AGENTS.md` (Codex, opencode). Should it be attributed to a specific tool or treated as tool-neutral?

4. **Windsurf MDC format**: Does Windsurf use the same MDC frontmatter format as Cursor, or plain markdown? If plain markdown, the parser is simpler but we lose frontmatter metadata (alwaysApply, globs, description).

5. **Detection priority**: If both `.windsurfrules` and `.cursorrules` exist, should both tools be reported? (Likely yes, with deduplication of overlapping content.)
