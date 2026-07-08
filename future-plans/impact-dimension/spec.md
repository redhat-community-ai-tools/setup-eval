# Measuring Impact: Does the Setup Actually Help?

**Status:** future
**Created:** 2026-06-10

## Problem

The tool can tell you a setup is well-structured, secure, and efficient. But none of that answers the most important question: does it make the agent better at its job?

A setup can pass every rule, have perfect token distribution, and zero security issues, while every skill contains generic advice Claude already follows by default. The setup looks great on paper but does nothing. We need a way to measure whether the setup changes the agent's behavior for the better.

This is the hardest problem in the project and the most valuable to solve. Lint checks structure and syntax. Review gets closer with qualitative evaluation. But the only way to know for sure is to test it empirically.

## Proposal

Use A/B probe tasks as the primary approach, with activation rate as a cheap pre-screen.

**A/B probe tasks (primary):** Run the agent on the same task twice, once with the setup loaded and once without. Compare the outputs using a judge. Start simple: 3 tasks, 1 judge call per task, simple win/loss/tie verdict.

**Skill activation rate (pre-screen):** For each skill, generate a prompt that should activate it and check if it does. Skills that never activate have zero impact regardless of content quality. Use this to skip expensive A/B tests on dead skills.

**Differential analysis (complement):** Remove one component at a time and observe the effect on lint + review scores. Good for identifying truly dead components but insufficient alone.

**Where it lives:** `src/setup_eval/experiment/` (new package)

**What to build:**
1. A `ProbeTask` dataclass: task description, target repo path, expected skill activation
2. A set of 3 default probe tasks (review, write, debug) that work on any repo
3. A `run_probe` function that spawns two subagents and a judge
4. A `compute_impact` function that aggregates probe results into a 1-5 score
5. Integration with `eval-setup` plugin via an `--with-impact` flag or a separate step in the SKILL.md protocol

## User stories

**Story 1: Impact measurement on a full setup**
- **Given** a user has a complete Claude Code setup with CLAUDE.md, skills, and commands
- **When** they run impact measurement
- **Then** the tool reports a 1-5 impact score with per-probe breakdowns showing whether the setup actually improves agent behavior
- **Acceptance criteria:** Score is based on blind judging across 3 probe tasks; judge doesn't know which response had the setup.

**Story 2: Dead skill detection via activation rate**
- **Given** a user has skills that may never get triggered
- **When** they run activation rate analysis
- **Then** the tool reports which skills activate on matching prompts and which don't
- **Acceptance criteria:** Skills with 0% activation are flagged; expensive A/B tests are skipped for these.

**Story 3: Component-level impact isolation**
- **Given** a user wants to know which specific component contributes the most value
- **When** they run differential analysis
- **Then** the tool shows the impact of removing each component individually
- **Acceptance criteria:** Components whose removal changes nothing are flagged as candidates for removal.

## Requirements

1. A/B probes must use blind judging (judge doesn't know which response had the setup).
2. Probe tasks must be portable across different projects or customizable per project.
3. Dimension-based scoring (accuracy, specificity, actionability, completeness, response quality), not "which is better overall."
4. Activation rate check must run before A/B probes to skip dead skills.
5. Impact measurement must live in `src/setup_eval/experiment/`.
6. Integration with the plugin must be opt-in (flag or separate step), not default.
7. Default probe tasks must work on any repo without customization.

## Success criteria

- Impact scores correlate with human judgment of setup quality on a test set of 5+ setups.
- Activation rate correctly identifies skills that never trigger on matching prompts.
- Total cost per evaluation stays under 9 LLM calls for the standard 3-probe run.
- Scores are stable enough that repeated runs on the same setup produce rankings within 1 point.

## Open questions

- Should probe tasks be generic (work on any project) or customizable per project?
- How many probe runs are needed to get a stable signal? (Non-determinism means one run might not be enough)
- What's an acceptable cost per evaluation? (3 probes x 3 LLM calls = 9 calls minimum)
- Should the judge be the same model as the agents, or a different one?
- How to handle projects with no test repo available?
