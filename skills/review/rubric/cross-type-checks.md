# Cross-Type Optimization Checks

Answer each of the 21 checks with YES or NO and a one-line explanation. Do not skip any.

## What good looks like

A well-structured setup follows these principles:
- CLAUDE.md contains only universal facts needed every session (under 200 lines per file). No procedures, no domain-specific rules.
- Skills each have one clear job, with SKILL.md under 500 lines. Detailed procedures live in reference files.
- Hooks enforce deterministic rules (secret scans, formatting). Advisory behavior lives in CLAUDE.md or skills.
- Commands (user-triggered skills) are reserved for explicit, high-stakes, or destructive actions. Passive behavior uses auto-invoked skills.
- Nothing is documented that Claude already knows (git, package managers, testing frameworks, standard language features, Docker, CI/CD, debugging).

## Transformations (1-11)

1. **Skill -> Hook:** If a skill contains rules that MUST happen every time without exception, that's a hook, not a skill. Skills are advisory (~80% adherence). Hooks are deterministic (100%). Test: "If Claude ignores this instruction, would something break?" If yes, it should be a hook.

2. **Skill -> Command:** If a skill describes a specific workflow the user triggers explicitly (e.g., "audit my code", "deploy to staging"), it should be a command (skill with `disable-model-invocation: true`). Auto-invoked skills are for passive behavior Claude detects. User-triggered actions are commands.

3. **Command -> Skill:** If a command describes general behavior that should always be active, it should be a skill with auto-invocation. Ask: "Does the user need to remember to trigger this, or should Claude recognize when it's needed?"

4. **Skill content -> CLAUDE.md:** If a skill contains rules that apply to EVERY conversation (e.g., "always use uv", "never commit .env"), those belong in CLAUDE.md. But check: would adding them push CLAUDE.md over 200 lines? If so, keep in a skill or split CLAUDE.md into subdirectory files.

5. **CLAUDE.md content -> Skill:** If CLAUDE.md contains domain-specific rules that only matter sometimes, or multi-step procedures, those waste context every session. Move to a skill. (See claude-md-rubric.md: "Procedures belong in skills")

6. **CLAUDE.md -> Hook:** If CLAUDE.md says "always run tests before committing" or "always format before saving" but Claude sometimes forgets, make it a hook. Hooks enforce; CLAUDE.md advises.

7. **Agent <-> Skill consistency:** Do agent's referenced skills exist? Do agent's instructions conflict with the referenced skill's instructions? Is the agent duplicating content already in its skills?

8. **Agent <-> Agent overlap:** Do multiple agents share large blocks of identical text? If so, extract to a shared skill.

9. **Agent <-> CLAUDE.md:** Are there rules in CLAUDE.md that should be in agent definitions, or vice versa?

10. **Skill structure optimization:** For skills with SKILL.md over 500 lines, or over ~800 tokens containing detailed procedures/tables: recommend splitting into thin SKILL.md + reference files (progressive disclosure). SKILL.md should be a routing and context document; details go in reference files.

11. **Guidelines extraction:** For skills with hard limits inline (MUST/NEVER/ALWAYS) but no guidelines.md: recommend extracting. Not a requirement, just a recommendation.

## Setup-Wide (12-18)

12. **Merge candidates:** Skills covering related topics that would be stronger combined.

13. **Overlapping triggers:** Skills whose descriptions might cause multiple to load unnecessarily. Check for vague or overly broad trigger phrases that match the same user requests.

14. **Coverage gaps:** Obvious missing areas based on what's present.

15. **Total context budget:** Sum all always-loaded tokens (CLAUDE.md + all SKILL.md files), warn if >20% of context window.

16. **Redundancy across types:** Same instruction appearing in CLAUDE.md AND a skill (double token cost). Also flag if any component documents things Claude already knows (git workflows, package managers, testing frameworks, standard language features, Docker, CI/CD patterns, debugging).

17. **Conflicts across types:** CLAUDE.md says one thing, a skill says the opposite. Or a hook enforces a rule that contradicts CLAUDE.md or a skill.

18. **Command shadows built-in:** Does any command share a name with a Claude Code built-in (init, review, security-review, help, clear, compact, config, cost, doctor, login, logout, memory, model, permissions, status, vim)?

## Behavioral Patterns (19-21)

19. **Mandate stacking:** Count skills with coercive language (MUST, ALWAYS, NEVER) in descriptions or hard gates in body. If >2 skills mandate pre-conditions, they create competing demands. Flag and suggest making most advisory.

20. **Autonomy erosion:** If skills intercept broad work categories AND contain hard gates, the user loses control. Flag broad-trigger + hard-gate combinations.

21. **Broad trigger collision:** Multiple skills with overlapping broad triggers waste context by loading redundant instructions.

## Output format

```
### Transformations
  1. Skill -> Hook:               [YES/NO] - [one-line explanation]
  2. Skill -> Command:            [YES/NO] - [one-line explanation]
  3. Command -> Skill:            [YES/NO] - [one-line explanation]
  4. Skill content -> CLAUDE.md:  [YES/NO] - [one-line explanation]
  5. CLAUDE.md -> Skill:          [YES/NO] - [one-line explanation]
  6. CLAUDE.md -> Hook:           [YES/NO] - [one-line explanation]
  7. Agent <-> Skill:             [YES/NO] - [one-line explanation]
  8. Agent <-> Agent:             [YES/NO] - [one-line explanation]
  9. Agent <-> CLAUDE.md:         [YES/NO] - [one-line explanation]
  10. Skill structure:            [YES/NO] - [which skills and why]
  11. Guidelines extraction:      [YES/NO] - [which skills and why]

### Setup-Wide
  12. Merge candidates:           [YES/NO] - [which or "none"]
  13. Overlapping triggers:       [YES/NO] - [which or "none"]
  14. Coverage gaps:              [YES/NO] - [what's missing or "none"]
  15. Total context budget:       [tokens] ([pct]%) - [OK/WARNING]
  16. Redundancy across types:    [YES/NO] - [what or "none"]
  17. Conflicts across types:     [YES/NO] - [what or "none"]
  18. Command shadows built-in:   [YES/NO] - [which or "none"]

### Behavioral Patterns
  19. Mandate stacking:           [YES/NO] - [how many, acceptable?]
  20. Autonomy erosion:           [YES/NO] - [which or "none"]
  21. Broad trigger collision:    [YES/NO] - [which or "none"]
```
