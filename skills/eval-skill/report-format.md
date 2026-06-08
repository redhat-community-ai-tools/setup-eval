# Eval-Skill Report Format

```
# Skill Evaluation: <skill-name>

**Date:** [today]
**Tokens:** [SKILL.md tokens] (+[reference file tokens] in reference files)
**Reference files:** [list or "none"]

---

## Layer 1: Rules (Static Analysis)

  [For each rule, show PASS or FAIL with message]
  SKILL.md exists                          PASS
  Frontmatter has description              PASS
  Description has use-case context          FAIL - lacks "use when" phrasing
  Frontmatter format valid                 PASS
  Token budget                             PASS - [N] tokens
  No broken file references                PASS
  No near-duplicates                       PASS
  No prompt injection patterns             PASS
  No credential references                 PASS

---

## Layer 2: Issue Detection

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
```
