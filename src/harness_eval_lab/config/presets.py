from __future__ import annotations

RECOMMENDED: dict[str, str] = {
    "structural/skill-md-exists": "error",
    "frontmatter/description-required": "error",
    "frontmatter/description-quality": "warning",
    "frontmatter/format-valid": "warning",
    "content/token-budget": "warning",
    "content/broken-references": "error",
    "content/duplicate-detection": "warning",
    "security/no-prompt-injection": "error",
    "security/no-credential-access": "error",
    "security/reverse-shell": "error",
    "security/obfuscation": "error",
    # Command rules
    "command/no-prompt-injection": "error",
    "command/no-credential-access": "error",
    "command/reverse-shell": "error",
    "command/obfuscation": "error",
    # CLAUDE.md rules
    "claude-md/exists": "warning",
    # Agent rules
    "agent/description-required": "error",
    "agent/referenced-skills-exist": "error",
    "agent/disallowed-tools-parseable": "warning",
    "agent/constraint-body-match": "warning",
    "agent/no-prompt-injection": "error",
    "agent/no-credential-access": "error",
    "agent/reverse-shell": "error",
    "agent/obfuscation": "error",
}

STRICT: dict[str, str] = {
    **RECOMMENDED,
    "frontmatter/description-quality": "error",
    "frontmatter/format-valid": "error",
    "content/token-budget": "error",
    "claude-md/exists": "error",
    "agent/disallowed-tools-parseable": "error",
    "agent/constraint-body-match": "error",
}

SECURITY: dict[str, str] = {
    "structural/skill-md-exists": "off",
    "frontmatter/description-required": "off",
    "frontmatter/description-quality": "off",
    "frontmatter/format-valid": "off",
    "content/token-budget": "off",
    "content/broken-references": "off",
    "content/duplicate-detection": "off",
    "security/no-prompt-injection": "error",
    "security/no-credential-access": "error",
    "security/reverse-shell": "error",
    # Command security rules
    "command/no-prompt-injection": "error",
    "command/no-credential-access": "error",
    "command/reverse-shell": "error",
    "command/obfuscation": "error",
    # CLAUDE.md rules
    "claude-md/exists": "off",
    # Agent rules
    "agent/description-required": "off",
    "agent/referenced-skills-exist": "off",
    "agent/disallowed-tools-parseable": "off",
    "agent/constraint-body-match": "off",
    "agent/no-prompt-injection": "error",
    "agent/no-credential-access": "error",
    "agent/reverse-shell": "error",
    "agent/obfuscation": "error",
}

PRE_WORKFLOW: dict[str, str] = {
    "structural/skill-md-exists": "off",
    "frontmatter/description-required": "off",
    "frontmatter/description-quality": "off",
    "frontmatter/format-valid": "off",
    "content/token-budget": "off",
    "content/broken-references": "error",
    "content/duplicate-detection": "off",
    "security/no-prompt-injection": "error",
    "security/no-credential-access": "error",
    "command/description-required": "off",
    "command/script-exists": "off",
    "command/skill-overlap": "off",
    "command/duplicate-detection": "off",
    "command/shadows-builtin": "off",
    "command/no-prompt-injection": "error",
    "command/no-credential-access": "error",
    "command/reverse-shell": "error",
    "claude-md/exists": "off",
    "claude-md/skill-duplication": "off",
    "claude-md/generic-advice": "off",
    "hooks/valid-structure": "error",
    "agent/description-required": "off",
    "agent/referenced-skills-exist": "error",
    "agent/disallowed-tools-parseable": "off",
    "agent/constraint-body-match": "off",
    "agent/no-prompt-injection": "error",
    "agent/no-credential-access": "error",
    "agent/reverse-shell": "error",
    "agent/obfuscation": "error",
}

PRESETS: dict[str, dict[str, str]] = {
    "recommended": RECOMMENDED,
    "strict": STRICT,
    "security": SECURITY,
    "pre-workflow": PRE_WORKFLOW,
}

__all__ = ["PRESETS", "RECOMMENDED", "STRICT", "SECURITY", "PRE_WORKFLOW"]
