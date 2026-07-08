# Commands Rubric

Check each command for issues in 7 categories. For clean commands, use a compact one-line format.

Note: In Claude Code, commands have been merged into the skills system. A command is now a skill with `disable-model-invocation: true` (user triggers it with /name, Claude never auto-invokes). When reviewing commands, consider whether each one belongs in this category or should be a skill with auto-invocation.

## Impact

For every issue flagged, state the runtime consequence. Not "this is a redundancy issue" but what will actually go wrong: wrong skill routing, wasted context tokens displacing useful content, contradictory instructions causing inconsistent behavior, broken commands producing errors, etc.

## Description quality

Flag if:
- Description is missing from frontmatter
- Description is too short or vague (2 words or fewer)
- Description doesn't clearly say what the command does

## Instruction clarity

Flag if:
- Claude wouldn't know what to do or in what order
- Steps are ambiguous or contradictory
- Uses vague language: "handle appropriately", "follow best practices", "be careful"
- Contains hedging where a clear directive is needed: "consider", "try to", "you might want to"
- Important instructions are buried below less important content
- Conditional instructions reference triggers or situations the command wouldn't encounter

## Script integrity

Flag if:
- Referenced script files don't exist
- Discovery pattern is broken

## Scope appropriateness

Flag if:
- Command should be a skill with auto-invocation instead (Claude detects the situation and loads it automatically)
- Ask: "Does the user need to remember to type /name, or should Claude recognize when this is needed?" If Claude should recognize it, this should be a skill with auto-invocation enabled.
- Conversely, commands that perform destructive or high-stakes actions (/deploy, /release) are correct as user-triggered commands.

## Token efficiency

Flag if:
- Command is over 15KB (recommend splitting)
- Command is over 30KB (must split)

## Redundancy with defaults

Flag if:
- Claude already does this without the command
- Built-in capabilities include: plan mode, commit messages, code explanation, code review, init, security-review
- Test: "If i deleted this command, could i get the same result by just asking Claude?" If yes, flag it.

## Robustness

Flag if:
- Command hardcodes assumptions (specific tools, languages, thresholds)
- Doesn't handle missing dependencies gracefully

## Verdict

- **KEEP**: No issues or only minor improvements possible
- **REVIEW**: Multiple issues that reduce effectiveness
- **REMOVE**: Fundamental problems (entirely redundant, broken, or harmful)
