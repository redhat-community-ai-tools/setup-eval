# How to Contribute

This document explains how to add things to setup-eval: new inspection rules, new future plans, and general contribution guidelines.

## Setup

```bash
cd setup-eval
uv sync --extra dev
uv run pre-commit install
```

## Before pushing

```bash
uv run ruff check src/ tests/
uv run pytest tests/ -q
```

Both must pass. Pre-commit hooks will also run automatically.

## Adding a new inspection rule

A rule is a Python class that checks one specific thing about one component type. Each rule lives in its own file.

### 1. Create the rule file

Rules go in `src/harness_eval_lab/inspection/rules/<category>/`. Pick the category that matches what you're checking:

| Category | What it checks | Target type |
|----------|---------------|-------------|
| `structural/` | File existence | Skill |
| `frontmatter/` | YAML metadata quality | Skill |
| `content/` | Body content (duplicates, references, budget) | Skill |
| `security/` | Credential access, prompt injection | Skill |
| `commands/` | Command-specific checks | Command |
| `claude_md/` | CLAUDE.md-specific checks | CLAUDE_MD |
| `hooks/` | Hook structure and safety | Hooks |
| `agents/` | Agent definition checks | Agent |

### 2. Follow the pattern

Every rule has the same shape. Here's the minimal template:

```python
from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class MyNewRule:
    meta = RuleMeta(
        id="category/rule-name",          # unique, kebab-case
        default_severity=Severity.WARNING, # or ERROR, INFO
        fixable=False,
        description="One sentence about what this checks",
        category=RuleCategory.CONTENT,     # match the folder
        messages={
            "message_id": "What to tell the user: {{variable}}",
        },
        target_type=ComponentType.SKILL,   # what component this applies to
        tools=None,                        # None = all tools; ("claude",) = Claude Code only; ("cursor",) = Cursor only
    )

    def create(self, context: RuleContext) -> None:
        # Access the component via context.skill, context.command,
        # context.claude_md, context.hooks, or context.agent
        # Use context.source_tool ("claude", "cursor", or None) for tool-specific behavior
        skill = context.skill
        if not skill.raw_content:
            return

        # Check something, report if it fails
        if some_condition:
            context.report(ReportDescriptor(
                message_id="message_id",
                data={"variable": "value"},
                location=Location(file=skill.skill_md_path, start_line=1),
            ))
```

Look at existing rules for real examples. `commands/shadows_builtin.py` is a simple one. `security/no_prompt_injection.py` is a complex one.

### 3. Register the rule

Add your class to `src/harness_eval_lab/inspection/rules/__init__.py`:

1. Add the import (alphabetical within its section)
2. Add the class to the `for rule_cls in [...]` list

### 4. Update the counts

Update the rule count in:
- `README.md` (the "Inspection Rules (N)" heading and the table)
- `CLAUDE.md` (the project structure line mentioning rule count)

### 5. Add tests

At minimum, add to `tests/`:
- One test where the rule fires
- One test where it doesn't fire on clean input

### 6. Cross-component state

If your rule needs to compare across components (like duplicate detection compares all skills to each other), use `context.scan_state` instead of module-level variables:

```python
STATE_KEY = "my-rule/state"

def create(self, context: RuleContext) -> None:
    if STATE_KEY not in context.scan_state:
        context.scan_state[STATE_KEY] = {"seen": {}}
    state = context.scan_state[STATE_KEY]
    # use state instead of module-level dicts
```

## Adding a new future plan

Future plans go in `future-plans/`, each in its own subfolder.

### 1. Create the subfolder and README

```
future-plans/my-plan-name/
  README.md
```

### 2. Follow the structure

Every plan doc should have:

```markdown
# Title: What Problem This Solves

> **Status:** future

## The problem
What's wrong or missing today. Why should anyone care.

## Why it matters
What happens if we don't solve this. What value solving it provides.

## Approaches explored
### Approach 1: Name
How it works. Trade-offs (bullet list).

### Approach 2: Name
How it works. Trade-offs (bullet list).

## Recommended direction
Which approach to start with and why.

## How to build it
Concrete steps. Where in the code. What to create.

## Open questions
Things we don't know yet. Decisions that need to be made.
```

### 3. Set the status

| Status | Meaning |
|--------|---------|
| `future` | Idea documented, not yet planned |
| `in design` | Actively being designed |
| `in progress` | Implementation underway |
| `built` | Implemented and merged |

### 4. Add to the root README

Add a row to the Future Plans table in `README.md`.

## PR guidelines

- One logical change per PR. Don't mix a new rule with a future plan rewrite.
- Run `uv run ruff check src/ tests/` and `uv run pytest tests/ -q` before pushing.
- PR title should describe what changed, not how (e.g., "Add shadows-builtin rule" not "Add new file and update init").
- If adding a rule, include the test in the same PR.
- If adding a future plan, follow the structure above.

## Project conventions

- **Python:** 3.11+, managed with `uv`
- **Linting:** ruff (select E, F, I, UP, B, SIM)
- **Type checking:** mypy strict
- **Data classes:** frozen dataclasses for domain objects, Pydantic for config
- **CLI:** Click command groups
- **Tests:** pytest, fixtures in `tests/fixtures/`
- **Line length:** 100 characters
