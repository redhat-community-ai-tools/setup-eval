# SARIF Output for CI Integration

**Status:** built
**Implemented:** 2026-07-07 (v3.8.0, `output/sarif.py` with `--format sarif` on lint and security commands)
**Created:** 2026-06-15

## Problem

setup-eval produces findings in two formats: terminal (human-readable) and JSON (machine-readable). Neither integrates natively with GitHub's code scanning experience. Users who run setup-eval in CI see findings in a log, not inline on the PR diff. This means findings are easy to miss and hard to act on.

GitHub's code scanning feature supports SARIF (Static Analysis Results Interchange Format), the same format used by CodeQL, Semgrep, and ESLint. Tools that produce SARIF get their findings displayed as inline annotations on PR diffs, in the Security tab, and in the code scanning alerts dashboard.

## Proposal

Add a `--format sarif` option to `lint` and `security` that produces a SARIF v2.1.0 JSON file. Users upload this to GitHub using the `github/codeql-action/upload-sarif` action.

### What the user sees after this

A PR that touches agent setup files gets inline annotations like:

```
WARNING: security/no-prompt-injection
Line 15: Contains a prompt injection pattern ('ignore previous instructions').
```

...rendered directly on the PR diff, not buried in a CI log.

### SARIF structure mapping

| setup-eval concept | SARIF field |
|---|---|
| Rule ID (e.g., `security/no-prompt-injection`) | `rules[].id` |
| Rule description | `rules[].shortDescription.text` |
| Rule category | `rules[].properties.tags[]` |
| Finding severity (error/warning/info) | `results[].level` |
| Finding message | `results[].message.text` |
| File path | `results[].locations[].physicalLocation.artifactLocation.uri` |
| Line number | `results[].locations[].physicalLocation.region.startLine` |
| Fix suggestion | `results[].fixes[].description.text` |

### CI workflow example

```yaml
- name: Lint agent setup
  run: |
    uv run setup-eval lint . --format sarif --output results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

### Implementation

Add a `format_sarif()` function in `src/setup_eval/output/sarif.py` that converts `list[Finding]` to a SARIF v2.1.0 document. The SARIF spec is well-defined; the mapping is straightforward since findings already carry rule ID, severity, message, file path, and line number.

No new dependencies needed. SARIF is just JSON with a specific schema.

## User stories

### Story 1: PR gets inline annotations

**Given** a team has setup-eval in their CI pipeline
**When** a developer opens a PR that modifies CLAUDE.md or a skill
**Then** GitHub shows inline annotations on the PR diff for any lint findings, with the rule ID, severity, message, and fix suggestion.

### Story 2: Security findings in GitHub Security tab

**Given** a team runs `security --format sarif` in CI
**When** a security finding is detected (prompt injection, credential exposure)
**Then** the finding appears in the repository's Security tab under Code scanning alerts, with severity and remediation guidance.

### Story 3: Tracking findings over time

**Given** SARIF results are uploaded on every push
**When** a maintainer views the Security tab
**Then** they see a timeline of open/closed/fixed findings, same as CodeQL.

## Requirements

1. Add `--format sarif` to `lint` and `security` CLI commands.
2. Add `--output <path>` flag for writing SARIF to a file (default: stdout).
3. SARIF output must conform to SARIF v2.1.0 schema (`$schema: https://json.schemastore.org/sarif-2.1.0.json`).
4. Each rule in the registry must map to a SARIF `reportingDescriptor` with ID, description, and tags.
5. Severity mapping: error -> error, warning -> warning, info -> note.
6. Fix suggestions (from fixable rules) must map to SARIF `fix` objects.
7. No new runtime dependencies.

## Success criteria

- `lint . --format sarif` produces valid SARIF that passes the Microsoft SARIF validator.
- `github/codeql-action/upload-sarif` accepts the output without errors.
- Findings appear as inline annotations on a test PR.
- All existing terminal and JSON output continues to work unchanged.

## Open questions

1. **Scope:** Should `review` (LLM-based) also support SARIF? LLM findings are non-deterministic and may cause alert churn in the Security tab. Probably lint and security only.

2. **Alert dismissal:** When a user suppresses a finding with a `# setup-eval: disable` comment, should the SARIF output omit it entirely or include it as "suppressed"? SARIF has a `suppressions` field for this.

3. **Tool version:** SARIF includes `tool.driver.version`. Should this come from pyproject.toml at build time or be hardcoded? Build-time extraction is cleaner.
