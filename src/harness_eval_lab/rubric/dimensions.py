"""Issue category definitions per component type."""

from __future__ import annotations

from harness_eval_lab.rubric.types import IssueCategory

SKILL_CATEGORIES = [
    IssueCategory(
        name="specificity",
        description="Flag if instructions are vague platitudes with no actionable patterns. Look for generic advice like 'write clean code' vs specific rules like 'always use raise from'.",
    ),
    IssueCategory(
        name="redundancy",
        description="Flag if instructions duplicate Claude's default behavior (e.g., 'be helpful', 'handle errors properly', 'think step by step'). Test: if this skill were deleted, would Claude behave differently?",
    ),
    IssueCategory(
        name="trigger_quality",
        description="Flag if the description is missing, too broad, too narrow, uses coercive language (MUST, ALWAYS), or lacks activation context ('use when' phrasing).",
    ),
    IssueCategory(
        name="token_efficiency",
        description="Flag if SKILL.md is over 3000 tokens with low value density, or if detailed procedures should be split into reference files.",
    ),
    IssueCategory(
        name="content_quality",
        description="Flag if there is no structure, no examples, broken file references, or missing edge case handling.",
    ),
]

COMMAND_CATEGORIES = [
    IssueCategory(
        name="description_quality",
        description="Flag if the description is missing, too vague, or doesn't clearly say what the command does.",
    ),
    IssueCategory(
        name="instruction_clarity",
        description="Flag if instructions are ambiguous or Claude wouldn't know what to do or in what order.",
    ),
    IssueCategory(
        name="script_integrity",
        description="Flag if referenced scripts don't exist or the discovery pattern is broken.",
    ),
    IssueCategory(
        name="scope",
        description="Flag if this should be a skill (auto-triggered) instead of a command (user-triggered), or vice versa.",
    ),
    IssueCategory(
        name="token_efficiency",
        description="Flag if the command is bloated. Under 15KB is fine; 15-30KB should be split; over 30KB must be split.",
    ),
    IssueCategory(
        name="redundancy",
        description="Flag if Claude already does this without the command. Built-in capabilities include plan mode, commit messages, code explanation, and code review.",
    ),
    IssueCategory(
        name="robustness",
        description="Flag if the command hardcodes assumptions or doesn't handle missing dependencies.",
    ),
]

CLAUDE_MD_CATEGORIES = [
    IssueCategory(
        name="conciseness",
        description="Flag lines that could be removed without causing Claude to make mistakes. Ruthlessly prune.",
    ),
    IssueCategory(
        name="signal_to_noise",
        description="Flag generic advice Claude already follows ('write clean code', 'be helpful', 'follow best practices'). Also flag standard language conventions (use linters instead) and detailed API docs (link instead).",
    ),
    IssueCategory(
        name="skill_separation",
        description="Flag domain-specific rules that only matter sometimes. These waste context every session and should be skills instead.",
    ),
    IssueCategory(
        name="structure",
        description="Flag if sections are unclear, critical rules aren't marked, or the document isn't scannable.",
    ),
    IssueCategory(
        name="conflict_free",
        description="Flag contradictions with any skill, command, or other configuration.",
    ),
]

AGENT_CATEGORIES = [
    IssueCategory(
        name="specificity",
        description="Flag if phases have vague steps like 'implement the fix' with no concrete procedure.",
    ),
    IssueCategory(
        name="constraint_clarity",
        description="Flag if constraints are missing, or if body constraints aren't backed by disallowedTools entries.",
    ),
    IssueCategory(
        name="zero_trust_integrity",
        description="Flag if external inputs (issue text, PR descriptions) are blindly trusted without verification steps.",
    ),
    IssueCategory(
        name="token_efficiency",
        description="Flag if over 5000 tokens with low value density, or if procedures should be delegated to skills.",
    ),
    IssueCategory(
        name="content_quality",
        description="Flag if missing key sections (identity, constraints, procedure, output format, failure handling).",
    ),
]

HOOKS_CATEGORIES = [
    IssueCategory(
        name="safety",
        description="Flag dangerous patterns (rm -rf, force push, curl|bash) or destructive state modifications.",
    ),
    IssueCategory(
        name="reliability",
        description="Flag if referenced scripts don't exist or commands are malformed.",
    ),
    IssueCategory(
        name="scope",
        description="Flag if the hook is over-broad or if the behavior is advisory (should be CLAUDE.md/skill instead).",
    ),
    IssueCategory(
        name="performance", description="Flag if the hook is slow or blocks unnecessarily."
    ),
]

CATEGORIES_BY_TYPE: dict[str, list[IssueCategory]] = {
    "skill": SKILL_CATEGORIES,
    "command": COMMAND_CATEGORIES,
    "claude_md": CLAUDE_MD_CATEGORIES,
    "agent": AGENT_CATEGORIES,
    "hooks": HOOKS_CATEGORIES,
}
