# Content Intelligence: Are These Instructions Actually Effective?

**Status:** future
**Created:** 2026-06-29

## Problem

A setup can pass every structural rule, every security check, and every metadata validation, while the instructions themselves are vague, redundant, or positioned where the model won't pay attention to them.

The tool currently evaluates whether a setup is well-formed and safe. It does not evaluate whether the instructions will actually work well with an LLM. This is a blind spot: the setup looks correct on paper but underperforms at runtime because the instructions are poorly written, poorly organized, or say things the model already knows.

This is the gap between structural correctness and instruction effectiveness.

## Proposal

A new category of deterministic lint rules under `quality/` that check instruction quality and effectiveness. No LLM required for detection. All rules are fast, CI-suitable, and heuristic-based (regex, position analysis, token counting, cross-component comparison).

What makes these rules different from structural checks: structural rules ask "is this well-formed?" while quality rules ask "will the model actually follow this?" The answer depends on how instructions are phrased, where they're positioned, whether they contradict each other, and whether they add anything the model doesn't already know.

### New rules

#### 1. `quality/imprecise-instruction` (WARNING)

Detect language that weakens instruction compliance. Three sub-categories:

**a) Hedging:** Non-committal phrasing where the author clearly intends a firm instruction. Patterns: "try to", "if possible", "you might want to", "perhaps consider", "ideally you should", "it would be nice to".

**b) Passive directives:** Instructions written in passive voice that obscure who should act. "Tests should be run before merging" is weaker than "Run tests before merging." The model has to infer that it is the actor. Patterns: "should be [verb]ed", "needs to be [verb]ed", "is expected to be", "are to be [verb]ed".

**c) Conditional ambiguity:** Conditional instructions where the condition itself is vague. "If appropriate, refactor the code" leaves the model to decide what "appropriate" means. Contrast with "If the function exceeds 50 lines, refactor it" where the condition is testable. Patterns: "if needed", "if appropriate", "when relevant", "as necessary", "if applicable", "where suitable".

**False-positive mitigation:**
- Skip lines inside code blocks (fenced or indented)
- Skip lines that are clearly examples or quoted text (lines starting with `>` or inside blockquotes)
- Skip hedging words that appear as part of a described behavior, not an instruction (e.g., "The API will try to reconnect" describes system behavior, not an instruction to the agent)
- For passive voice: only flag lines that contain an instruction verb (run, check, validate, create, update, use, add, remove, test, deploy, build, format, lint) in passive form. Don't flag descriptive passive voice ("the database is hosted on AWS")
- For conditional ambiguity: only flag when the vague condition is the primary gating clause, not a parenthetical. "Refactor if appropriate" is flagged. "Use the standard pattern (adjusting as needed for edge cases)" is fine because "as needed" modifies a secondary clause

**Implementation:** Multi-pass regex with context awareness. First pass identifies candidate lines (not in code blocks, not in blockquotes). Second pass classifies the type (hedging, passive, conditional). Third pass applies false-positive filters (is this descriptive text or an instruction?).

**Example findings:**
```
WARNING  imprecise-instruction: Line 14: 'try to use TypeScript' — hedging weakens compliance. State directly: 'use TypeScript'
WARNING  imprecise-instruction: Line 28: 'Tests should be run before merging' — passive voice obscures the actor. Use active: 'Run tests before merging'
WARNING  imprecise-instruction: Line 41: 'Refactor if appropriate' — condition is too vague for the model to evaluate. Specify when.
```

#### 2. `quality/tautological` (WARNING)

Detect instructions the model already follows by default, in skills, commands, and agents. This extends `claude-md/generic-advice` beyond CLAUDE.md to all component types, with a broader pattern set.

Two layers of detection:

**a) Direct tautology:** Explicit statements of default behavior. Patterns: "write tests for your code", "use descriptive variable names", "follow the DRY principle", "handle edge cases", "validate user input", "use proper error handling", "write readable code", "document your changes", "keep functions small", "separate concerns".

**b) Implied tautology:** Instructions that describe standard professional practice without project-specific context. "Make sure your code compiles before committing" (the model won't commit code that doesn't compile). "Review your changes before submitting" (the model reviews its work by default).

**Relationship to existing rules:** `claude-md/generic-advice` handles CLAUDE.md with 12 patterns. This rule targets skills, commands, and agents with a broader, deduplicated pattern set. The two rules share a base pattern list via a common module, extended per component type. The shared list avoids maintenance drift.

