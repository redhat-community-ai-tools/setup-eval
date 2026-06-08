# Hooks Rubric

Check each hook for issues in 4 categories.

## Safety

Flag if:
- Contains dangerous patterns (rm -rf, force push, curl|bash, git reset --hard)
- Modifies state destructively without safeguards

## Reliability

Flag if:
- Referenced script or command doesn't exist
- Command is malformed or will fail silently

## Scope

Flag if:
- Hook is over-broad (runs on events it shouldn't)
- Behavior is advisory, not deterministic (should be in CLAUDE.md or a skill instead)
- Hooks are for things that MUST happen every time; advisory behavior doesn't belong here

## Performance

Flag if:
- Hook is slow or blocking when it could be async
- Hook does unnecessary work on every invocation
