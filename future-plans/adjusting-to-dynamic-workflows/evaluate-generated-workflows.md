# Evaluating Generated Workflow Code

> **Status:** future

## The problem

Dynamic workflows generate JavaScript orchestration code at runtime. Claude writes a script that spawns subagents, routes them to models, and coordinates their outputs. Sometimes this orchestration is well-designed. Sometimes it's not: vague prompts, no verification step, unnecessary parallelism, missing error handling. Currently there's no way to check.

This is different from evaluating the static setup. The static setup is markdown files you wrote. The workflow is code Claude generated on the fly.

## The concept

Extend setup-eval with a new category of rules that inspect generated workflow scripts for common orchestration mistakes. Think of it as linting for agent orchestration, not just agent configuration.

## What could be checked

Possible rules for a new "workflow" category:

| Rule | What it catches | Why it matters |
|------|----------------|---------------|
| Subagent prompt specificity | Prompts under ~50 words | Vague prompts produce vague, unfocused work |
| Verification pattern usage | Review/audit tasks with no adversarial verify step | Self-preferential bias (agents trust their own output) |
| Fan-out reasonableness | 16 agents for a 3-file change | Wasted tokens and time |
| Schema usage | Subagents returning free-form text | Fragile parsing, silent failures |
| Error handling | No `.filter(Boolean)` after `parallel()` | Null results from failed agents crash downstream |
| Budget awareness | No `budget.remaining()` check in loops | Unbounded loops hit the 1000-agent cap |

## Approaches explored

### Approach 1: Static analysis of workflow scripts

Parse the JavaScript workflow script and apply rules like the existing 26 rules for markdown. Check for patterns in the code: does the script use `schema` in agent calls? Does it filter nulls after `parallel()`?

**Trade-offs:**
- Deterministic and fast
- Requires a JavaScript parser (the current tool only parses markdown and YAML)
- Can only check structural patterns, not semantic quality of prompts
- Workflow scripts follow a known API (agent, parallel, pipeline), so parsing is constrained

### Approach 2: Post-workflow review

After a workflow completes, analyze its results: how many agents failed? How long did each take? Were any agent outputs empty or truncated? This is runtime analysis, not static analysis.

**Trade-offs:**
- Catches real failures, not hypothetical ones
- Requires workflow execution (can't check before running)
- Needs access to workflow logs/traces
- More complex to build (needs integration with Claude Code's workflow runtime)

### Approach 3: LLM-based review

Send the workflow script to Claude and ask it to evaluate the orchestration quality. Similar to how review evaluates skill quality.

**Trade-offs:**
- Can judge semantic quality (are the prompts specific enough for this task?)
- Non-deterministic
- Costs money per evaluation
- Could be part of the plugin's review rather than a new lint rule category

## Recommended direction

Start with **Approach 1 (static analysis)** for the mechanical checks (schema usage, error handling, fan-out count). These are the easiest to build and the most reliable.

Add **Approach 3 (LLM review)** as part of the plugin's review protocol: after running a workflow, Claude reviews the script for orchestration quality.

**Approach 2** is valuable but depends on Claude Code exposing workflow traces, which is outside this tool's control.

## How to build it

1. **New parser:** `parse_workflow(script_path)` that reads a JavaScript workflow script and extracts: agent calls (with prompts, schemas, labels), parallel/pipeline usage, phase declarations, meta block. The scripts follow a known API, so this is pattern matching, not full JS parsing.

2. **New rules:** 4-6 rules in `inspection/rules/workflow/`. Each checks one pattern in the parsed workflow.

3. **New CLI command:** `setup-eval eval-workflow <script.js>` or integrate into `scan` with auto-detection (if the file is `.js` and starts with `export const meta`).

4. **Access to scripts:** Workflow scripts are persisted in the session directory. The tool needs to know where to find them, or the user passes the path explicitly.

## Open questions

- Is a regex-based JS parser sufficient, or does this need a proper AST parser?
- Should workflow evaluation be a separate command or part of `scan`?
- How to handle workflows that are correct but suboptimal? (Warning vs info?)
- Should the tool evaluate workflows in isolation or in context of the setup they operate within?
