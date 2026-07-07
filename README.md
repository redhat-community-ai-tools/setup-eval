# setup-eval

[![CI](https://github.com/redhat-community-ai-tools/harness-eval-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/redhat-community-ai-tools/harness-eval-lab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/setup-eval)](https://pypi.org/project/setup-eval/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Rules](https://img.shields.io/badge/rules-58-blue)](https://github.com/redhat-community-ai-tools/harness-eval-lab#inspection-rules-58)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

Evaluate AI code agent setups for best practices, redundancy, security, and cross-component issues.

Available as a **CLI tool**, a **Claude Code plugin**, and **Cursor commands**.

Supports Claude Code, Cursor, Copilot, Gemini CLI, and OpenCode projects. Auto-detects which tool(s) a project uses. Also discovers third-party modules installed via package managers.

## What it does

Most tools test whether a skill produces correct output. This tool checks the setup itself: CLAUDE.md, GEMINI.md, AGENTS.md, skills, commands, hooks, MCP configs, agents, `.cursor/rules/*.mdc`, `.cursorrules`, `.github/prompts/`, `.opencode/`.

Four commands, same engine:

| Command | What it does | LLM in CLI | LLM in Claude Code / Cursor |
|---------|-------------|-----------|----------------------------|
| `setup-eval-lint` | 58 deterministic rules + system analysis (token budget, trigger overlaps, dependencies). Fast, CI-suitable. Supports `--format sarif` for GitHub code scanning. | No | No |
| `setup-eval-review` | Per-component rubric review with 0-3 scoring per dimension, 21 cross-type checks. KEEP/REVIEW/REMOVE verdicts. | Yes (API key) | Yes (in-session) |
| `setup-eval-security` | All security rules + YARA + CVE lookups + semantic review. SAFE/CAUTION/UNSAFE. | Scan: no. Semantic review: `--review` flag | Yes (in-session) |
| `eval-skill` | Deep-evaluate one skill individually and in context of the full setup. | Lint: no. Rubric: `--rubric` flag | Yes (in-session) |

## Supported AI Assistants

Auto-detects which tool(s) a project uses and evaluates all discovered components.

| Assistant | What it discovers |
|-----------|------------------|
| Claude Code | `CLAUDE.md`, `skills/`, `commands/`, `.claude/agents/`, `.claude/settings.json`, `.mcp.json` |
| Cursor | `.cursor/rules/*.mdc`, `.cursorrules`, `.cursor/commands/`, `.cursor/skills/`, `.cursor/hooks.json`, `.cursor/mcp.json` |
| Copilot | `.github/skills/`, `.github/prompts/`, `.github/agents/` |
| Gemini CLI | `GEMINI.md`, `.gemini/commands/` |
| OpenCode | `AGENTS.md`, `.opencode/commands/`, `.opencode/agents/` |
| Third-party modules | `.lola/modules/` (skills, commands, agents installed via package managers) |

Multi-tool projects are fully supported. When a project contains files for multiple assistants, all are discovered, deduplicated, and evaluated together.

## Install

### CLI tool

Install from PyPI and run from the terminal:

```bash
pip install setup-eval

setup-eval setup-eval-lint .
setup-eval setup-eval-lint . --watch     # re-run lint automatically on file changes
setup-eval setup-eval-review . --provider gemini
setup-eval setup-eval-security . --review
setup-eval eval-skill ./skills/my-skill --context . --rubric
```

Requires `GEMINI_API_KEY` or `ANTHROPIC_API_KEY` for review/security/skill commands.

`setup-eval-security` supports optional YARA malware signature scanning. To enable it: `pip install setup-eval[yara]`

### Claude Code plugin

No pip install needed. Install directly from within Claude Code:

```
/plugin marketplace add redhat-community-ai-tools/harness-eval-lab
/plugin install setup-eval@harness-eval-lab
/reload-plugins
```

The 4 commands appear in the `/` menu:
- `/setup-eval:setup-eval-lint`
- `/setup-eval:setup-eval-review`
- `/setup-eval:setup-eval-security`
- `/setup-eval:eval-skill`

No API key needed. Claude evaluates in-session.

**Updating:** Re-run the install command to get the latest rules.

### Cursor commands

Requires the CLI tool installed first (Cursor commands call it for the deterministic scan):

```bash
pip install setup-eval
```

Then copy `.cursor/commands/` from [this repo](https://github.com/redhat-community-ai-tools/harness-eval-lab) into your project. The 4 commands appear in Cursor's command palette:
- `/setup-eval-lint`
- `/setup-eval-review`
- `/setup-eval-security`
- `/eval-skill`

No API key needed for review/security/skill. Cursor evaluates in-session.

## Inspection Rules (58)

| Category | Rules | What they check |
|----------|-------|-----------------|
| Structural | 1 | SKILL.md exists |
| Frontmatter | 3 | Description required/quality, format valid |
| Content | 4 | Duplicate detection (TF-IDF), broken references, circular references, token budget |
| Quality | 5 | Imprecise instructions (hedging, passive voice, vague conditions), redundant guidance (model defaults + tooling config), unfinished content (placeholders, empty sections, deferred markers), example gap, stale references |
| Security | 10 | Credential access, prompt injection (17 patterns), data exfiltration, obfuscation, reverse shells, AST analysis, Python taint tracking, bash taint tracking, MCP least-privilege, tool poisoning |
| Security (opt-in) | 2 | YARA signatures, CVE lookups via OSV.dev |
| Commands | 11 | Description, script exists, duplicates, credentials, injection, exfiltration, obfuscation, reverse shells, skill overlap, shadows built-in, references nonexistent skill |
| CLAUDE.md | 3 | Exists, skill duplication, generic advice detection |
| MCP | 4 | Configuration structure, duplicate servers, suspicious endpoints (localhost/private IPs), wildcard tool exposure |
| Hooks | 5 | Structure validation, script boundary, dangerous commands, env variable leakage, network access |
| Agents | 10 | Description, model specified, skills exist, tool format, constraint matching, credentials, injection, exfiltration, obfuscation, reverse shells |

Four presets: `recommended` (default), `strict`, `security`, `pre-workflow`.

## Security

For a full overview of how this tool protects your code, your credentials, and your supply chain, see [`how-can-you-know-its-safe-to-use-this-tool.md`](how-can-you-know-its-safe-to-use-this-tool.md).

## Privacy and Data Handling

`setup-eval` reads files from your project directory to analyze your AI agent setup. Here is what happens with your data in each mode:

| Command | Sends data externally? | What is sent | Where |
|---------|----------------------|--------------|-------|
| `setup-eval-lint` | No | Nothing. Fully offline. | N/A |
| `setup-eval-review` | Yes (CLI only) | Code snippets from your setup files | Gemini or Anthropic API (your choice via `--provider`) |
| `setup-eval-security` | Scan: No. `--review`: Yes (CLI only) | Code snippets from flagged files | Gemini or Anthropic API |
| `eval-skill` | Lint: No. `--rubric`: Yes (CLI only) | The skill content being evaluated | Gemini or Anthropic API |

When used as a **Claude Code plugin**, review/security/eval-skill commands use the existing Claude session. No additional API calls are made.

When used as **Cursor commands**, the evaluation happens in the Cursor session. No additional API calls are made.

**File access:** The tool only reads files within the project directory you point it at. Path traversal protections prevent reading files outside the project boundary.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for adding rules and submitting PRs.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for release history.

## Future Plans

See [`future-plans/`](future-plans/) for planned improvements (security benchmarks, runner abstraction, dynamic workflows, impact measurement).
