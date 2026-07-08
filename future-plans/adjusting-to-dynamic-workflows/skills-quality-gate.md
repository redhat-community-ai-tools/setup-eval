# Skills Ecosystem Quality Gate

> **Status:** future

## The problem

The skills ecosystem grew from zero to hundreds of skills in about six months. Many are low-quality: vague descriptions, bloated token counts, duplicate content, missing "use when" phrasing. Every skill's metadata (name + description) loads into the system prompt at startup. Bad skills waste that space and confuse trigger matching.

A skill with a vague description like "helps with documents" might activate when it shouldn't, pushing better skills out of the context window. With dynamic workflows referencing skills and skills being created by agents, quality control becomes more important.

## The concept

Use `setup-eval` as an automated quality gate for skills before they're published, installed, or added to a team setup. Like a linter in CI: if the skill doesn't pass, it doesn't get merged.

## Approaches explored

### Approach 1: CI integration

Add `setup-eval scan skills/ --preset strict` to the CI pipeline. Skills that fail the check don't get merged. Teams enforce quality at PR time.

**Trade-offs:**
- Uses existing infrastructure (scan command, presets)
- Catches problems before they reach users
- Needs a "strict" preset tuned for skill quality (not security)
- Binary pass/fail might be too harsh for new skills

### Approach 2: Skill report card

A dedicated `setup-eval grade <skill-path>` command that produces a concise pass/fail report card for a single skill. Designed for quick feedback during development, not CI gating.

**Trade-offs:**
- Better developer experience than reading a raw scan output
- Can include actionable fix suggestions
- Doesn't enforce anything (advisory only)
- Could be a different output format of `eval-skill` rather than a new command

### Approach 3: Registry/marketplace integration

If a shared skills registry emerges, `setup-eval scan` becomes part of the submission process. Every skill submission gets scanned before it's listed.

**Trade-offs:**
- Scales quality control to the ecosystem level
- Depends on a registry existing (doesn't yet)
- Needs a standardized scoring threshold ("what passes?")
- Could create a perverse incentive to game the rules rather than improve quality

## Recommended direction

Start with **Approach 1 (CI integration)** because it's the simplest and uses existing tools. Create a `strict-skills` preset and a CI template. This gives teams a quality gate today.

Add **Approach 2 (report card)** as a developer-facing UX improvement. When you're authoring a skill, you want quick feedback, not a full scan report.

**Approach 3** is forward-looking. Build it when a registry exists.

## How to build it

### The `strict-skills` preset

A new preset in `src/setup_eval/config/presets.py` that enforces Anthropic's published best practices:

| Rule | Severity in strict-skills |
|------|--------------------------|
| `frontmatter/description-required` | error |
| `frontmatter/description-quality` (all checks) | error (not warning) |
| `frontmatter/format-valid` | error |
| `content/token-budget` | error (with lower threshold, e.g., 2000 tokens) |
| `content/broken-references` | error |
| `security/no-prompt-injection` | error |
| `security/no-credential-access` | error |

Rules that don't apply to quality gating (like `content/duplicate-detection`, which requires context of other skills) stay at warning or off.

### GitHub Action template

A reusable GitHub Action that teams can add to their repos:

```yaml
- name: Check skill quality
  run: |
    pip install setup-eval
    setup-eval scan skills/ --preset strict-skills --fail-on-error
```

### Report card format

A compact output for `eval-skill` that answers three questions:
1. Does it pass structural checks? (yes/no)
2. Does it follow Anthropic's best practices? (yes/no, with specific violations)
3. Is it ready to add to a setup? (yes/no, with a one-line reason)

## Open questions

- What's the right threshold for "pass"? Zero errors? Zero errors and fewer than 3 warnings?
- How to handle intentionally large skills (e.g., skills with extensive reference docs)?
- Should the quality gate also check the skill's reference files, or only SKILL.md?
- Should there be tiers? ("bronze" = passes scan, "silver" = passes scan + rubric, "gold" = passes scan + rubric + A/B test)
