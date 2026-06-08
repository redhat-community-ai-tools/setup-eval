# Skills Rubric

Check each skill for issues in 5 categories. Report only real issues, citing specific evidence.

## Specificity

Flag if:
- Instructions use vague platitudes ("write clean code", "be thorough")
- Rules lack concrete patterns or examples
- No actionable instructions that would change Claude's behavior

## Redundancy

Flag if:
- Instructions duplicate Claude's default behavior
- The skill wraps a built-in capability without adding specific rules

Things Claude already does by default (always redundant):
- "Write clean, readable code"
- "Be helpful and thorough"
- "Handle errors properly" (too vague to add value)
- "Follow best practices"
- "Use proper formatting"
- "Think step by step"
- "Consider edge cases"

Test: "if i deleted this skill, would Claude behave differently?" If not, flag it.

Also check overlap with built-in capabilities: plan mode, code review, commit messages, code explanation. A skill that wraps a built-in without adding specific rules is redundant.

## Trigger quality

Flag if:
- No description, or description too vague/broad
- Uses coercive language with broad scope ("MUST use this", "ALWAYS use this before")
- Contains hard gates ("Do NOT proceed until") for broad workflows (acceptable for narrow safety concerns)
- Claims authority over entire categories ("any creative work", "all code changes")
- Lacks activation context (no "use when" phrasing)

Test: "Could a reasonable user want to skip this skill and go straight to coding?" If yes, the trigger shouldn't prevent that.

## Token efficiency

Flag if:
- SKILL.md is over 3,000 tokens with low value density
- SKILL.md is over ~800 tokens and contains detailed procedures/tables that should be split into reference files (progressive disclosure)

Token budget applies to SKILL.md only (always-loaded cost). Reference files in subdirectories load on demand.

## Content quality

Flag if:
- No structure (no headers, no logical flow)
- Broken file references
- Missing edge case handling for workflow-type skills
- Workflow steps require synthesizing more than 3 inputs at once (cognitive overload)
- Skills that execute commands or call APIs don't define failure behavior

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely redundant, broken, or harmful)
