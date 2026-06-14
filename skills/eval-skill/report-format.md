# Eval-Skill Report Format

```
# Skill Evaluation: <skill-name>

**Date:** [today]
**Tokens:** [SKILL.md tokens] (+[reference file tokens] in reference files)
**Reference files:** [list or "none"]

---

## Lint Results (Static Analysis)

  [For each rule, show PASS or FAIL with WHY it failed]
  PASS  SKILL.md exists
  PASS  Frontmatter has description
  FAIL  Description has use-case context — lacks "use when" phrasing, Claude won't know when to activate
  PASS  Frontmatter format valid
  PASS  Token budget — [N] tokens
  FAIL  Broken file references — 3 referenced files don't exist (scripts/foo.sh, etc.)
  PASS  No near-duplicates
  PASS  No prompt injection patterns
  PASS  No credential references

---

## Qualitative Review

### Individual Assessment                        [VERDICT]

  Issues found:
    [category] [description] -> [suggestion]
    [category] [description] -> [suggestion]
  Or: No issues found.

### Contextual Analysis

  Overlap with other skills:   [NONE/MINOR/SIGNIFICANT] - [findings]
  Conflict with CLAUDE.md:     [NONE/MINOR/SIGNIFICANT] - [findings]
  Conflict with other skills:  [NONE/MINOR/SIGNIFICANT] - [findings]
  Type appropriateness:        [CORRECT/WRONG TYPE] - [assessment]
  Structure optimization:      [OPTIMAL/COULD IMPROVE] - [findings]

  + What's good
  ! What could improve
  x What's broken

---

## Final Verdict

**[KEEP / REVIEW / REMOVE]** - [one-sentence summary]

Suggestions:
  1. [suggestion]
  2. [suggestion]

Duration: [X minutes Y seconds]
```
