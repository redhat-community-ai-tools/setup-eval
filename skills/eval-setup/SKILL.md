---
name: eval-setup
description: Evaluate the full agent setup (CLAUDE.md, skills, commands, hooks, agents, MCP configs) with static analysis and qualitative issue detection. Use when the user wants to check their setup health, find redundancy, detect issues, or get a quality report.
allowed-tools:
  - Bash
  - Read
---

# Evaluate Setup

Evaluate the user's full agent setup using two layers: static analysis (Layer 1, deterministic) and qualitative issue detection (Layer 2, Claude reads every file).

## Hard Rules

1. **Never give a verdict without reading the files.** Layer 1 counts are input data, not the verdict. A component with warnings can still be healthy.
2. **Read before you judge.** Read every file's actual content before assessing.
3. **Don't manufacture problems.** If the setup is good, say so.
4. **Always end with the evidence-based summary.**

## Step 1: Run Layer 1 (Static Analysis)

Determine the setup path. If the user doesn't specify one, use the current working directory.

```bash
uv run python skills/eval-setup/scripts/run_assessment.py <setup-path> recommended
```

Read the JSON output. This gives you per-component diagnostics, token budget, trigger overlaps, and dependency findings.

## Step 2: Read Actual Files (Layer 2)

Read the actual content of every component: SKILL.md files (including reference files in subdirectories), command files, agent files, CLAUDE.md, and settings.json for hooks.

## Step 3: Analyze Each Component

For each component, provide:
- Layer 1 results (which rules passed/failed)
- A 2-3 sentence qualitative assessment (what it does, whether it adds value, whether it's well-built)
- Issues found, citing specific content
- Per-component verdict: KEEP, REVIEW, or REMOVE

Use the per-component rubric files for detailed criteria:
- Skills: read `rubric/skills-rubric.md`
- CLAUDE.md: read `rubric/claude-md-rubric.md`
- Commands: read `rubric/commands-rubric.md`
- Agents: read `rubric/agents-rubric.md`
- Hooks: read `rubric/hooks-rubric.md`

## Step 4: Cross-Type Optimization

Read `rubric/cross-type-checks.md` and answer all 21 checks with YES/NO and a one-line explanation. These check whether components should be transformed (skill to hook?), merged, or removed.

## Step 5: Summarize by Area

Based on everything from Steps 1-4, summarize findings in 5 areas. Do not assign numeric scores. Count issues and cite specifics.

**Structure:** Count Layer 1 structural/frontmatter errors. List by name. "N errors (list)" or "Clean. No issues found."

**Security:** Count Layer 1 security findings + Layer 2 concerns. List by name. "N issues (list)" or "Clean. No issues found."

**Coherence:** Count duplicates, conflicts, trigger overlaps, broken dependencies, cross-type issues. List specifics.

**Efficiency:** Report always-loaded vs on-demand token ratio and heaviest component with token counts.

**Redundancy:** Count components containing content Claude already knows by default. List which ones and why.

## Step 6: Produce the Report

Read `report-format.md` for the full report structure. The report must include:
1. The setup health summary (the headline)
2. Inventory table
3. Token budget breakdown
4. Per-component analysis (Layer 1 + Layer 2)
5. Cross-type optimization (21 checks)
6. Numbered suggestions
7. Terminal summary
