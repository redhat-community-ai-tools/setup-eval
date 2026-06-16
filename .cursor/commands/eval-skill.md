# Eval Skill

Deep-evaluate a single skill individually and in the context of the full setup. Runs lint rules, contextual analysis (overlap with other skills, CLAUDE.md duplication, trigger conflicts), and optional rubric scoring.

## Arguments

$ARGUMENTS should be the path to the skill directory (containing SKILL.md).

## Instructions

1. Determine the skill path from $ARGUMENTS. If not provided, ask the user which skill to evaluate.

2. Run the eval-skill command:

```bash
uv run harness-eval-lab eval-skill <skill-path> --context .
```

For rubric scoring (requires API key):

```bash
uv run harness-eval-lab eval-skill <skill-path> --context . --rubric --provider gemini
```

3. Present the results:
   - Lint findings (errors, warnings)
   - Contextual analysis: content overlap with other skills, overlap with system instructions, trigger overlaps
   - Rubric issues (if --rubric was used)

4. If the tool is not installed, tell the user to clone and set up:

```bash
git clone https://github.com/redhat-community-ai-tools/harness-eval-lab.git
cd harness-eval-lab
uv sync --extra llm  # if using --rubric
```
