# setup-eval

[![CI](https://github.com/redhat-community-ai-tools/harness-eval-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/redhat-community-ai-tools/harness-eval-lab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/setup-eval)](https://pypi.org/project/setup-eval/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

Evaluate AI code agent setups for best practices, redundancy, security, and cross-component issues.

Available as a **CLI tool**, a **Claude Code plugin**, and **Cursor commands**.

Supports Claude Code and Cursor projects. Auto-detects which tool(s) a project uses.

## What it does

Most tools test whether a skill produces correct output. This tool checks the setup itself: CLAUDE.md, skills, commands, hooks, MCP configs, agents, `.cursor/rules/*.mdc`, `.cursorrules`.

Four commands, same engine:

| Command | What it does | LLM in CLI | LLM in Claude Code / Cursor |
|---------|-------------|-----------|----------------------------|
| `setup-eval-lint` | 43 deterministic rules + system analysis (token budget, trigger overlaps, dependencies). Fast, CI-suitable. | No | No |
| `setup-eval-review` | Per-component rubric review with 0-3 scoring per dimension, 21 cross-type checks. KEEP/REVIEW/REMOVE verdicts. | Yes (API key) | Yes (in-session) |
| `setup-eval-security` | All security rules + YARA + CVE lookups + semantic review. SAFE/CAUTION/UNSAFE. | Scan: no. Semantic review: `--review` flag | Yes (in-session) |
| `eval-skill` | Deep-evaluate one skill individually and in context of the full setup. | Lint: no. Rubric: `--rubric` flag | Yes (in-session) |

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
/plugin install setup-eval@setup-eval
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

## Inspection Rules (43)

| Category | Rules | What they check |
|----------|-------|-----------------|
| Structural | 1 | SKILL.md exists |
| Frontmatter | 3 | Description required/quality, format valid |
| Content | 4 | Duplicate detection (TF-IDF), broken references, circular references, token budget |
| Security | 9 | Credential access, prompt injection (17 patterns), data exfiltration, obfuscation, reverse shells, AST analysis, taint tracking, MCP least-privilege, tool poisoning |
| Security (opt-in) | 2 | YARA signatures, CVE lookups via OSV.dev |
| Commands | 8 | Description, script exists, duplicates, credentials, injection, skill overlap, shadows built-in, references nonexistent skill |
| CLAUDE.md | 3 | Exists, skill duplication, generic advice detection |
| Hooks | 1 | Structure validation, dangerous patterns, network access |
| Agents | 9 | Description, skills exist, tool format, constraint matching, credentials, injection, exfiltration, obfuscation, reverse shells |

Four presets: `recommended` (default), `strict`, `security`, `pre-workflow`.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for adding rules and submitting PRs.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for release history.

## Future Plans

See [`future-plans/`](future-plans/) for planned improvements (SARIF output, security benchmarks, runner abstraction, dynamic workflows, impact measurement).
