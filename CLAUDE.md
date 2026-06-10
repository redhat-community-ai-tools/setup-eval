# harness-eval-lab

AI agent setup evaluation tool. See [`README.md`](README.md) for usage, features, and installation.

## Development

- Python 3.11+, managed with `uv`
- Run tests: `uv run pytest`
- Lint: `uv run ruff check src/ tests/`
- Type check: `uv run mypy src/`
- Format: `uv run ruff format src/ tests/`
- See [`how-to-contribute.md`](how-to-contribute.md) for adding rules, plans, and PRs
- See [`CHANGELOG.md`](CHANGELOG.md) for release history

## Project structure

- `src/harness_eval_lab/` - main package
  - `cli.py` - Click CLI (3 commands)
  - `config/` - rule presets (recommended/strict/security/pre-workflow)
  - `core/` - setup discovery, fingerprinting, component types
  - `inspection/` - static analysis: parsers, lint engine, 35 rules, suppression, auto-fix
  - `rubric/` - LLM-based issue detection; prompts in `rubric/prompts/`
  - `analysis/` - system-level analysis (budget, triggers, dependencies, context utilization)
  - `output/` - report generation (terminal + JSON)
  - `utils/` - token counting, TF-IDF similarity, frontmatter parsing, LLM client
- `skills/` - plugin skills with SKILL.md + rubric files + scripts
- `tests/` - pytest test suite with fixtures
- `future-plans/` - planned improvements in structured spec format

## Conventions

- Use `uv run` for all commands
- Frozen dataclasses for domain objects, Pydantic for config
- CLI uses Click command groups
- Plugin skills call Python scripts that use the same engine as the CLI
- Cross-component state in rules uses `context.scan_state`, not module-level variables
- Tests go in `tests/` mirroring the source structure
- LLM prompts live in `src/harness_eval_lab/rubric/prompts/` as markdown files, not inline strings
- `skills/eval-skill/rubric/skills-rubric.md` is a symlink to `skills/eval-setup-review/rubric/skills-rubric.md`; edit the source, not the link
