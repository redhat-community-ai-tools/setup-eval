# Hooks Rubric

Check each hook for issues in 5 categories.

## Impact

For every issue flagged, state the runtime consequence. Not "this is a redundancy issue" but what will actually go wrong: wrong skill routing, wasted context tokens displacing useful content, contradictory instructions causing inconsistent behavior, broken commands producing errors, etc.

## Safety

Flag if:
- Contains dangerous patterns (rm -rf, force push, curl|bash, git reset --hard)
- Modifies state destructively without safeguards

## Reliability

Flag if:
- Referenced script or command doesn't exist
- Command is malformed or will fail silently
- Hook depends on tools or paths that may not exist in all environments

## Scope and appropriateness

Flag if:
- Hook is over-broad (runs on events it shouldn't)
- Behavior is advisory, not deterministic (should be in CLAUDE.md or a skill instead)
- Hook contains LLM-style logic or judgment calls; hooks must be deterministic shell commands, not AI reasoning

Hooks are for enforcement that MUST happen every time. Advisory behavior ("prefer X over Y", "consider doing Z") belongs in CLAUDE.md or skills.

PreToolUse vs PostToolUse appropriateness:
- PreToolUse hooks can block tool calls (exit code 2). Use for: secret scanning, forbidden file checks, policy enforcement that must prevent an action.
- PostToolUse hooks cannot block; they run after the action. Use for: auto-formatting, logging, notifications.
- Flag if a PostToolUse hook is trying to prevent something (it can't; that's a PreToolUse job).
- Flag if a PreToolUse hook is doing post-processing (formatting, cleanup) that should happen after the action.

## Performance

Flag if:
- Hook runs a heavy operation (full test suite, large linter scan, network calls) on every file edit
- Hook is slow or blocking when it could be async
- Hook does unnecessary work on every invocation (e.g., scanning all files when only one changed)

Test: "Does this hook need to run on every single tool call, or could it be scoped to specific events?" If it runs too broadly, flag it.

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (dangerous, broken, or misplaced logic)
