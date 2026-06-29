# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [3.7.0] - 2026-06-29

### Added
- New `quality/` rule category with 5 lint rules for instruction effectiveness:
  - `quality/imprecise-instruction`: detect hedging, passive voice, and vague conditions
  - `quality/redundant-guidance`: detect instructions redundant with model defaults or project tooling config (.editorconfig, .prettierrc, .eslintrc, tsconfig.json, pyproject.toml)
  - `quality/unfinished-content`: detect placeholders, TODO/FIXME markers, deferred content (TBD, coming soon), and empty markdown sections
  - `quality/example-gap`: flag skills with many instructions but no code examples
  - `quality/stale-references`: detect deprecated models (text-davinci, gpt-3.5-turbo, claude-v1/v2), sunset APIs, old runtimes (Node 14/16, Python 3.7/3.8), and outdated tools (tslint, create-react-app)
- Shared pattern module `_patterns.py` for tautological detection across rules
- 56 tests covering positive matches and false-positive prevention for all quality rules
- Future plan spec for content intelligence Phase 2-3 rules

## [3.6.2] - 2026-06-29

### Added
- Path traversal protection: `safe_join()` and `is_within()` utilities prevent file references and auto-fixes from escaping the project directory
- 12 tests for path safety covering traversal, symlink escape, and absolute path injection
- Gitleaks and Bandit pre-commit hooks for secret scanning and Python security analysis
- Incident response plan in SECURITY.md (contain, assess, yank, notify, remediate, post-mortem)
- Privacy and data handling section in README documenting what each command sends externally
- CODEOWNERS: both @Benkapner and @csoceanu required for review (2 approvals), with stricter ownership rules for release-critical files

### Fixed
- Broken references rule now rejects path traversal attempts instead of following them
- Command script-exists rule now rejects path traversal in script references
- Auto-fixer validates file paths stay within project root before writing

## [3.6.1] - 2026-06-26

### Fixed
- UNKNOWN CVE severity now defaults to WARNING instead of ERROR (previously fell through to preset default)
- Subprocess calls with dynamic arguments downgraded from ERROR to WARNING (subprocess is a capability, not a vulnerability; only exec chains with decoded/fetched data remain ERROR)
- Parse errors (YAML frontmatter failures) excluded from security scan results (structural defects, not security findings)

## [3.6.0] - 2026-06-25

### Added
- LLM-based adjudication of scanner findings: when `--review` is enabled, each deterministic finding is classified as CONFIRMED, FALSE_POSITIVE, or DOWNGRADED before the risk assessment is computed
- `AdjudicatedFinding` type with `is_confirmed`, `is_false_positive`, and `effective_severity` properties
- Adjudication prompt template for structured LLM review of scanner findings
- 10 new tests covering base64 entropy filtering, subprocess argument analysis, CVE severity mapping, adjudication parsing, and adjudicated finding properties

### Changed
- Security risk assessment now uses adjudicated findings (not raw scanner output) when `--review` is enabled; without `--review`, behavior is unchanged (backward compatible)
- JSON output adds `adjudicated`, `raw_errors`, `raw_warnings`, `confirmed_errors`, `false_positives`, and `downgraded` fields
- Terminal output shows "Scanner: X errors -> After review: Y confirmed, Z false positives" when adjudicated
- `security/mcp-tool-poisoning`: base64 detection now uses Shannon entropy filtering (threshold 4.5 bits/char) and path exclusion to reduce false positives on file paths and command examples
- `security/ast-behavioral`: subprocess/os calls with hardcoded literal arguments are now reported as WARNING instead of ERROR; dynamic/user-controlled arguments remain ERROR
- `security/cve-lookup`: MEDIUM CVEs now produce WARNING (not ERROR), LOW CVEs produce INFO (not ERROR); only CRITICAL/HIGH CVEs produce ERROR

### Fixed
- False positive base64 detections on file paths containing base64-like character sequences (e.g., `/home/user/.specify/extensions.yml`)
- Overly aggressive subprocess detection flagging hardcoded `subprocess.run(["ruff", "check", "."])` as ERROR
- All CVE findings treated as errors in the security preset regardless of actual severity

## [3.5.2] - 2026-06-23

### Added
- Comprehensive tests for `content/broken-references` rule: valid links, URL skipping, anchor skipping, template variable skipping, glob skipping, inline code references, deduplication (7 new test cases)

## [3.5.0] - 2026-06-23

