# Eval Setup Lint

Run 43 deterministic rules + system-level analysis on the agent setup. No LLM. Fast, reproducible, CI-suitable.

## Instructions

1. Ask the user where to present results: terminal or file.

2. Run the lint command on the current project:

```bash
uv run harness-eval-lab eval-setup-lint .
```

For JSON output (if the user prefers file output):

```bash
uv run harness-eval-lab eval-setup-lint . --format json
```

3. Present the report. Include all sections: inventory, token budget, trigger analysis, dependencies, findings, and inspection summary.

4. If the tool is not installed, tell the user to clone and set up:

```bash
git clone https://github.com/redhat-community-ai-tools/harness-eval-lab.git
cd harness-eval-lab
uv sync
```

Then run from within the cloned directory, pointing at their project:

```bash
uv run harness-eval-lab eval-setup-lint /path/to/their/project
```