**False-positive mitigation:**
- Only flag when the instruction has no project-specific qualifier. "Write tests" is tautological. "Write tests using pytest with the fixtures in `tests/conftest.py`" is specific and useful.
- Heuristic: if the flagged line also contains a file path, tool name, or project-specific term (detected via the component's frontmatter `name` field or referenced paths), skip it
- Skip lines inside examples sections (under headings containing "example", "sample", "template")

**Implementation:** Shared pattern module at `src/setup_eval/inspection/rules/quality/_patterns.py` used by both this rule and `claude-md/generic-advice`. Each pattern is a `(label, regex, specificity_check)` tuple where `specificity_check` is an optional function that returns True if the line contains enough project-specific context to not be tautological.

**Example finding:**
```
WARNING  tautological: Line 8: 'handle edge cases' — the model does this by default. Either remove or add project-specific detail.
```

#### 3. `quality/negative-only` (WARNING)

Detect prohibitions without constructive alternatives. Goes beyond simple "don't/never" matching with two analysis levels:

**a) Standalone prohibition:** A line with a negative keyword ("don't", "never", "avoid", "do not", "must not", "should not") where no positive alternative appears within a 4-line window after it. Positive signals: "instead", "use", "prefer", "rather", "alternative", a colon followed by a concrete noun/verb, or a code block.

**b) Negation-heavy sections:** When a markdown section (heading-to-heading) has more than 60% of its instruction lines starting with negative keywords, flag the section. A section that's mostly "don't do X, don't do Y, don't do Z" is structurally unhelpful even if each prohibition has a local alternative.

**False-positive mitigation:**
- Don't flag negations in security-focused sections (under headings containing "security", "safety", "warning", "danger"). Security instructions are legitimately prohibitive.
- Don't flag "do not" / "never" that appear in descriptions of expected behavior ("The system will never retry failed payments") vs instructions to the agent
- Require the negative keyword to be at the start of a clause or sentence, not mid-sentence. "The function returns null, never undefined" describes behavior, not a prohibition.

**Implementation:** Line-by-line scan with a lookahead window. Track negation ratio per section for the section-level check.

**Example findings:**
```
WARNING  negative-only: Line 22: 'Never use SELECT *' has no positive alternative within 4 lines. Add what to do instead.
WARNING  negative-only: Section '## Code Style' has 5/7 instruction lines starting with prohibitions. Reframe as positive guidance.
```

#### 4. `quality/attention-zone` (INFO)

Detect critical instructions positioned where LLM attention is weakest. Based on the well-documented U-shaped attention pattern in transformer models: strong attention at the beginning and end of input, measurable degradation in the middle.

**How it works:**

Unlike a simple "middle third" heuristic, this rule uses a position-based risk score:

1. Divide the file into 10 equal segments by line count
2. Segments 1-2 (top 20%) and 9-10 (bottom 20%) are the "high attention" zone
3. Segments 4-7 (middle 40%) are the "low attention" zone
4. Segments 3 and 8 are transitional (not flagged)

Only fires when ALL of these conditions are met:
- The file is longer than 80 lines (short files don't have meaningful attention gradients)
- The line contains an emphasis marker: words in ALL-CAPS that are instruction keywords (MUST, CRITICAL, NEVER, ALWAYS, IMPORTANT, REQUIRED, WARNING, ESSENTIAL), bold markdown (`**must**`), or admonition-style markers (`> **Note:**`)
- The emphasis marker is part of an instruction, not a heading or example

**Why this threshold design:** Attention degradation is gradual, not a cliff at the one-third mark. The 10-segment model avoids flagging content that's only slightly past the top section. The 80-line minimum prevents noise on typical short skills.

**False-positive mitigation:**
- Skip headings (lines starting with `#`), since headings provide their own structural salience
- Skip lines inside code blocks
- Skip files with fewer than 3 emphasis markers (if the whole file is critical, none of it is uniquely important)
- Only flag when the critical instruction is NOT under a heading that itself contains emphasis. If the section heading is "## CRITICAL: Input Validation", the content under it inherits the heading's salience.

**Example finding:**
```
INFO     attention-zone: Line 112: 'MUST validate all user input' is in the low-attention zone (segment 6/10 of 240-line file). Consider moving to the first or last 20% of the file.
```

#### 5. `quality/wall-of-text` (INFO)

Warn when a markdown section is too dense for effective LLM processing. Two sub-checks:

**a) Section length:** A markdown section (content between two headings of the same or higher level) exceeds 400 tokens without sub-headings. Threshold is configurable via rule options.

