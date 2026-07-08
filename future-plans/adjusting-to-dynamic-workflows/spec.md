# Adjusting to Dynamic Workflows

**Status:** future
**Created:** 2026-06-10

## Problem

Claude Code introduced dynamic workflows: the agent writes and runs its own multi-agent orchestration code at runtime. Instead of a fixed setup with static skills, Claude generates a JavaScript workflow that spawns subagents, routes them to different models, and coordinates their outputs using patterns like fan-out, adversarial verification, and tournaments.

This changes the role of the static setup (CLAUDE.md, skills, hooks, commands). It doesn't replace it; it builds on top of it. Every subagent spawned by a workflow still operates within the environment defined by the static setup. The skills it references, the rules in CLAUDE.md, the hooks that gate execution. If the foundation is broken, the workflow multiplies those problems across every subagent.

Harness evaluation becomes more important in the dynamic workflow era, not less.

## Proposal

Four directions for adapting setup-eval, ranging from near-term to ambitious. Each is explored in a dedicated file in this directory:

| Direction | File | Complexity | Value |
|-----------|------|-----------|-------|
| Pre-flight check | [preflight-check.md](preflight-check.md) | Low | High |
| Skills quality gate | [skills-quality-gate.md](skills-quality-gate.md) | Low | High |
| Evaluating generated workflows | [evaluate-generated-workflows.md](evaluate-generated-workflows.md) | High | Medium |
| Impact measurement via workflows | [impact-via-workflows.md](impact-via-workflows.md) | High | High |

**Recommended order:** Start with the two low-complexity, high-value items (pre-flight and quality gate). They use existing infrastructure. Then tackle impact measurement, which connects to [../impact-dimension/](../impact-dimension/). Workflow evaluation is the most speculative and can wait.

## User stories

**Story 1: Pre-flight validation before workflow execution**
- **Given** a user is about to run a dynamic workflow that depends on skills and CLAUDE.md
- **When** they invoke a pre-flight check
- **Then** the tool validates the static setup foundation and reports any issues that would propagate to subagents
- **Acceptance criteria:** All 26 rules pass on referenced components before workflow starts; broken references are caught before runtime.

**Story 2: Quality gate for skills used in workflows**
- **Given** a workflow references specific skills by name
- **When** the quality gate runs
- **Then** each referenced skill is evaluated for completeness, specificity, and correctness before the workflow proceeds
- **Acceptance criteria:** Skills that fail quality thresholds are flagged with actionable fix suggestions.

**Story 3: Workflow-aware impact measurement**
- **Given** a user wants to know whether their setup actually helps subagents perform better
- **When** they run impact measurement through a dynamic workflow
- **Then** the tool spawns A/B probe tasks and judges the difference between "with setup" and "without setup"
- **Acceptance criteria:** Impact score is reported on a 1-5 scale with per-probe breakdowns.

## Requirements

1. Discover when a dynamic workflow is about to run (hook, API, or file watcher).
2. Pre-flight check must reuse existing lint rules without duplication.
3. Skills quality gate must validate individual skills against the existing rubric.
4. Workflow evaluation (if built) must handle non-deterministic outputs gracefully.
5. Impact measurement must integrate with the impact-dimension plan.
6. Cost controls must be available: "light" vs "full" evaluation modes.

## Success criteria

- Pre-flight check catches broken references and critical rule violations before a workflow runs.
- Skills quality gate reduces the rate of "skill loaded but unhelpful" outcomes.
- Impact measurement produces stable, reproducible scores across repeated runs.
- No more than 10% overhead in token cost for "light" mode evaluations.

## Open questions

- How does setup-eval discover that a dynamic workflow is about to run? (Hook? API? File watcher?)
- Should the tool evaluate workflows at design time (before they run) or runtime (as they execute)?
- How to handle the cost question? Workflows already use significant tokens. Adding evaluation on top increases cost. Should there be a "light" vs "full" mode?
