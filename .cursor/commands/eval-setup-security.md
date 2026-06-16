# Eval Setup Security

Deep security audit of the agent setup. Runs all security rules (prompt injection, credential access, data exfiltration, obfuscation, reverse shells, AST analysis, taint tracking, MCP checks) plus optional YARA scanning and CVE lookups.

## Instructions

1. Run the security command:

```bash
uv run harness-eval-lab eval-setup-security .
```

For a full audit with LLM semantic review (requires API key):

```bash
uv run harness-eval-lab eval-setup-security . --review --provider gemini
```

2. Present the results:
   - Risk assessment: SAFE / CAUTION / UNSAFE
   - Security findings by component
   - Per-rule issues with line numbers
   - Skipped checks (if YARA or CVE dependencies are missing)

3. If the tool is not installed, tell the user to clone and set up:

```bash
git clone https://github.com/redhat-community-ai-tools/harness-eval-lab.git
cd harness-eval-lab
uv sync
# Optional: for YARA scanning
pip install yara-python
```