**b) Instruction density:** A section contains more than 15 discrete instruction-like lines (lines starting with imperative verbs, numbered items, or list markers with action verbs) within 400 tokens. High-density instruction blocks overwhelm the model; it may follow the first few and lose track of the rest.

**Why two sub-checks:** A 600-token narrative section with 3 instructions is too long but manageable (just needs sub-headings). A 400-token section with 25 tightly-packed instructions is a different problem, even if it's technically within length. Both need different fixes.

**Implementation:** Parse markdown headings to identify sections. Count tokens using the existing `count_tokens()` utility. For density, scan for instruction-starting patterns (imperative verbs, numbered lists, `-`/`*` list items followed by a verb).

**Example findings:**
```
INFO     wall-of-text: '## Development' section is ~720 tokens with no sub-headings. Break into smaller sections.
INFO     wall-of-text: '## Rules' section has 22 instruction lines in ~380 tokens. Consider grouping related instructions under sub-headings.
```

#### 6. `quality/hook-candidate` (INFO)

Detect prose instructions that describe deterministic, event-triggered actions better enforced as hooks.

**What qualifies:** An instruction is a hook candidate when it describes:
- A specific action (run a command, execute a script, check something)
- Triggered by a specific event (before commit, after save, before push, on PR)
- Expected to happen every time (indicated by "always", "make sure", "ensure", "every time", or imperative without qualification)

**Pattern design:** Two-part matching: (1) an event trigger phrase ("before committing", "before pushing", "after every change", "before submitting", "before merging", "on every PR") AND (2) a command-like token in the same sentence (a tool name like `ruff`, `pytest`, `eslint`, `prettier`, a script path like `./scripts/`, or a shell-like pattern like `run ...`).

Both parts must be present. "Before committing, think about the impact" has a trigger but no command (it's guidance, not a hook candidate). "Run ruff format" has a command but no trigger (it's a general instruction, not event-bound).

**False-positive mitigation:**
- Require both trigger AND command in the same sentence or adjacent lines
- Skip instructions inside conditional blocks ("If you're making a large change, run tests before committing" is conditional guidance, not a universal enforcement candidate)
- Skip when the instruction is already described as optional ("you may want to run X before committing")
- Cross-check: if the setup already has a matching hook in `context.scan_state` (populated by `hooks/valid-structure`), skip the finding. No point suggesting a hook that already exists.

**Example finding:**
```
INFO     hook-candidate: Line 31: 'Always run ruff format before committing' — consider converting to a pre-commit hook for reliable enforcement.
```

#### 7. `quality/placeholder-text` (WARNING)

Detect unfilled template markers and scaffolding remnants.

**Patterns (ordered by confidence):**

- **High confidence:** `[INSERT ...]`, `[YOUR ...]`, `<your-...-here>`, `[PLACEHOLDER]`, `[FILL IN]`, `[CHANGE THIS]`, `[UPDATE THIS]`. These are almost certainly unfilled templates.
- **Medium confidence:** `TODO:`, `FIXME:`, `XXX:`, `HACK:` (with colon, distinguishing from prose use of the word "todo"). These are unfinished items.
- **Low confidence (suppressed by default):** `{{...}}` double-brace patterns, bracket-enclosed ALL-CAPS like `[PROJECT_NAME]`. These have high false-positive rates in files that legitimately use template syntax.

**False-positive mitigation:**
- Skip code blocks entirely (template syntax in code is intentional)
- For TODO/FIXME: require the colon suffix to distinguish "TODO: add error handling" from "we need to decide the todo list format"
- For bracket patterns: only flag `[ALL_CAPS_WITH_UNDERSCORES]` patterns that contain common placeholder words (YOUR, INSERT, PROJECT, NAME, DESCRIPTION, API, KEY, TOKEN, URL, PATH). Don't flag `[RFC 2119]` or `[Section 3.1]`.
- For `{{...}}`: only flag in non-template files. If the file contains a Jinja/Handlebars import or the project has a templates directory, suppress. This sub-check is off by default (low confidence tier).

**Implementation:** Layered regex with confidence tiers. High-confidence patterns always fire. Medium-confidence patterns fire unless suppressed. Low-confidence patterns are opt-in via rule options.

