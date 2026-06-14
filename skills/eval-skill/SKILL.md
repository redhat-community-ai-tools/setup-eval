---
name: eval-skill
description: Deep-evaluate a single skill with static analysis and qualitative issue detection, both individually and in context of the full setup. Use when the user wants to check if a specific skill is worth keeping, well-built, or redundant.
allowed-tools:
  - Bash
  - Read
---

# Evaluate Skill

Deep-evaluate a single skill using two layers: static analysis (Layer 1) and qualitative issue detection (Layer 2), both individually and in context of the full setup.

## Hard Rules

1. **Never give a verdict without running the checks.** Read the actual file content and check all rubric categories before assigning a verdict.
2. **Every category must be checked.** Both the individual rubric AND the contextual analysis must be fully evaluated.
3. **Read before you judge.** Read the actual SKILL.md content (and reference files if they exist).
4. **Don't manufacture problems.** If the skill is good, say so. Only report real issues.
5. **Always end with a short summary.**

## Step 1: Ask Output Preference

Before doing anything else, ask the user:

> Where should i present the results?
> 1. **Terminal** - print the report here in the conversation
> 2. **File** - write a markdown report to a file (you'll choose the path)

Wait for their answer before proceeding.

## Step 2: Select the Skill

Determine the skill path. If the user says a skill name, find it under `skills/<name>/SKILL.md`.

## Step 3: Run Layer 1 (Static Analysis)

Determine the setup context path (usually the current working directory).

```bash
uv run python skills/eval-skill/scripts/run_skill_eval.py <skill-path> <context-path> recommended
```

If no context path, pass `-` as the second argument.

Read the JSON output. It contains diagnostics, token count, and contextual findings from Layer 1.

## Step 4: Read Actual Files (Layer 2 Preparation)

Read the skill's actual content:
1. The SKILL.md file
2. All files in the skill's subdirectories (reference files). Check the COMBINED content.
3. The skill's guidelines.md (if it exists)

Also read for context (don't check these, they're context for evaluating the target skill):
4. All OTHER skill SKILL.md files in the workspace
5. CLAUDE.md
6. Hooks in .claude/settings.json

## Step 5: Individual Rubric (Layer 2)

Read `rubric/skills-rubric.md` for the issue categories and what to flag.

Check the skill against all 5 categories. For each issue found, cite specific evidence from the content.

Verdict: **KEEP** (no issues or minor only), **REVIEW** (multiple issues), **REMOVE** (fundamentally broken/redundant)

## Step 6: Contextual Analysis (Layer 2)

Read `rubric/contextual-analysis.md` and evaluate all 5 contextual dimensions.

Check redundancy against three sources:
- Claude's default behavior (generic advice = redundant)
- Other skills in the workspace (overlap = partially redundant)
- CLAUDE.md content (duplication = wasted tokens)

## Step 7: Produce the Report

Read `report-format.md` for the full report structure.

The report must include:
- Layer 1 results (rule checklist with PASS/FAIL)
- Layer 2 individual issues (by category)
- Layer 2 contextual analysis
- +/!/x sections (good, improve, broken)
- Final verdict with suggestions

At the very end of the report, include a timing line:

```
Completed in [duration] seconds.
```

Where [duration] is the wall-clock time from when you started Step 3 to when you finished formatting.

**If the user chose terminal:** print the report in the conversation.

**If the user chose file:** write the report as markdown to the path they specified (or suggest `eval-skill-report.md` in the current directory). Tell them the file path when done.
