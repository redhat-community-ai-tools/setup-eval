---
name: eval-skill
description: Deep-evaluate a single skill, both individually and in context of the full setup. Use when the user wants to check if a specific skill is worth keeping, well-built, or redundant.
allowed-tools:
  - Bash
  - Read
---

# Evaluate Skill

Deep-evaluate a single skill individually and in context of the user's full setup.

## What to do

1. Determine the skill path. If the user says a skill name, find it under `skills/<name>/SKILL.md`.

2. Determine the setup context path. This is usually the current working directory (the project root containing CLAUDE.md, skills/, commands/, etc.).

3. Run the evaluation script:
```bash
uv run python skills/eval-skill/scripts/run_skill_eval.py <skill-path> <context-path> recommended
```
If no context path, pass `-` as the second argument.

4. Read the JSON output. It contains:
   - `skill`: skill name
   - `tokens`: token count
   - `files`: files in the skill directory
   - `frontmatter`: parsed frontmatter metadata
   - `errors` / `warnings`: counts from static analysis
   - `findings`: specific issues found by 24 rules
   - `context_findings`: issues found by comparing to the rest of the setup

5. Present the results to the user:
   - Start with the skill identity: name, token count, description
   - Report static analysis findings (errors first)
   - Report contextual findings: overlap with other skills, CLAUDE.md duplication, trigger collisions
   - Give a clear verdict: is this skill worth keeping?
   - If there are issues, give specific, actionable suggestions

6. Read the actual SKILL.md content to give deeper qualitative feedback:
   - Is the content specific or vague?
   - Does the description help the agent know when to activate it?
   - Is the token cost justified by the value?
   - Are there things in this skill that should be in CLAUDE.md or a hook instead?

## Evaluation Criteria

**Individual quality:**
- Specificity: concrete patterns vs vague platitudes
- Trigger quality: clear "use when" phrasing in description
- Token efficiency: value per token consumed
- Structure: organized sections, examples, edge cases

**In-context quality:**
- Not redundant with other skills (TF-IDF > 0.60 = overlap)
- Not duplicating CLAUDE.md content (TF-IDF > 0.50 = overlap)
- No trigger collision with other skills (similar descriptions = load together)
- Correct type placement (should this be a hook or command instead?)

## Verdicts

- **KEEP**: well-built, unique, good triggers, justified token cost
- **REVIEW**: some issues but potentially valuable, needs changes
- **REMOVE**: redundant, vague, or restates default model behavior
