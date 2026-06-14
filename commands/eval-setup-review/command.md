---
description: "Full qualitative review of the agent setup. Per-component rubrics, 21 cross-type checks, KEEP/REVIEW/REMOVE verdicts. Use for deep review, redundancy check, or quality assessment."
---

# Eval Setup Review

Use the Skill tool to invoke `eval-setup-review` explicitly.

Pass through any arguments from $ARGUMENTS (e.g., a specific path to evaluate).

If the Skill tool is not available or the skill is not found, tell the user:
- Check that `skills/eval-setup-review/SKILL.md` exists in the workspace
- If not, re-run `python install.py --target <workspace>` from the harness-eval-lab repo
