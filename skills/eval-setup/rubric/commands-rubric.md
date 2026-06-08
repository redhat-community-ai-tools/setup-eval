# Commands Rubric

Check each command for issues in 7 categories. For clean commands, use a compact one-line format.

## Description quality

Flag if:
- Description is missing from frontmatter
- Description is too short or vague (2 words or fewer)
- Description doesn't clearly say what the command does

## Instruction clarity

Flag if:
- Claude wouldn't know what to do or in what order
- Steps are ambiguous or contradictory

## Script integrity

Flag if:
- Referenced script files don't exist
- Discovery pattern is broken

## Scope appropriateness

Flag if:
- This should be a skill (auto-triggered) instead of a command (user-triggered)
- Commands are for explicit actions (/review, /deploy); skills are for passive behavior

## Token efficiency

Flag if:
- Command is over 15KB (recommend splitting)
- Command is over 30KB (must split)

## Redundancy with defaults

Flag if:
- Claude already does this without the command
- Built-in capabilities include: plan mode, commit messages, code explanation, code review
- Test: "if i deleted this command, could i get the same result by just asking Claude?" If yes, flag it.

## Robustness

Flag if:
- Command hardcodes assumptions (specific tools, languages, thresholds)
- Doesn't handle missing dependencies gracefully

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely redundant, broken, or harmful)
