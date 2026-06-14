# Setup Recommendations: What's Missing for This Project?

**Status:** future
**Created:** 2026-06-14

## Problem

A setup can pass every lint rule and every review check, but still be incomplete for the project it serves. A FastAPI project with Docker and GitHub Actions gets zero value from a setup that only has generic Python skills. The tool currently evaluates what exists but never asks: "what should exist but doesn't?"

This is the gap between quality (is this skill well-built?) and coverage (does this setup cover what the project needs?).

## Proposal

A new command (`eval-setup-recommend`) that profiles the current project's stack, compares it against the setup's component inventory, and identifies gaps.

### How it works

**Step 1: Project discovery (deterministic, no LLM)**

Scan the filesystem from the current working directory for project indicators:
- Language markers: `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`
- Framework evidence: imports in source files, dependency names (fastapi, django, react, express)
- Infrastructure: `Dockerfile`, `docker-compose.yml`, `terraform/`, `k8s/`, `.github/workflows/`, `.gitlab-ci.yml`
- Data stores: connection strings, ORM configs (SQLAlchemy, Prisma, TypeORM)
- Testing: `pytest.ini`, `jest.config`, `vitest.config`, test directories
- AI tooling: `.mcp.json`, `.claude/`, `CLAUDE.md`, `skills/`, agent configs
- Project type classification: frontend, api-service, ml-project, ai-agent, fullstack, library, CLI tool

If multiple projects are found (e.g., a workspace with several repos or a monorepo), present the user with a list and ask which to evaluate.

Output: a structured "stack profile" JSON.

**Step 2: Gap analysis (LLM in plugin, or heuristic in CLI)**

Compare the stack profile against the setup's component inventory:
- What the project uses vs. what the setup has skills/commands/hooks for
- Common workflows for this stack that have no supporting component
- Framework-specific patterns that the CLAUDE.md doesn't mention

In the plugin context, Claude does the reasoning (the command.md prompt provides the stack profile and component list). In the CLI context, a heuristic matcher maps stack elements to expected component categories, or the LLM does it via API.

**Step 3: Recommendations**

Output a ranked list of gaps with explanations:
- "This is a FastAPI project but the setup has no API development skill"
- "Docker is used but no containerization commands exist"
- "GitHub Actions CI is configured but no CI/CD skill is present"
- "The project uses PostgreSQL but CLAUDE.md doesn't mention database conventions"

### User interaction (plugin)

The user types `/eval-setup-recommend`. The command:
1. Scans for projects/repos/code starting from cwd
2. If multiple found, asks the user which to evaluate
3. Profiles the selected project
4. Compares against the setup
5. Reports gaps and suggestions

No arguments needed. Works in any directory.

### User interaction (CLI)

```bash
harness-eval-lab eval-setup-recommend /path/to/project
harness-eval-lab eval-setup-recommend /path/to/project --setup /path/to/setup
```

Default: setup is discovered from the project directory itself. The `--setup` flag allows evaluating a separate setup against a project.

## Where it lives

- `src/harness_eval_lab/profiling/` (new package): stack profiler, gap matcher
- `src/harness_eval_lab/profiling/scanner.py`: project discovery and stack profile generation
- `src/harness_eval_lab/profiling/gaps.py`: stack-to-setup gap analysis
- `skills/eval-setup-recommend/`: plugin skill with SKILL.md and script
- CLI command in `cli.py`

## User stories

**Story 1: Single project recommendation**
- **Given** a user has a Python FastAPI project with a Claude Code setup
- **When** they run `/eval-setup-recommend`
- **Then** the tool profiles the project, identifies that no API-related skill exists, and suggests adding one
- **Acceptance criteria:** Recommendations are specific to the detected stack, not generic.

**Story 2: Multi-project discovery**
- **Given** a user works in a workspace with 5 repos cloned in various directories
- **When** they run `/eval-setup-recommend`
- **Then** the tool discovers all 5 projects, asks which to evaluate, and runs the analysis on the selected one(s)
- **Acceptance criteria:** Discovery finds projects by walking the filesystem for markers, not by expecting a specific directory layout.

**Story 3: Monorepo support**
- **Given** a user has a monorepo with frontend (React), backend (FastAPI), and infra (Terraform)
- **When** they run the command
- **Then** the tool detects all three sub-projects and evaluates setup coverage for each
- **Acceptance criteria:** Each sub-project's gaps are reported separately.

## Requirements

1. Project discovery must be generic (no hardcoded directory names like `repositories/`).
2. Stack profiling must be deterministic and fast (no LLM, no network).
3. Gap analysis in the plugin uses Claude directly (no API key needed).
4. Gap analysis in the CLI uses heuristic matching by default, LLM via `--provider` flag.
5. Recommendations must be actionable ("add a skill for X") not vague ("consider improving coverage").
6. Multi-project discovery must present a selection UI, not auto-evaluate everything.

## Open questions

- How deep should framework detection go? (e.g., detecting FastAPI vs just "Python web framework")
- Should recommendations link to specific skill templates or examples?
- How to handle projects with unusual or custom stacks that don't map to known categories?
- Should the tool suggest specific skill content or just identify the gap?
- How to avoid recommending skills for every detected technology (noise vs signal)?
