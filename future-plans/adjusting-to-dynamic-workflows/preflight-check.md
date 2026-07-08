# Pre-flight Check for Dynamic Workflows

> **Status:** built

## The problem

A dynamic workflow that spawns 16 subagents, each loading a broken setup, multiplies every problem by 16. One missing skill reference becomes 16 "skill not found" errors. One bloated CLAUDE.md wastes tokens across every subagent's context window. Currently there's no checkpoint between "user triggers workflow" and "16 agents start burning tokens."

## The concept

Run `setup-eval scan` automatically before any workflow starts. Like a pilot's pre-flight checklist: check the instruments before takeoff, not after you're in the air.

## Approaches explored

### Approach 1: Claude Code hook

A `PreToolUse` hook in `settings.json` that fires before Workflow tool calls. The hook runs `setup-eval scan . --preset security --format json` and blocks if errors are found.

**Trade-offs:**
- Uses existing infrastructure (hooks, scan command)
- Adds latency before every workflow (scan takes 1-3 seconds)
- User has no choice: it blocks or it doesn't
- Can't distinguish between "quick workflow" and "expensive 16-agent workflow"

### Approach 2: Workflow preamble

Instead of a hook, the workflow script itself calls scan as its first step. The workflow reads the results and decides whether to proceed.

**Trade-offs:**
- Per-workflow control (some workflows skip the check, others require it)
- The scan becomes part of the workflow's token budget
- More flexible (can check specific things relevant to this workflow)
- Requires workflow authors to include the check (not automatic)

### Approach 3: Dedicated preset

Create a `pre-workflow` preset that only runs the rules most relevant to workflow safety: broken references, missing skills, security issues, credential access. Skip rules that don't matter for workflows (like description quality or token budget).

**Trade-offs:**
- Faster than running all 26 rules
- Focused on what actually breaks workflows
- Needs research into which rules matter most for workflow execution

## Recommended direction

**Approach 1 (hook) + Approach 3 (dedicated preset).**

The hook makes it automatic. The dedicated preset keeps it fast. Together: a hook runs `setup-eval scan . --preset pre-workflow` before workflows, takes under 1 second, and warns (not blocks) on errors.

## How to build it

1. **Define the `pre-workflow` preset** in `src/setup_eval/config/presets.py`. Include only: `structural/skill-md-exists`, `content/broken-references`, `agent/referenced-skills-exist`, `security/no-credential-access`, `security/no-prompt-injection`, `hooks/valid-structure`. Disable everything else.

2. **Add a `--fail-on-error` flag** to the `scan` command. Exit code 1 if any errors found, 0 if only warnings. This lets hooks decide whether to block.

3. **Write a hook configuration example** in the README showing how to wire it up:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Workflow",
      "command": "setup-eval scan . --preset pre-workflow --fail-on-error"
    }]
  }
}
```

4. **Test** that the preset runs in under 1 second on a typical setup (20-50 components).

## Open questions

- Should the pre-flight warn or block? (Warn is friendlier, block is safer)
- Should the user be able to bypass it? ("proceed anyway")
- What's an acceptable latency overhead? (Under 1 second seems right)
- Should the pre-flight check also validate the workflow script itself? (See [evaluate-generated-workflows.md](evaluate-generated-workflows.md))
