# Distributable Packaging: Setup-Eval as an Installable Module

**Status:** future
**Created:** 2026-07-03

## Problem

setup-eval is distributed through three channels: PyPI (CLI), Claude Code plugin, and manually-copied Cursor commands. Each channel requires separate maintenance and reaches only one assistant's users.

Third-party AI skills package managers can install skills and commands to any supported assistant with a single command. If setup-eval's skills were packaged as a portable module, they could be distributed to Copilot, Gemini CLI, OpenCode, and future assistants without building custom integrations for each.

## Proposal

Package setup-eval's 4 skills and 4 commands as a self-contained module that conforms to the portable module specification (skills in `skills/*/SKILL.md`, commands in `commands/*.md`). The module would coexist with the existing distribution channels, not replace them.

### Module structure

```
setup-eval-module/
  skills/
    setup-eval-lint/
      SKILL.md
      scripts/
        run_assessment.py
        ensure_deps.py
      report-format.md
    setup-eval-review/
      SKILL.md
      rubric/
    setup-eval-security/
      SKILL.md
      scripts/
        run_security_scan.py
      rubric/
    eval-skill/
      SKILL.md
      scripts/
        run_skill_eval.py
      rubric/
  commands/
    setup-eval-lint.md
    setup-eval-review.md
    setup-eval-security.md
    eval-skill.md
```

### Dependency handling

The skills invoke Python scripts that require `setup-eval` installed via pip. The module would include a post-install hook that checks for the pip package and warns if missing:

```yaml
# lola.yaml (or equivalent manifest)
hooks:
  post-install: scripts/check-deps.sh
```

## User stories

### Story 1: Install via package manager

**Given** a developer using Copilot
**When** they run `<pkg-manager> install setup-eval-module -a copilot-vscode`
**Then** the 4 commands appear in Copilot's command palette and the skills are available in `.github/skills/`

### Story 2: Auto-update

**Given** a project with setup-eval installed via a package manager
**When** the developer runs `<pkg-manager> update`
**Then** setup-eval's skills and commands update to the latest version with new rules

### Story 3: Cross-assistant consistency

**Given** a team where some use Claude Code and others use Cursor
**When** all install setup-eval via the same package manager
**Then** everyone gets the same evaluation capabilities regardless of assistant

### Story 4: Discovery via marketplace

**Given** a developer searching for "linting" or "code quality" in a module marketplace
**When** they browse results
**Then** setup-eval appears with description and tags

## Requirements

1. Module must contain all 4 skills with their scripts, rubrics, and report formats
2. Module must contain all 4 commands
3. Existing CLI (`pip install setup-eval`) must remain the primary distribution channel
4. Existing Claude Code plugin must remain independent and unaffected
5. Module frontmatter must include accurate descriptions for marketplace discoverability
6. Post-install hook must validate that `setup-eval` CLI is available and report version
7. Module version must stay in sync with PyPI package version

## Success criteria

- Module installable via at least one third-party package manager to at least 3 assistants
- All 4 commands functional after install (with `setup-eval` pip package as prerequisite)
- Existing CI pipeline (lint, typecheck, test, dogfood) passes unchanged
- Version sync enforced (test or CI check)

## Open questions

1. **Manifest format**: Which module manifest format to use? The emerging standard uses `SKILL.md` frontmatter for metadata, but some package managers also require a separate manifest file.

2. **Python dependency in non-Python environments**: The skills call Python scripts. Users of assistants in non-Python environments would need to install Python + pip + setup-eval separately. Should the module include a self-contained binary (e.g., via PyInstaller) as a fallback?

3. **Ruleset extensibility**: Should the module support custom rulesets? Users might want to add organization-specific rules. This could be done via a `custom-rules/` directory in the module or via a plugin mechanism.

4. **Version pinning**: Should the module pin to a specific setup-eval CLI version, or allow any compatible version? Pinning is safer but creates update friction.

5. **Which package managers to target first**: Prioritize by adoption and maturity. Start with whichever has the most stable module specification and broadest assistant support.