### Added
- Fuzzy matching for rule IDs: suppression comments, preset configs, and registry lookups now warn with "Did you mean?" suggestions when a rule ID doesn't match any registered rule
- Tool-aware rule filtering: rules can declare `tools=("claude",)` or `tools=("cursor",)` to only run for matching components
- `source_tool` field on `ParsedComponent` and `RuleContext` to track whether a component came from `.claude/` or `.cursor/`
- Cursor-aware budget analysis: respects `alwaysApply` frontmatter in `.mdc` files instead of treating all Cursor rules as always-loaded
- Tool-aware report labels: Cursor-only setups show "Cursor Rules" instead of "CLAUDE.md" in reports
- 8 new Cursor-specific tests (source_tool tracking, rule filtering, budget, report labels)

### Fixed
- `security/no-prompt-injection`: removed `\bDAN\b` from jailbreak pattern to prevent false positives on legitimate names (e.g., "Dan reviewed the PR")

### Added
- Positive-match unit tests for all 17 injection regex patterns, proving each detects its target content
- Negative-match tests confirming clean text (including "Dan") does not trigger false positives

### Changed
- `claude-md/exists`, `claude-md/generic-advice`, and `command/shadows-builtin` rules now only fire for Claude Code components (skipped for Cursor)
- `claude-md/skill-duplication` uses Cursor-appropriate message text when evaluating Cursor rules
- System analysis messages use tool-aware labels ("cursor rules" vs "CLAUDE.md")

## [3.4.0] - 2026-06-18

### Added
- `--watch` flag for `setup-eval-lint` that monitors agent setup files and re-runs lint on save

## [3.3.0] - 2026-06-17

### Added
- Impact field on rubric issues: states concrete runtime consequence for each finding
- Attack scenarios required for security review FLAG findings
- Evaluation metadata in all command outputs (version, duration, components, LLM call info)
- Parallel LLM calls in review and security commands (ThreadPoolExecutor, max 4 workers)
- Batch evaluation for small components (up to 3 per LLM call)
- Multi-tool expansion future plan (Codex, Cline, Gemini CLI, Windsurf file patterns)
- `EvalMetadata` dataclass for structured metadata output
- Batch prompt template for grouped component evaluation
- LLM client call counters (total/succeeded) for metadata tracking

### Changed
- JSON output includes `impact`, `verdict`, and `metadata` fields
- LLM prompt (issue-template.md) requests impact for each issue
- Security review rubric requires concrete attack scenarios for FLAG findings
- All review rubric files include impact guidance sections
- All SKILL.md files and Cursor commands include metadata footer instructions

### Fixed
- Broken symlink in `skills/eval-skill/rubric/skills-rubric.md` (pointed to old directory name)

## [3.1.2] - 2026-06-17

### Changed
- Renamed `setup-eval-skill` command to `eval-skill` across CLI, Claude Code plugin, and Cursor
- Renamed `how-to-contribute.md` to `CONTRIBUTING.md` (standard convention)
- LLM dependencies (anthropic, google-genai) now included in default install (no separate extras)
- Simplified README (removed duplication, fixed inconsistencies)

### Added
- `SECURITY.md` with vulnerability reporting instructions
- `py.typed` marker for type checking support
- PyPI version badge in README

## [3.1.0] - 2026-06-16

### Changed
- Renamed package from `harness-eval-lab` to `setup-eval` on PyPI (`pip install setup-eval`)
- Renamed CLI entry point from `harness-eval-lab` to `setup-eval`
- Renamed all commands: `eval-setup-lint` to `setup-eval-lint`, `eval-setup-review` to `setup-eval-review`, `eval-setup-security` to `setup-eval-security`, `eval-skill` to `eval-skill`
- Renamed plugin skill directories to match new command names
- Cursor commands rewritten to use in-session LLM (no extra API key needed for review/security/skill)

## [3.0.0] - 2026-06-16

### Added
- Cursor IDE support: discovers `.cursor/rules/*.mdc`, `.cursorrules`, `.cursor/commands/*.md`, `.cursor/skills/*/SKILL.md`, `.cursor/hooks.json`, `.cursor/mcp.json`
- Multi-tool auto-detection: reports which tools a project uses (Claude Code, Cursor, or both)
- 4 Cursor commands (`.cursor/commands/`): setup-eval-lint, setup-eval-review, setup-eval-security, eval-skill
- Component deduplication across tools (shared skills are not double-counted)
- "Detected tools" shown in terminal and JSON output
- Cursor file patterns added to fingerprinting for change detection
- Published to PyPI: `pip install setup-eval`
- 14 new tests for Cursor discovery and linting (153 total)

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
