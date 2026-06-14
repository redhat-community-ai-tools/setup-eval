---
description: "Run deterministic static analysis on the full agent setup (CLAUDE.md, skills, commands, hooks, agents, MCP configs). 39 rules + system-level analysis. No LLM, fast, CI-suitable."
---

# Eval Setup Lint

Use the Skill tool to invoke `eval-setup-lint` explicitly.

Pass through any arguments from $ARGUMENTS (e.g., a specific path to evaluate).

If the Skill tool is not available or the skill is not found, tell the user:
- Check that `skills/eval-setup-lint/SKILL.md` exists in the workspace
- If not, reinstall the harness-eval-lab plugin
