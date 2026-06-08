from __future__ import annotations

from harness_eval_lab.inspection.registry import register_rule


def register_all_rules() -> None:
    """Import and register all built-in rules."""
    # Skill rules
    from harness_eval_lab.inspection.rules.agents.constraint_body_match import ConstraintBodyMatch

    # Agent rules
    from harness_eval_lab.inspection.rules.agents.description_required import (
        AgentDescriptionRequired,
    )
    from harness_eval_lab.inspection.rules.agents.disallowed_tools_parseable import (
        DisallowedToolsParseable,
    )
    from harness_eval_lab.inspection.rules.agents.no_credential_access import (
        AgentNoCredentialAccess,
    )
    from harness_eval_lab.inspection.rules.agents.no_prompt_injection import AgentNoPromptInjection
    from harness_eval_lab.inspection.rules.agents.referenced_skills_exist import (
        ReferencedSkillsExist,
    )
    from harness_eval_lab.inspection.rules.agents.reverse_shell_detection import (
        AgentReverseShellDetection,
    )

    # CLAUDE.md rules
    from harness_eval_lab.inspection.rules.claude_md.exists import ClaudeMdExists
    from harness_eval_lab.inspection.rules.claude_md.generic_advice import ClaudeMdGenericAdvice
    from harness_eval_lab.inspection.rules.claude_md.skill_duplication import (
        ClaudeMdSkillDuplication,
    )

    # Command rules
    from harness_eval_lab.inspection.rules.commands.description_required import (
        CommandDescriptionRequired,
    )
    from harness_eval_lab.inspection.rules.commands.duplicate_detection import (
        CommandDuplicateDetection,
    )
    from harness_eval_lab.inspection.rules.commands.no_credential_access import (
        CommandNoCredentialAccess,
    )
    from harness_eval_lab.inspection.rules.commands.no_prompt_injection import (
        CommandNoPromptInjection,
    )
    from harness_eval_lab.inspection.rules.commands.reverse_shell_detection import (
        CommandReverseShellDetection,
    )
    from harness_eval_lab.inspection.rules.commands.script_exists import CommandScriptExists
    from harness_eval_lab.inspection.rules.commands.shadows_builtin import CommandShadowsBuiltin
    from harness_eval_lab.inspection.rules.commands.skill_overlap import CommandSkillOverlap
    from harness_eval_lab.inspection.rules.content.broken_references import BrokenReferences
    from harness_eval_lab.inspection.rules.content.duplicate_detection import DuplicateDetection
    from harness_eval_lab.inspection.rules.content.token_budget import TokenBudget
    from harness_eval_lab.inspection.rules.frontmatter.description_quality import DescriptionQuality
    from harness_eval_lab.inspection.rules.frontmatter.description_required import (
        DescriptionRequired,
    )
    from harness_eval_lab.inspection.rules.frontmatter.format_valid import FormatValid

    # Hooks rules
    from harness_eval_lab.inspection.rules.hooks.valid_structure import HooksValidStructure
    from harness_eval_lab.inspection.rules.security.no_credential_access import NoCredentialAccess
    from harness_eval_lab.inspection.rules.security.no_prompt_injection import NoPromptInjection
    from harness_eval_lab.inspection.rules.security.reverse_shell_detection import (
        ReverseShellDetection,
    )
    from harness_eval_lab.inspection.rules.structural.skill_md_exists import SkillMdExists

    for rule_cls in [
        SkillMdExists,
        DescriptionRequired,
        DescriptionQuality,
        FormatValid,
        TokenBudget,
        BrokenReferences,
        DuplicateDetection,
        NoPromptInjection,
        NoCredentialAccess,
        ReverseShellDetection,
        CommandDescriptionRequired,
        CommandScriptExists,
        CommandNoPromptInjection,
        CommandNoCredentialAccess,
        CommandReverseShellDetection,
        CommandSkillOverlap,
        CommandShadowsBuiltin,
        CommandDuplicateDetection,
        ClaudeMdExists,
        ClaudeMdSkillDuplication,
        ClaudeMdGenericAdvice,
        HooksValidStructure,
        AgentDescriptionRequired,
        ReferencedSkillsExist,
        DisallowedToolsParseable,
        ConstraintBodyMatch,
        AgentNoPromptInjection,
        AgentNoCredentialAccess,
        AgentReverseShellDetection,
    ]:
        register_rule(rule_cls())
