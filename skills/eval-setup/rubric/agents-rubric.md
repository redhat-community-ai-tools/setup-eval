# Agents Rubric

Check each agent for issues in 5 categories. Report only real issues, citing specific evidence.

## Specificity

Flag if:
- Phases have vague steps like "implement the fix" or "review the code" with no concrete procedure
- No defined output format

## Constraint clarity

Flag if:
- No constraints stated (agent can do anything)
- Body says "cannot" or "must not" do something but disallowedTools doesn't enforce it
- Scope isn't explicitly bounded ("you do X, you do not do Y, Z, or W")

## Zero-trust integrity

Flag if:
- No mention of input trust; agent blindly follows issue text or PR descriptions
- External inputs are treated as trusted without verification steps
- No injection-resistance patterns

## Token efficiency

Flag if:
- Over 5,000 tokens with low value density
- Procedures are inlined instead of delegated to skills
- Repeated boilerplate across agents

## Content quality

Flag if:
- Missing key sections (identity, constraints, procedure, output format, failure handling)
- No exit codes documented
- Handoff contract is implicit rather than explicit

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (no constraints, no procedure, or harmful)