**Example findings:**
```
WARNING  placeholder-text: Line 5: '[INSERT YOUR PROJECT DESCRIPTION]' looks like unfilled template text.
WARNING  placeholder-text: Line 12: 'TODO: add deployment instructions' — unfinished template section.
```

#### 8. `quality/cross-component-conflict` (WARNING)

Detect conflicting instructions across different components in the same setup. This is unique to multi-component analysis and leverages the existing `context.all_skills` and `context.scan_state` infrastructure.

**How it works:**

Phase 1 (extraction): As each component is scanned, extract "instruction fingerprints" from directive lines: normalized (topic, stance) pairs. For example, "Use tabs for indentation" becomes `(indentation, tabs)`. "Always use 2-space indentation" becomes `(indentation, 2-space)`. Store these in `context.scan_state`.

Phase 2 (comparison): After all components are scanned, compare fingerprints across components. Flag when two components express opposing stances on the same topic.

**Topics to track:** A curated list of common configuration domains where contradictions cause real problems:
- Indentation (tabs vs spaces, 2 vs 4)
- Quotes (single vs double)
- Semicolons (use vs omit)
- Trailing commas (use vs omit)
- Naming convention (camelCase vs snake_case vs kebab-case)
- Testing framework preferences
- Import ordering
- Error handling style (throw vs return error)
- Logging approach

**Why this matters:** When CLAUDE.md says "use 4-space indentation" and a skill says "use tabs", the model gets contradictory instructions. It will follow one and ignore the other, producing inconsistent output. Worse, which one it follows may vary between sessions. This is a common real-world problem when setups are assembled from multiple authors or templates.

**False-positive mitigation:**
- Only flag when both components are active in the same context. A skill scoped to "Python development" saying "use spaces" doesn't conflict with a skill scoped to "Go development" saying "use tabs."
- Use the extracted topic list, not free-text similarity. Two components that both mention "indentation" aren't necessarily conflicting.
- Require opposing stances, not just different wording. "Use 4-space indentation" and "Indent with 4 spaces" are the same stance, differently worded.

**Implementation:** Topic extraction via keyword + pattern matching (not TF-IDF). Store in `scan_state["quality_fingerprints"]`. Comparison runs as a post-scan phase. This rule needs to run after all components are processed, so it uses a two-phase pattern: `create()` extracts and stores, a separate finalize step (or a final pseudo-component scan) does the comparison.

**Example finding:**
```
WARNING  cross-component-conflict: CLAUDE.md says 'use 4-space indentation' (line 15) but skill 'python-dev' says 'use tabs' (line 8). Contradictory instructions produce inconsistent behavior.
```

## Where it lives

- `src/setup_eval/inspection/rules/quality/` (new directory, 8 rule files + shared patterns module)
  - `_patterns.py` — shared pattern lists used by `quality/tautological` and `claude-md/generic-advice`
  - `imprecise_instruction.py`
  - `tautological.py`
  - `negative_only.py`
  - `attention_zone.py`
  - `wall_of_text.py`
  - `hook_candidate.py`
  - `placeholder_text.py`
  - `cross_component_conflict.py`
- Rule IDs follow the `quality/` namespace
- Category: `RuleCategory.CONTENT` (these are content checks, just a different dimension)
- Tests: `tests/test_quality_rules.py` (one test class per rule, with positive matches and false-positive checks)

## Preset configuration

| Rule | recommended | strict | security | pre-workflow |
|------|-------------|--------|----------|--------------|
| `quality/imprecise-instruction` | warning | error | off | off |
| `quality/tautological` | warning | error | off | off |
| `quality/negative-only` | warning | error | off | off |
| `quality/attention-zone` | info | warning | off | off |
| `quality/wall-of-text` | info | warning | off | off |
| `quality/hook-candidate` | info | info | off | off |
| `quality/placeholder-text` | warning | error | off | off |
| `quality/cross-component-conflict` | warning | error | off | off |

All rules are `off` in the `security` and `pre-workflow` presets since they're about instruction quality, not safety or CI gating.

## Implementation order

**Phase 1 (highest value, most differentiated):**
1. `quality/imprecise-instruction` — three sub-categories (hedging, passive, conditional ambiguity) with context-aware false-positive filters
2. `quality/placeholder-text` — layered confidence tiers, straightforward implementation
3. `quality/tautological` — shared pattern module with `claude-md/generic-advice`, specificity-check filter

**Phase 2 (cross-component and structural):**
4. `quality/cross-component-conflict` — unique multi-component analysis using scan_state
5. `quality/negative-only` — windowed lookahead + section-level negation ratio

