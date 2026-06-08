# Report Format

## Structure

```
## How This Evaluation Works

This report evaluates the Claude Code setup across 5 areas:

- **Structure** - Do all components parse correctly? Are required fields present? Do references resolve?
- **Security** - Any credential exposure, injection risk, or dangerous hooks?
- **Coherence** - Do components work together? Any duplicates, conflicts, or broken dependencies?
- **Efficiency** - Is the token budget well-distributed? Always-loaded vs on-demand?
- **Redundancy** - Does each component teach Claude something it doesn't already know?

Two layers produce the evidence:

**Layer 1 (Static Analysis)** runs 26 deterministic rules. No AI involved.
**Layer 2 (Qualitative Analysis)** Claude reads every file and checks for issues
that deterministic rules can't catch.

---

## Setup Health Summary

Structure:   [N] errors ([specifics]) / Clean. No issues found.
Security:    [N] issues ([specifics]) / Clean. No issues found.
Coherence:   [N] overlaps/conflicts ([specifics]) / Clean.
Efficiency:  [N]% always-loaded. Heaviest: [name] at [N] tokens.
Redundancy:  [N] components with default-behavior content ([which]).

---

## Inventory

| Type | Count | Total Tokens | Errors | Warnings |
|------|-------|-------------|--------|----------|
| Skills | [N] | [N] | [N] | [N] |
| Commands | [N] | [N] | [N] | [N] |
| CLAUDE.md | [N] | [N] | [N] | [N] |
| Hooks | [N] | [N] | [N] | [N] |
| Agents | [N or 0] | [N] | [N] | [N] |

## Token Budget

  Always-loaded (CLAUDE.md, hooks): [N] tokens ([pct]%)
  On-demand (skills, commands, agents): [N] tokens ([pct]%)

  By type:
    [type]    [tokens] tokens ([pct]%)

---

## Per-Component Analysis

For each component, provide:

### component-name                              [KEEP/REVIEW/REMOVE]
  Tokens: [N]
  Type: [skill/command/agent/claude_md/hooks]

  Layer 1: [pass/fail checklist for relevant rules]

  Layer 2 Assessment:
    [2-3 sentences: what this component does, whether it adds value,
    whether it's well-built. Reference specific content.]

  Issues found:
    [category] [description] -> [suggestion]
  Or: No issues found.

For clean components with no issues, use a compact one-line format:
### component-name                              KEEP
  Tokens: [N] | Layer 1: all pass | [one-line assessment]

---

## Cross-Type Optimization

[All 21 checks from cross-type-checks.md, answered YES/NO with one-line explanation]

---

## Suggestions

[Numbered actionable items. Each is one line. Only recommend changes
that make a real difference.]
```

## Terminal Summary

Always print this at the end:

```
## Evaluation Summary

[one-sentence overall assessment]

Structure:   [summary]
Security:    [summary]
Coherence:   [summary]
Efficiency:  [summary]
Redundancy:  [summary]

Reviewed [N] skills, [M] commands, CLAUDE.md, [H] hooks, [A] agents.
Total: [tokens] tokens.
Cross-type: [count]/21 checks flagged.

Suggestions:
  1. [one-line]
  2. [one-line]
  3. [one-line]
```
