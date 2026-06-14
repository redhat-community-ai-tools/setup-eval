---
description: "Deep security audit of the agent setup. Deterministic security rules (prompt injection, credential access, exfiltration, taint tracking, YARA, CVE) plus LLM semantic review."
---

# Eval Setup Security

Use the Skill tool to invoke `eval-setup-security` explicitly.

Pass through any arguments from $ARGUMENTS (e.g., a specific path to evaluate).

If the Skill tool is not available or the skill is not found, tell the user:
- Check that `skills/eval-setup-security/SKILL.md` exists in the workspace
- If not, re-run `python install.py --target <workspace>` from the harness-eval-lab repo
