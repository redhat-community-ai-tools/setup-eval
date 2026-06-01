---
name: eval-setup
description: Evaluate the full agent setup (CLAUDE.md, skills, commands, hooks, agents, MCP configs) across 5 dimensions. Use when the user wants to check their setup health, find redundancy, detect issues, or get a quality scorecard.
allowed-tools:
  - Bash
  - Read
---

# Evaluate Setup

Evaluate the user's full agent setup across 5 dimensions: Soundness, Safety, Coherence, Efficiency, and Impact.

## What to do

1. Determine the setup path. If the user doesn't specify one, use the current working directory.

2. Run the assessment script:
```bash
uv run python skills/eval-setup/scripts/run_assessment.py <setup-path> recommended
```

3. Read the JSON output. It contains:
   - `dimension_scores`: scores 0-5 for each of the 5 dimensions
   - `overall`: average score
   - `budget`: token budget breakdown (always-loaded vs on-demand)
   - `triggers`: skill trigger overlap analysis
   - `dependencies`: broken references and orphan components
   - `findings`: system-level findings
   - `inspection`: per-component findings from 24 static analysis rules

4. Present the results to the user in a clear, conversational format:
   - Start with the 5-dimension scorecard (use star ratings)
   - Highlight the most important findings (errors first, then warnings)
   - Explain what each finding means and why it matters
   - If the token budget ratio is inverted (>50% always-loaded), explain why that's a problem
   - If there are trigger overlaps, explain which skills would load together unnecessarily
   - End with 3-5 concrete, prioritized suggestions for improvement

5. If the user asks follow-up questions, use the JSON data to answer specifically. Reference exact components, token counts, and rule IDs.

## Scoring Guide

- **Soundness**: Does each component parse correctly? Are references valid? Are required fields present?
- **Safety**: Any credential exposure? Prompt injection patterns? Dangerous hook commands? Unenforced constraints?
- **Coherence**: Any duplicates between components? Trigger collisions? Broken dependencies? Type misplacement?
- **Efficiency**: Is the token budget well-distributed? Any single component dominating? Overlapping triggers wasting context?
- **Impact**: Requires task probing (not yet implemented). Report as "requires empirical testing."

## Verdicts

- 4-5/5: HEALTHY
- 3/5: NEEDS WORK
- 1-2/5: PROBLEMATIC