**Phase 3 (position and density analysis):**
6. `quality/attention-zone` — 10-segment attention model with emphasis marker detection
7. `quality/wall-of-text` — section length + instruction density dual check
8. `quality/hook-candidate` — two-part pattern (event trigger + command), cross-checked against existing hooks

## Report appearance

These rules appear in the standard inspection results, grouped by component type. No changes to the report format are needed.

Terminal output example:
```
  Skills (8)
  ────────────────────────────────────────────────────────
    deploy-skill                             3 warnings
      WARNING  imprecise-instruction: 3 findings
               Line 14: 'try to use TypeScript' — hedging weakens compliance
               Line 28: 'Tests should be run' — passive voice obscures actor
               Line 41: 'Refactor if appropriate' — vague condition

    code-review                              1 warning, 1 info
      WARNING  negative-only: Line 22: 'Never use SELECT *' has no positive alternative
      INFO     attention-zone: Line 112: 'MUST validate input' in low-attention zone (segment 6/10)

  CLAUDE.md (1)
  ────────────────────────────────────────────────────────
    CLAUDE.md                                1 warning, 1 info
      WARNING  cross-component-conflict: CLAUDE.md says 'use spaces' but skill 'python-dev' says 'use tabs'
      INFO     wall-of-text: '## Development' is ~720 tokens with no sub-headings
```

## Target component types

Most rules target all text-bearing components (skills, commands, CLAUDE.md, agents). Exceptions:
- `quality/tautological` skips CLAUDE.md (already covered by `claude-md/generic-advice`)
- `quality/hook-candidate` targets CLAUDE.md and skills (commands and agents rarely contain hook-candidate instructions)
- `quality/attention-zone` only fires on components with 80+ lines
- `quality/cross-component-conflict` runs across all components via scan_state

## Design principles

1. **No false positives over missed findings.** Every rule has explicit false-positive mitigations. A rule that fires incorrectly on real-world setups erodes trust in the entire tool. It's better to miss a real issue than to flag legitimate content.

2. **Context-aware analysis.** Rules don't just match patterns in isolation. They consider whether a line is in a code block, under a security heading, inside an examples section, or describing system behavior vs giving an instruction.

3. **Cross-component awareness.** Several rules use `context.scan_state` to share data across the scan. `cross-component-conflict` compares fingerprints across all components. `hook-candidate` checks whether a matching hook already exists. This is infrastructure that per-file linters cannot provide.

4. **Graduated severity.** Each rule's findings have appropriate severity based on impact. "Your critical instruction is in the middle of the file" is INFO (a suggestion). "Two components give contradictory instructions" is WARNING (will cause inconsistent behavior). Rules don't cry wolf.

5. **Dogfood first.** Before shipping, every rule must produce zero false positives when run on this project's own setup and on 5+ real-world setups. Any false positive discovered during dogfooding must be addressed with a filter, not suppressed.

## Open questions

- Should `quality/tautological` share its pattern list with `claude-md/generic-advice` via `_patterns.py`, or keep separate lists? Sharing reduces maintenance but may need different patterns for skills (which are domain-scoped) vs CLAUDE.md (which is global).
- What is the right threshold for `quality/wall-of-text`? 400 tokens is a starting point. May need calibration against real-world setups. Should it be configurable via rule options (e.g., `["warning", 600]`)?
- For `quality/cross-component-conflict`: how to handle scope-aware conflict detection? Two skills that never activate together can safely contradict. Detecting scope overlap requires understanding skill trigger descriptions, which is fuzzy.
- Should `quality/attention-zone` account for retrieval-augmented setups where the model's context is dynamically composed? In those setups, "position in file" is less meaningful than "position in assembled context."
- How should these rules interact with the LLM review? Should the rubric prompt reference quality rules as categories for the LLM to check more deeply? (e.g., "The lint found 3 hedging instances; evaluate whether the surrounding context makes them acceptable.")

## Success criteria

- Phase 1 rules ship with tests and zero false positives when dogfooded on the project's own setup.
- Rules add measurable value: running on 5+ real-world setups, each rule fires at least once on genuinely improvable content.
- No performance regression: all rules complete within the existing lint budget (they're regex/heuristic, not LLM calls).
- `quality/cross-component-conflict` detects at least one real contradiction in test setups assembled from multiple sources.
- Rule count in README updates from 43 to 51.
