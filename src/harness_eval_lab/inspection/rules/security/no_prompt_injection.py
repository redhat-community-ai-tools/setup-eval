from __future__ import annotations

import re

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security._shared import (
    extract_content_and_path,
    scan_lines_for_patterns,
)
from harness_eval_lab.inspection.types import (
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_INJECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "ignore previous instructions",
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    ),
    ("disregard prior", re.compile(r"disregard\s+(all\s+)?(prior|previous|above)", re.I)),
    ("you are now", re.compile(r"you\s+are\s+now\s+(?:a|an|the)\s+", re.I)),
    ("system prompt override", re.compile(r"system\s*prompt\s*(override|injection|change)", re.I)),
    (
        "override instructions",
        re.compile(r"override\s+(all\s+)?(instructions|rules|guidelines)", re.I),
    ),
    ("new instructions", re.compile(r"new\s+instructions?\s*:", re.I)),
    ("jailbreak attempt", re.compile(r"(do\s+anything\s+now|developer\s+mode)", re.I)),
    (
        "prompt leak",
        re.compile(r"(reveal|show|print|output)\s+(your|the)\s+(system\s+)?prompt", re.I),
    ),
    ("role hijack", re.compile(r"forget\s+(everything|all|your)\s+(you|instructions|rules)", re.I)),
    ("hidden instruction", re.compile(r"<\s*(?:system|instruction|hidden)\s*>", re.I)),
    ("role play", re.compile(r"pretend\s+(?:to\s+be|you\s+are)\s+(?:a|an|the)\s+", re.I)),
    (
        "encoding evasion",
        re.compile(r"(?:in\s+base64|encode\s+(?:as|in|to)\s+base64|base64\s+encod)", re.I),
    ),
    ("repeat after me", re.compile(r"repeat\s+after\s+me", re.I)),
    (
        "bypass safety",
        re.compile(r"(?:ignore\s+safety|bypass\s+(?:filter|safety|restriction))", re.I),
    ),
    ("output control", re.compile(r"output\s+the\s+following\s+exactly", re.I)),
    ("markdown image exfiltration", re.compile(r"!\[.*?\]\(https?://", re.I)),
    (
        "translate evasion",
        re.compile(r"translate\s+(?:this|the\s+following)\s+(?:to|into)\s+", re.I),
    ),
]


class NoPromptInjection:
    meta: RuleMeta = RuleMeta(
        id="security/no-prompt-injection",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Skill content should not contain prompt injection patterns",
        category=RuleCategory.SECURITY,
        messages={
            "injection_detected": "Line {{line}} contains a word pattern ('{{label}}') that could be used to manipulate the AI assistant. Check if this is intentional content or an actual risk.",
            "injection_in_code_block": "Line {{line}} contains '{{label}}' inside a code block — likely safe (documentation or example).",
            "injection_in_example": "Line {{line}} contains '{{label}}' in a quote or example — likely safe.",
        },
    )

    def create(self, context: RuleContext) -> None:
        result = extract_content_and_path(context, ComponentType.SKILL)
        if result is None:
            return
        content, file_path = result
        scan_lines_for_patterns(
            content,
            file_path,
            context,
            _INJECTION_PATTERNS,
            detected_msg="injection_detected",
            code_block_msg="injection_in_code_block",
            example_msg="injection_in_example",
        )
