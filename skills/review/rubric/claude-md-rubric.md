# CLAUDE.md Rubric

Check CLAUDE.md for issues in 6 categories. Report only real issues, citing specific evidence.

## Impact

For every issue flagged, state the runtime consequence. Not "this is a redundancy issue" but what will actually go wrong: wrong skill routing, wasted context tokens displacing useful content, contradictory instructions causing inconsistent behavior, broken commands producing errors, etc.

## Size and density

Flag if:
- File exceeds 200 lines (Anthropic's recommended limit per file)
- Content is padded or repetitive
- Any line could be removed without causing Claude to make mistakes

Test: "Would removing this line cause Claude to make a mistake it wouldn't otherwise make?" If not, flag it.

For large projects, use multiple focused CLAUDE.md files in subdirectories rather than one oversized root file.

## Signal-to-noise

Flag if:
- Contains generic advice Claude already follows ("write clean code", "be helpful", "follow best practices", "think step by step")
- Documents things Claude already knows: git workflows, package managers, testing frameworks, standard language features, Docker, CI/CD patterns, debugging
- Contains standard language conventions that linters enforce
- Contains detailed API docs (link instead of inline)
- Contains file-by-file descriptions that will rot as the codebase evolves
- Rules are not specific and verifiable

Specificity test examples:
- Bad: "Format code properly" (vague, unverifiable)
- Good: "Use 2-space indentation in all YAML files"
- Bad: "Handle errors gracefully" (Claude already does this)
- Good: "All API handlers must return ErrorResponse with error_code from errors.py"
- Bad: "Write good tests" (vague platitude)
- Good: "Tests use factory_boy fixtures, never raw model constructors"

## Procedures belong in skills

Flag if:
- Contains multi-step procedures (deployment steps, review checklists, migration guides)
- Contains domain-specific rules that only matter for certain tasks (e.g., "when writing API endpoints..." or "for database migrations...")
- These waste context every session; move them to on-demand skills instead

Test: "Does this rule matter in every single conversation, or only when doing a specific task?" If task-specific, it belongs in a skill.

CLAUDE.md should contain only facts Claude needs every session: project identity, build/test commands, universal conventions, and pointers to where detailed procedures live.

## Structure

Flag if:
- Sections are unclear or poorly organized
- Critical rules aren't marked or easy to find
- Document isn't scannable (no headers, no logical grouping)

## Instruction clarity

Flag if:
- Contains contradictory instructions: "always use tabs" in one section and "use spaces for indentation" in another. Look for pairs where one rule negates or conflicts with another rule in the same file.
- Uses non-deterministic language for rules that should be deterministic: "consider", "maybe", "sometimes", "if possible", "try to" in contexts where a clear rule is needed. (These are fine in suggestions, but not in rules.)
- Critical instructions are buried in the middle of a long file. Important rules should be near the top or clearly marked, not hidden in paragraph 47.
- Contains conditional instructions ("when X, do Y") where the condition X is never defined or referenced elsewhere in the setup.

## Conflict-free

Flag if:
- Any rule contradicts what a skill, command, or hook says
- Same instruction appears in both CLAUDE.md and a skill (double token cost)

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely generic or conflicting)
