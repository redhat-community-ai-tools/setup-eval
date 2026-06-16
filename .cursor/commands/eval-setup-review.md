# Eval Setup Review

Run LLM-based rubric review on the agent setup. Evaluates each component across specificity, redundancy, trigger quality, token efficiency, instruction clarity, and content quality. Produces KEEP/REVIEW/REMOVE verdicts.

## Instructions

1. Check that an API key is available. The tool supports Gemini (default) or Anthropic:

```bash
echo $GEMINI_API_KEY  # or $ANTHROPIC_API_KEY
```

If no key is set, ask the user to export one.

2. Run the review command:

```bash
uv run harness-eval-lab eval-setup-review .
```

Or with Anthropic:

```bash
uv run harness-eval-lab eval-setup-review . --provider anthropic
```

3. Present the per-component review results. For each component, show:
   - Component name and type
   - Issues found (category, severity, evidence, suggestion)
   - Summary verdict

4. If the tool is not installed, tell the user to clone and set up:

```bash
git clone https://github.com/redhat-community-ai-tools/harness-eval-lab.git
cd harness-eval-lab
uv sync --extra llm
```
