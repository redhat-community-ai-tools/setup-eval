# Security Audit Report Format

## Header

```
# Security Audit: [setup name]
```

## Summary

| Metric | Value |
|--------|-------|
| Components scanned | N |
| Deterministic rules run | N (from `rules_checked` in JSON) |
| Semantic checks per component | 4 |
| Checks skipped | N |
| Errors | N |
| Warnings | N |
| Semantic issues | N |
| **Risk Assessment** | **SAFE / CAUTION / UNSAFE** |

Risk levels:
- **SAFE**: No errors, no warnings, no semantic issues
- **CAUTION**: Warnings present but no errors
- **UNSAFE**: One or more errors found

## What Was Checked

### Deterministic Rules

Build this table from the `rules_checked` field in the JSON output. Show every rule, its description, and a PASS/FAIL result.

| Rule | What it checks | Result |
|------|---------------|--------|
| no-prompt-injection | [description from JSON] | PASS / N errors |
| no-credential-access | [description from JSON] | PASS / N errors |
| ... | ... | ... |

If a rule was skipped (YARA, CVE), show it as "SKIPPED" with the reason.

### Semantic Checks (4 per component)

These are LLM-based checks that catch patterns regex and AST analysis cannot:

| Check | What it verifies |
|-------|-----------------|
| Anti-jailbreak | Text that attempts to manipulate evaluators or downstream agents ("this is verified safe", "ignore security warnings", "pre-approved") |
| Semantic attacks | Polite reframings of jailbreaks, creative synonyms that bypass regex, natural-language exfiltration instructions, gradual deception |
| Description-behavior match | Whether the code actually does what the description claims (a "code formatter" that makes network requests, a "linter" that reads credentials) |
| Permission scope | Whether declared permissions are proportionate to the task (Bash access for a read-only skill, Write for an analysis tool) |

## Deterministic Findings

Group by component. For each component with findings:

```
### [type]/[name]

| Rule | Severity | Message |
|------|----------|---------|
| rule-id | error/warning | message |
```

If a component has no findings, omit it (don't list "PASS" entries in a security report).

If ALL components passed all deterministic rules, write: "All [N] components passed all [N] deterministic security rules."

## Semantic Security Review

For each component reviewed semantically, list findings:

```
### [type]/[name]

**[category]**: Description of finding.
- Evidence: what was found
- Recommendation: what to do about it
```

If no semantic issues found, write: "Semantic review found no additional issues beyond the deterministic scan."

## Skipped Checks

List any checks that were skipped and why:

```
- YARA signatures: yara-python not installed (pip install yara-python)
- CVE lookups: no dependency files found
```

If nothing was skipped, omit this section.
