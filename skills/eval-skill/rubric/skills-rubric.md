# Skills Rubric

Check each skill for issues in 6 categories. Report only real issues, citing specific evidence.

## What good looks like

A well-built skill:
- Has one clear job (e.g., "review Python test coverage" not "help with testing")
- SKILL.md is a thin routing + context document (under 500 lines)
- Detailed procedures, tables, and examples live in reference files that load on demand
- Description contains specific trigger phrases ("Use when...", "Run when...") with keywords that match real user requests
- Adds rules or context Claude does not already know

Example of a strong description (under 1024 chars):
```
Review test coverage gaps. Use when the user asks about test coverage,
missing tests, or untested code paths. Run when coverage reports show
drops. Analyzes source and test files to identify untested branches,
edge cases, and missing integration tests.
```

## Impact

For every issue flagged, state the runtime consequence. Not "this is a redundancy issue" but what will actually go wrong: wrong skill routing, wasted context tokens displacing useful content, contradictory instructions causing inconsistent behavior, broken commands producing errors, etc.

## Specificity

Flag if:
- Instructions use vague platitudes ("write clean code", "be thorough")
- Rules lack concrete patterns or examples
- No actionable instructions that would change Claude's behavior
- Rules are not verifiable ("format code properly" vs "use 2-space indentation in YAML files")

## Redundancy

Flag if:
- Instructions duplicate Claude's built-in knowledge
- The skill wraps a built-in capability without adding specific rules

Claude already knows these things (always redundant to document):
- Git, GitHub/GitLab workflows, commit conventions, branch strategies
- Package managers (npm, pip, cargo, gem, uv)
- Testing frameworks (pytest, jest, unittest, RSpec)
- Standard language features, idioms, debugging
- Docker, shell commands, CI/CD patterns
- Reading error messages, stack traces
- "Write clean, readable code", "be helpful", "follow best practices", "think step by step"

Test: "If i deleted this skill, would Claude behave differently?" If not, flag it.

Also check overlap with built-in capabilities: plan mode, code review, commit messages, code explanation. A skill that wraps a built-in without adding project-specific rules is redundant.

## Trigger quality

Flag if:
- Description is missing or over 1024 characters
- Description is too vague or broad to route correctly
- No activation context (missing "use when" or "run when" phrasing)
- Description lacks specific keywords that match how users actually phrase requests
- Uses coercive language with broad scope ("MUST use this", "ALWAYS use this before")
- Contains hard gates ("Do NOT proceed until") for broad workflows (acceptable for narrow safety concerns)
- Claims authority over entire categories ("any creative work", "all code changes")

Routing test: read the description and ask "would this trigger on the right requests and stay silent on unrelated ones?" If the answer is unclear, the description needs work.

Test: "Could a reasonable user want to skip this skill and go straight to coding?" If yes, the trigger shouldn't prevent that.

## Token efficiency and progressive disclosure

Flag if:
- SKILL.md exceeds 500 lines (Anthropic's recommended limit)
- SKILL.md is over ~800 tokens and contains detailed procedures, tables, or examples that should be in reference files
- SKILL.md duplicates content that exists in a reference file

Token budget applies to SKILL.md only (always-loaded cost). Reference files in subdirectories load on demand. The pattern is: SKILL.md provides routing, context, and high-level instructions; reference files provide details.

## Instruction clarity

Flag if:
- Contains contradictory instructions within the same SKILL.md (e.g., "always run tests" in one section, "skip tests if not needed" in another)
- Uses vague, non-actionable language: "follow best practices", "be thorough", "use common sense", "handle appropriately". These tell Claude nothing it doesn't already know.
- Uses hedging language for rules that should be deterministic: "consider doing X", "you might want to", "try to", "if possible" when a clear "do X" is needed
- Important instructions are buried deep in the file, below less important content. Critical rules should be early or clearly marked.
- Contains orphaned conditionals: "when the user asks about X, do Y" where X is not something the skill's trigger would match

## Content quality

Flag if:
- No structure (no headers, no logical flow)
- Broken file references
- Missing edge case handling for workflow-type skills
- Workflow steps require synthesizing more than 3 inputs at once (cognitive overload)
- Skills that execute commands or call APIs don't define failure behavior
- Skill name doesn't match directory name, or uses characters other than lowercase letters and hyphens

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely redundant, broken, or harmful)
