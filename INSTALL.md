# Install

harness-eval is available as a CLI tool, a GitHub Action, a Claude Code plugin, and Cursor commands. Pick whichever fits your workflow.

## CLI tool

Install from PyPI:

```bash
pip install harness-eval                # core (token counting via chars/4 heuristic)
pip install harness-eval[tiktoken]      # exact token counting via tiktoken
```

Run:

```bash
harness-eval lint .                         # deterministic lint (59 rules)
harness-eval lint . --watch                 # re-run automatically on file changes
harness-eval lint . --fail-on-error         # exit code 1 on errors (CI gate)
harness-eval lint . --fail-on-warning       # exit code 1 on any finding (strict)
harness-eval lint . --format sarif          # SARIF output for GitHub code scanning
harness-eval lint . --format json           # JSON output for scripts
harness-eval review . --provider gemini     # LLM-based rubric review
harness-eval security .                     # deterministic security scan
harness-eval security . --review            # security scan + LLM semantic review
harness-eval security . --fail-on-warning   # exit code 1 on any security finding
harness-eval skill ./skills/my-skill --context . --rubric   # deep-evaluate one skill
```

`review`, `security --review`, and `skill --rubric` require `GEMINI_API_KEY` or `ANTHROPIC_API_KEY`.

Optional: YARA malware signature scanning for security: `pip install harness-eval[yara]`

## GitHub Action

Add one file to your repo. Every PR gets security + lint checks with inline annotations on the diff.

Create `.github/workflows/harness-eval.yml`:

```yaml
name: Agent Setup Check
on:
  pull_request:
    branches: [main]

permissions:
  security-events: write
  contents: read

jobs:
  harness-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: redhat-community-ai-tools/harness-eval/.github/actions/harness-eval@main
```

No API key needed. No LLM calls. Fully deterministic.

### Options

```yaml
      - uses: redhat-community-ai-tools/harness-eval/.github/actions/harness-eval@main
        with:
          path: "."              # directories to scan, one per line (default: repo root)
          preset: "recommended"  # recommended, strict, security, or pre-workflow
          security-gate: "true"  # block on any security finding
          lint-gate: "true"      # block on structural errors
          lint-fail-on: "error"  # "error" (default) or "warning" (strict)
          sarif: "true"          # inline PR annotations via Code Scanning
          version: ""            # pin a specific version (default: latest)
```

### Multiple directories

For monorepos or repos with nested agent configs:

```yaml
      - uses: redhat-community-ai-tools/harness-eval/.github/actions/harness-eval@main
        with:
          path: |
            .
            internal/scaffold/agent-configs
            apps/frontend
```

### Manual CI setup

If you prefer manual setup over the action:

```yaml
- run: pip install harness-eval
- run: harness-eval security . --fail-on-warning
- run: harness-eval lint . --fail-on-error
- run: harness-eval lint . --format sarif --output results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

## Claude Code plugin

No pip install needed. Install directly from within Claude Code:

```
/plugin marketplace add redhat-community-ai-tools/harness-eval
/plugin install harness-eval@harness-eval
/reload-plugins
```

The 4 commands appear in the `/` menu:
- `/harness-eval:lint`
- `/harness-eval:review`
- `/harness-eval:security`
- `/harness-eval:skill`

No API key needed. Claude evaluates in-session.

To update: re-run the install command.

## Cursor commands

Requires the CLI tool installed first (Cursor commands call it for the deterministic scan):

```bash
pip install harness-eval
```

Then copy `.cursor/commands/` from [this repo](https://github.com/redhat-community-ai-tools/harness-eval) into your project. The 4 commands appear in Cursor's command palette:
- `/lint`
- `/review`
- `/security`
- `/skill`

No API key needed for review/security/skill. Cursor evaluates in-session.
