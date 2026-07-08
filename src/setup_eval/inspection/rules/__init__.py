from __future__ import annotations

from setup_eval.inspection.registry import register_rule


def register_all_rules() -> None:
    """Import and register all built-in rules."""
    # Skill rules
    from setup_eval.inspection.rules.agents.constraint_body_match import ConstraintBodyMatch
    from setup_eval.inspection.rules.agents.data_exfiltration import AgentDataExfiltration

    # Agent rules
    from setup_eval.inspection.rules.agents.description_required import (
        AgentDescriptionRequired,
    )
    from setup_eval.inspection.rules.agents.disallowed_tools_parseable import (
        DisallowedToolsParseable,
    )
    from setup_eval.inspection.rules.agents.model_specified import AgentModelSpecified
    from setup_eval.inspection.rules.agents.no_credential_access import (
        AgentNoCredentialAccess,
    )
    from setup_eval.inspection.rules.agents.no_prompt_injection import AgentNoPromptInjection
    from setup_eval.inspection.rules.agents.obfuscation_detection import (
        AgentObfuscationDetection,
    )
    from setup_eval.inspection.rules.agents.referenced_skills_exist import (
        ReferencedSkillsExist,
    )
    from setup_eval.inspection.rules.agents.reverse_shell_detection import (
        AgentReverseShellDetection,
    )

    # CLAUDE.md rules
    from setup_eval.inspection.rules.claude_md.exists import ClaudeMdExists
    from setup_eval.inspection.rules.claude_md.generic_advice import ClaudeMdGenericAdvice
    from setup_eval.inspection.rules.claude_md.skill_duplication import (
        ClaudeMdSkillDuplication,
    )
    from setup_eval.inspection.rules.commands.data_exfiltration import CommandDataExfiltration

    # Command rules
    from setup_eval.inspection.rules.commands.description_required import (
        CommandDescriptionRequired,
    )
    from setup_eval.inspection.rules.commands.duplicate_detection import (
        CommandDuplicateDetection,
    )
    from setup_eval.inspection.rules.commands.no_credential_access import (
        CommandNoCredentialAccess,
    )
    from setup_eval.inspection.rules.commands.no_prompt_injection import (
        CommandNoPromptInjection,
    )
    from setup_eval.inspection.rules.commands.obfuscation_detection import (
        CommandObfuscationDetection,
    )
    from setup_eval.inspection.rules.commands.references_nonexistent_skill import (
        CommandReferencesNonexistentSkill,
    )
    from setup_eval.inspection.rules.commands.reverse_shell_detection import (
        CommandReverseShellDetection,
    )
    from setup_eval.inspection.rules.commands.script_exists import CommandScriptExists
    from setup_eval.inspection.rules.commands.shadows_builtin import CommandShadowsBuiltin
    from setup_eval.inspection.rules.commands.skill_overlap import CommandSkillOverlap
    from setup_eval.inspection.rules.content.broken_references import BrokenReferences
    from setup_eval.inspection.rules.content.circular_references import CircularReferences
    from setup_eval.inspection.rules.content.duplicate_detection import DuplicateDetection
    from setup_eval.inspection.rules.content.token_budget import TokenBudget
    from setup_eval.inspection.rules.frontmatter.description_quality import DescriptionQuality
    from setup_eval.inspection.rules.frontmatter.description_required import (
        DescriptionRequired,
    )
    from setup_eval.inspection.rules.frontmatter.format_valid import FormatValid

    # Hooks rules
    from setup_eval.inspection.rules.hooks.dangerous_command import HooksDangerousCommand
    from setup_eval.inspection.rules.hooks.env_leakage import HooksEnvLeakage
    from setup_eval.inspection.rules.hooks.network_access import HooksNetworkAccess
    from setup_eval.inspection.rules.hooks.script_boundary import HooksScriptBoundary
    from setup_eval.inspection.rules.hooks.valid_structure import HooksValidStructure

    # MCP rules
    from setup_eval.inspection.rules.mcp.duplicate_server import McpDuplicateServer
    from setup_eval.inspection.rules.mcp.no_wildcard_tools import McpNoWildcardTools
    from setup_eval.inspection.rules.mcp.suspicious_endpoint import McpSuspiciousEndpoint
    from setup_eval.inspection.rules.mcp.valid_config import McpValidConfig
    from setup_eval.inspection.rules.quality.example_gap import ExampleGap
    from setup_eval.inspection.rules.quality.imprecise_instruction import ImpreciseInstruction
    from setup_eval.inspection.rules.quality.redundant_guidance import RedundantGuidance
    from setup_eval.inspection.rules.quality.stale_references import StaleReferences
    from setup_eval.inspection.rules.quality.unfinished_content import UnfinishedContent
    from setup_eval.inspection.rules.security.ast_behavioral import AstBehavioral
    from setup_eval.inspection.rules.security.bash_taint_tracking import BashTaintTracking
    from setup_eval.inspection.rules.security.cve_lookup import CveLookup
    from setup_eval.inspection.rules.security.data_exfiltration import DataExfiltration
    from setup_eval.inspection.rules.security.mcp_least_privilege import McpLeastPrivilege
    from setup_eval.inspection.rules.security.mcp_tool_poisoning import McpToolPoisoning
    from setup_eval.inspection.rules.security.no_credential_access import NoCredentialAccess
    from setup_eval.inspection.rules.security.no_prompt_injection import NoPromptInjection
    from setup_eval.inspection.rules.security.obfuscation_detection import (
        ObfuscationDetection,
    )
    from setup_eval.inspection.rules.security.reverse_shell_detection import (
        ReverseShellDetection,
    )
    from setup_eval.inspection.rules.security.taint_tracking import TaintTracking
    from setup_eval.inspection.rules.security.yara_scan import YaraScan
    from setup_eval.inspection.rules.structural.skill_md_exists import SkillMdExists

    for rule_cls in [
        SkillMdExists,
        DescriptionRequired,
        DescriptionQuality,
        FormatValid,
        TokenBudget,
        BrokenReferences,
        CircularReferences,
        DuplicateDetection,
        NoPromptInjection,
        NoCredentialAccess,
        ReverseShellDetection,
        ObfuscationDetection,
        DataExfiltration,
        CommandDescriptionRequired,
        CommandScriptExists,
        CommandNoPromptInjection,
        CommandNoCredentialAccess,
        CommandReverseShellDetection,
        CommandObfuscationDetection,
        CommandDataExfiltration,
        CommandSkillOverlap,
        CommandShadowsBuiltin,
        CommandDuplicateDetection,
        CommandReferencesNonexistentSkill,
        ClaudeMdExists,
        ClaudeMdSkillDuplication,
        ClaudeMdGenericAdvice,
        HooksScriptBoundary,
        HooksValidStructure,
        HooksDangerousCommand,
        HooksEnvLeakage,
        HooksNetworkAccess,
        AgentDescriptionRequired,
        ReferencedSkillsExist,
        DisallowedToolsParseable,
        ConstraintBodyMatch,
        AgentNoPromptInjection,
        AgentNoCredentialAccess,
        AgentReverseShellDetection,
        AgentObfuscationDetection,
        AgentDataExfiltration,
        AgentModelSpecified,
        AstBehavioral,
        TaintTracking,
        BashTaintTracking,
        McpLeastPrivilege,
        McpValidConfig,
        McpDuplicateServer,
        McpSuspiciousEndpoint,
        McpNoWildcardTools,
        McpToolPoisoning,
        YaraScan,
        CveLookup,
        ImpreciseInstruction,
        RedundantGuidance,
        UnfinishedContent,
        ExampleGap,
        StaleReferences,
    ]:
        register_rule(rule_cls())
