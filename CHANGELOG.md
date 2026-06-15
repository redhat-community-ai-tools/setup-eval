# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2.0.0] - 2026-06-15

### Added
- CI pipeline: GitHub Actions with lint, typecheck, test, and dogfood jobs
- CI enforces minimum 70% test coverage via `--cov-fail-under=70`
- CODEOWNERS file for PR review governance
- Skillsaw linter config (`.skillsaw.yaml`) for skill context budget validation
- `eval-setup-security` CLI command: dedicated security audit with all security rules, AST analysis, YARA scanning, CVE lookups, and optional LLM semantic review
- `eval-setup-security` plugin skill with 4-check semantic security review
- 6 new security inspection rules (MCP least-privilege, MCP tool poisoning, AST behavioral, taint tracking, YARA scan, CVE lookup)
- Security test fixtures (`tests/fixtures/security-issues/`) with injection, credential, exfiltration, and reverse shell patterns
- Security rule unit and integration tests
- E2E CLI tests using Click's CliRunner
- Mock LLM response tests for rubric checker
- Instruction clarity checks added to eval-setup-review rubrics
- PASS/FAIL/WARNING labels with legend in lint output
- Per-rule pass/fail checklist in lint output
- Discovery of `.claude/rules/`, output-styles, and uncategorized files
- Timing output for all plugin skills
- Plugin marketplace support via `marketplace.json`
- Install script and command files for plugin installation
- Native Claude Code plugin system (replaces custom install script)
- Plugin namespace prefix for command names (`harness-eval-lab:eval-setup-lint`)
- Runner abstraction future plan (`future-plans/runner-abstraction/`)
- Setup recommend future plan (`future-plans/setup-recommend/`)
- Security benchmarks future plan (`future-plans/security-benchmarks/`)
- SARIF output future plan (`future-plans/sarif-output/`)
- Prompt versioning: LLM prompts extracted to `src/harness_eval_lab/rubric/prompts/` as markdown files
- `content/circular-references` rule: detect circular reference chains between skills and commands
- `command/references-nonexistent-skill` rule: detect commands referencing skills that don't exist
- Network access detection in hooks: curl, wget, netcat, ncat patterns with dedup against pipe-to-shell
- Release script (`scripts/release.py`) for version bumping, changelog management, and tagging
- PyPI publish workflow (`.github/workflows/publish.yml`)
- README badges: CI status, coverage, Python version, license

### Changed
- Renamed "Layer 1/Layer 2" terminology to "lint/review" throughout codebase
- README updated to remove dimension-based framing, describes review as best-practices + cross-component + redundancy checking
- Future plans restructured from free-form READMEs to structured spec format (problem, proposal, user stories, requirements, success criteria)
- SessionStart `ensure_deps.py` rewritten with isolated venv, stamp-based caching, and uv/pip fallback
- Report output reordered for clarity, added exact timing
- Reduced false positives in lint output
- MCP least-privilege rule skips overdeclared check on SKILL.md-only skills
- Security command outputs only security findings (not full lint)
- Deduplicated YARA/CVE skip notices in security output

### Removed
- References to "5 dimensions" (Soundness, Safety, Coherence, Efficiency, Impact) from README
- `future-plans/impact-dimension/` and `future-plans/scoring-calibration/` removed from README (plans still exist, just not listed as active)
- Context utilization section removed from lint output

## [0.1.0] - 2026-05-01

Initial release.

- 26 deterministic inspection rules across 8 categories
- System-level analysis (token budget, trigger overlaps, dependencies, context utilization)
- LLM-based qualitative review with per-component issue categories
- CLI with 3 commands: eval-setup-lint, eval-setup-review, eval-skill
- Claude Code plugin with 3 skills
- 62 tests
