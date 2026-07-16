# Install

setup-eval is available as a CLI tool, a GitHub Action, a Claude Code plugin, and Cursor commands. Pick whichever fits your workflow.

## CLI tool

Install from PyPI:

```bash
pip install setup-eval                # core (token counting via chars/4 heuristic)
pip install setup-eval[tiktoken]      # exact token counting via tiktoken
```

Run:

```bash
setup-eval lint .                         # deterministic lint (59 rules)
setup-eval lint . --watch                 # re-run automatically on file changes
setup-eval lint . --fail-on-error         # exit code 1 on errors (CI gate)
setup-eval lint . --fail-on-warning       # exit code 1 on any finding (strict)
setup-eval lint . --format sarif          # SARIF output for GitHub code scanning
setup-eval lint . --format json           # JSON output for scripts
setup-eval review . --provider gemini     # LLM-based rubric review
setup-eval security .                     # deterministic security scan
setup-eval security . --review            # security scan + LLM semantic review
setup-eval security . --fail-on-warning   # exit code 1 on any security finding
setup-eval skill ./skills/my-skill --context . --rubric   # deep-evaluate one skill
```

`review`, `security --review`, and `skill --rubric` require `GEMINI_API_KEY` or `ANTHROPIC_API_KEY`.

Optional: YARA malware signature scanning for security: `pip install setup-eval[yara]`

## GitHub Action

Add one file to your repo. Every PR gets security + lint checks with inline annotations on the diff.

Create `.github/workflows/setup-eval.yml`:

```yaml
name: Agent Setup Check
on:
  pull_request:
    branches: [main]

permissions:
  security-events: write
  contents: read

jobs:
  setup-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: redhat-community-ai-tools/setup-eval/.github/actions/setup-eval@main
```

No API key needed. No LLM calls. Fully deterministic.

### Options

```yaml
      - uses: redhat-community-ai-tools/setup-eval/.github/actions/setup-eval@main
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
      - uses: redhat-community-ai-tools/setup-eval/.github/actions/setup-eval@main
        with:
          path: |
            .
            internal/scaffold/agent-configs
            apps/frontend
```

### Manual CI setup

If you prefer manual setup over the action:

```yaml
- run: pip install setup-eval
- run: setup-eval security . --fail-on-warning
- run: setup-eval lint . --fail-on-error
- run: setup-eval lint . --format sarif --output results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

## Claude Code plugin

No pip install needed. Install directly from within Claude Code:

```
/plugin marketplace add redhat-community-ai-tools/setup-eval
/plugin install setup-eval@setup-eval
/reload-plugins
```

The 4 commands appear in the `/` menu:
- `/setup-eval:lint`
- `/setup-eval:review`
- `/setup-eval:security`
- `/setup-eval:skill`

No API key needed. Claude evaluates in-session.

To update: re-run the install command.

## Cursor commands

Requires the CLI tool installed first (Cursor commands call it for the deterministic scan):

```bash
pip install setup-eval
```

Then copy `.cursor/commands/` from [this repo](https://github.com/redhat-community-ai-tools/setup-eval) into your project. The 4 commands appear in Cursor's command palette:
- `/lint`
- `/review`
- `/security`
- `/skill`

No API key needed for review/security/skill. Cursor evaluates in-session.
