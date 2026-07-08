# Lint Report Format

```
## Setup Lint: <setup-name>

Components: [N]
Total tokens: [N]

---

## Inventory

| Type | Count | Tokens | Errors | Warnings |
|------|-------|--------|--------|----------|
| Skills | [N] | [N] | [N] | [N] |
| Commands | [N] | [N] | [N] | [N] |
| CLAUDE.md | [N] | [N] | [N] | [N] |
| Hooks | [N] | [N] | [N] | [N] |
| Agents | [N] | [N] | [N] | [N] |

---

## Token Budget

  Always-loaded (CLAUDE.md, hooks): [N] tokens ([pct]%)
  On-demand (skills, commands, agents): [N] tokens ([pct]%)

  By type:
    [type]    [tokens] tokens ([pct]%)

---

## Context Utilization

  Always-loaded: [N] tokens
  Peak (all loaded): [N] tokens

  Model                     Window      Always    Peak     Left
  ─────────────────────────────────────────────────────────────────
  gpt-4o                    128,000      [N]%     [N]%     [N]%  (!)
  claude-haiku-4.5          200,000      [N]%     [N]%     [N]%
  claude-sonnet-4.6         200,000      [N]%     [N]%     [N]%
  claude-opus-4.6           200,000      [N]%     [N]%     [N]%
  ...
  claude-opus-4.8-1m      1,000,000      [N]%     [N]%     [N]%
  gemini-2.5-flash        1,048,576      [N]%     [N]%     [N]%

  (!) = peak load exceeds 20% of context window

Only show models where utilization is non-trivial. If all 1M models show <1%, group them on one summary line.

---

## Trigger Analysis

  [N]/[N] skills have descriptions
  [N] skills lack activation context ('use when' phrasing):
    - [skill name]
  [N] trigger overlap(s) detected:
    - [skill-a] <-> [skill-b] ([pct]% similar)

---

## Dependencies

  [N] broken reference(s):
    - [source] references missing [target]

Or: No broken references.

---

## Findings

  [!] [finding text]
  [!] [finding text]

Or: No system-level findings.

---

## Inspection Results

  [N] components inspected, [N] errors, [N] warnings

  ### Skills ([N])

    [skill-name]                               PASS
    [skill-name]                               [N] errors, [N] warnings
      [X] rule-id: message
      [!] rule-id: message

  ### Commands ([N])

    [cmd-name]                                 PASS
    [cmd-name]                                 [N] warnings
      [!] rule-id: [N] findings
            [detail]
            [detail]

  ### Hooks ([N])

    hooks                                      [N] warnings
      [!] rule-id: message

  ### CLAUDE.md ([N])

    CLAUDE.md                                  PASS

  ### Agents ([N])

    [agent-name]                               PASS

Group by component type. Show PASS for clean components. For components with findings, show error/warning counts on the status line and details indented below. When a single rule fires multiple times, compress into "[N] findings" with details listed underneath.
```
