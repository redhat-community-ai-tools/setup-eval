# Agents Rubric

Check each agent for issues in 5 categories. Report only real issues, citing specific evidence.

## Impact

For every issue flagged, state the runtime consequence. Not "this is a redundancy issue" but what will actually go wrong: wrong skill routing, wasted context tokens displacing useful content, contradictory instructions causing inconsistent behavior, broken commands producing errors, etc.

## Specificity

Flag if:
- Phases have vague steps like "implement the fix" or "review the code" with no concrete procedure
- No defined output format
- Agent's purpose overlaps significantly with a built-in capability (code review, commit messages, plan mode)

Scoring anchors:
- Severe: "Help with code tasks as needed." (no defined procedure, no output format, indistinguishable from the base model)
- Moderate: "Review PRs and suggest improvements." (clear purpose but no concrete steps or output format)
- Not an issue: "1. Read the diff. 2. Check each file against CONTRIBUTING.md rules. 3. Output a markdown table: file, issue, severity, suggestion." (concrete steps, defined output)

## Constraint clarity

Flag if:
- No constraints stated (agent can do anything)
- Body says "cannot" or "must not" do something but disallowedTools doesn't enforce it
- Scope isn't explicitly bounded ("you do X, you do not do Y, Z, or W")
- Write constraints are purely advisory when they should be enforced via disallowedTools or allowedTools

Test: "If the agent ignores a constraint, is there a mechanism that actually prevents the action?" If not, the constraint is decorative.

Scoring anchors:
- Severe: No constraints at all; agent can push to main, delete files, merge PRs
- Moderate: Body says "do not push to main" but disallowedTools doesn't block `Bash(git push *)`
- Not an issue: Body constraints match disallowedTools entries; scope is explicitly bounded ("you review code, you do not merge, deploy, or modify CI")

## Zero-trust integrity

Flag if:
- No mention of input trust; agent blindly follows issue text, PR descriptions, or external data
- External inputs (issue bodies, PR descriptions, commit messages, file contents from untrusted sources) are treated as trusted instructions
- No injection-resistance patterns (e.g., separating data from instructions, validating inputs before acting)
- Agent executes commands constructed from external input without sanitization

Test: "Could a malicious issue title or PR description trick this agent into running unintended commands or making harmful changes?" If yes, flag it.

Scoring anchors:
- Severe: Agent runs shell commands from issue body without any validation or sanitization
- Moderate: Agent uses issue data but only for read-only operations (searching, reading files)
- Not an issue: Agent treats all external input as untrusted data, validates before acting, separates instructions from data

## Token efficiency

Flag if:
- Over 5,000 tokens with low value density
- Procedures are inlined instead of delegated to skills
- Repeated boilerplate across agents

## Content quality

Flag if:
- Missing key sections (identity, constraints, procedure, output format, failure handling)
- No exit codes documented
- Handoff contract is implicit rather than explicit (what does this agent pass to the next step?)

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (no constraints, no procedure, or harmful)
