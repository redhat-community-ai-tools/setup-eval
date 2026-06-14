# harness-eval-lab

Evaluate AI agent setups for best practices, redundancy, security, and cross-component issues.

## What it does

Most agent evaluation tools test whether a **skill** completes a task correctly. This tool evaluates the **entire setup** that surrounds the agent: CLAUDE.md, skills, commands, hooks, MCP configs, and sub-agents.

It checks whether each component follows Claude Code best practices, whether components work well together, and whether anything is redundant, conflicting, or insecure.

## Overview

```
 ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
 │ eval-setup-lint │  │ eval-setup-     │  │ eval-setup-     │  │ eval-skill      │
 │                 │  │ review          │  │ security        │  │                 │
 │ 39 rules        │  │ per-component   │  │ all security    │  │ deep-dive on    │
 │ system analysis │  │ rubrics         │  │ rules           │  │ one skill       │
 │ token budget    │  │ 21 cross-type   │  │ AST + taint     │  │ lint + rubric   │
 │ trigger overlap │  │ checks          │  │ YARA + CVE      │  │ + contextual    │
 │ dependencies    │  │ instruction     │  │ 4-check         │  │ analysis        │
 │ context util    │  │ clarity         │  │ semantic review  │  │                 │
 │                 │  │ KEEP / REVIEW   │  │ SAFE / CAUTION  │  │ KEEP / REVIEW   │
 │ no LLM, fast   │  │ / REMOVE        │  │ / UNSAFE        │  │ / REMOVE        │
 └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
   "does it pass?"      "is it effective?"     "is it safe?"       "how is this skill?"
```

## Install

### As a CLI tool

```bash
uv sync
```

Optional extras:

```bash
uv sync --extra llm       # LLM support (for review CLI and eval-skill --rubric)
uv sync --extra security  # YARA signature scanning (for security)
```

### As a Claude Code plugin

Install directly from within Claude Code:

```
/plugin marketplace add redhat-community-ai-tools/harness-eval-lab
/plugin install harness-eval-lab
```

Or test locally during development:

```bash
claude --plugin-dir /path/to/harness-eval-lab
```

After installing, these commands become available in `/` autocomplete:
- `/eval-setup-lint` - fast static analysis, no LLM, CI-suitable
- `/eval-setup-review` - full qualitative review with KEEP/REVIEW/REMOVE verdicts
- `/eval-setup-security` - deep security audit with deterministic scan + semantic review
- `/eval-skill <skill-name>` - deep-evaluate one skill in context

## Usage

### CLI

```bash
harness-eval-lab eval-setup-lint /path/to/project
harness-eval-lab eval-setup-lint /path/to/project --preset strict --format json
harness-eval-lab eval-setup-lint /path/to/project --fail-on-error

export GEMINI_API_KEY=your-key  # or ANTHROPIC_API_KEY
harness-eval-lab eval-setup-review /path/to/project
harness-eval-lab eval-setup-review /path/to/project --provider anthropic --model claude-sonnet-4-20250514

harness-eval-lab eval-setup-security /path/to/project
harness-eval-lab eval-setup-security /path/to/project --review --provider gemini

harness-eval-lab eval-skill /path/to/skills/my-skill --context /path/to/project
harness-eval-lab eval-skill /path/to/skills/my-skill --context /path/to/project --rubric
```

**Note on `/eval-setup-security`:** The YARA signature scanning check requires `yara-python`. If not installed, the YARA check is skipped automatically and the report notes it. All other security checks run without extra dependencies. To enable YARA scanning:

```bash
pip install yara-python
```

## CLI Commands

| Command | Description | Needs LLM? |
|---------|-------------|------------|
| `eval-setup-lint` | 39 deterministic rules + system analysis (budget, triggers, deps, context utilization). | No |
| `eval-setup-review` | Per-component rubric review, 21 cross-type checks, KEEP/REVIEW/REMOVE verdicts. | Yes (API key) |
| `eval-setup-security` | All security rules + YARA + CVE lookups + optional LLM semantic review. | Optional (`--review`) |
| `eval-skill` | Deep-evaluate a single skill individually and in context of the setup. | Optional (`--rubric`) |

## Plugin Skills

| Skill | Description | Needs LLM? |
|-------|-------------|------------|
| `/eval-setup-lint` | 39 rules, system analysis. Fast, CI-suitable. | No |
| `/eval-setup-review` | Per-component rubrics, 21 cross-type checks, KEEP/REVIEW/REMOVE verdicts. | Yes (Claude in-session) |
| `/eval-setup-security` | Deterministic security scan + semantic security review with 4-check checklist. | Yes (Claude in-session) |
| `/eval-skill` | Deep-evaluate one skill against rubric + contextual analysis. | Yes (Claude in-session) |

## Inspection Rules (39)

| Category | Rules | What they check |
|----------|-------|-----------------|
| Structural | 1 | SKILL.md exists |
| Frontmatter | 3 | Description required/quality (POV, use-case, length), format valid |
| Content | 3 | Duplicate detection (TF-IDF), broken references, token budget |
| Security | 9 | Credential access, prompt injection (17 patterns), data exfiltration, obfuscation, reverse shells, AST behavioral analysis, taint tracking, MCP least-privilege, MCP tool poisoning |
| Security (opt-in) | 2 | YARA signature scanning, CVE lookups via OSV.dev (only in `eval-setup-security`) |
| Commands | 7 | Description, script exists, duplicates, credentials, injection, skill overlap, shadows built-in |
| CLAUDE.md | 3 | Exists, skill duplication, generic advice detection |
| Hooks | 1 | Structure validation, dangerous patterns |
| Agents | 9 | Description, skills exist, tool format, constraint matching, credentials, injection, exfiltration, obfuscation, reverse shells |

Four presets: `recommended` (default), `strict`, `security`, `pre-workflow`.

## Future Plans

The [`future-plans/`](future-plans/) directory contains planned improvements, each in its own subfolder. Each doc explores a problem, presents approaches with trade-offs, and describes how to build it.

Every plan doc has a **Status** at the top:

| Status | Meaning |
|--------|---------|
| `future` | Idea documented, not yet planned for implementation |
| `in design` | Actively being designed, approaches being evaluated |
| `in progress` | Implementation underway |
| `built` | Implemented and merged |

| Plan | What it addresses |
|------|-------------------|
| [adjusting-to-dynamic-workflows](future-plans/adjusting-to-dynamic-workflows/) | Adapting to Claude Code's dynamic workflows (pre-flight checks, workflow evaluation, quality gates) |
| [test-coverage](future-plans/test-coverage/) | Expanding tests to cover all rules with edge cases |
| [runner-abstraction](future-plans/runner-abstraction/) | Evaluating setups for other agent tools (Cursor, Copilot, Windsurf) |
| [impact-dimension](future-plans/impact-dimension/) | Measuring whether a setup actually helps the agent (A/B testing) |
| [scoring-calibration](future-plans/scoring-calibration/) | Validating review accuracy against human judgment |
| [setup-recommend](future-plans/setup-recommend/) | Recommending missing components based on project stack profiling |

## Contributing

See [`how-to-contribute.md`](how-to-contribute.md) for guidelines on adding rules, future plans, and submitting PRs.

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for release history and notable changes.
