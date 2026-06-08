# CLAUDE.md Rubric

Check CLAUDE.md for issues in 5 categories. Report only real issues, citing specific evidence.

## Conciseness

Flag if:
- Any line could be removed without causing Claude to make mistakes
- Content is padded or repetitive

Test: "Would removing this cause Claude to make mistakes?" If not, flag it.

## Signal-to-noise

Flag if:
- Contains generic advice Claude already follows ("write clean code", "be helpful", "follow best practices", "think step by step")
- Contains standard language conventions (use linters instead)
- Contains detailed API docs (link instead of inline)
- Contains file-by-file descriptions that will rot as the codebase evolves

## Skill separation

Flag if:
- Contains domain-specific rules that only matter for specific tasks
- These waste context every session and should be on-demand skills instead

## Structure

Flag if:
- Sections are unclear or poorly organized
- Critical rules aren't marked or easy to find
- Document isn't scannable (no headers, no logical grouping)

## Conflict-free

Flag if:
- Any rule contradicts what a skill, command, or hook says
- Same instruction appears in both CLAUDE.md and a skill (double token cost)

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely generic or conflicting)
