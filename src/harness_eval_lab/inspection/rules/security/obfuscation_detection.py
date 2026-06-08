from __future__ import annotations

import re

from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_OBFUSCATION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("eval with decode", re.compile(r"eval\s*\(\s*(?:atob|Buffer\.from|base64\.b64decode)\s*\(", re.I)),
    ("char code construction", re.compile(r"String\.fromCharCode\s*\(", re.I)),
    ("hex escape sequence", re.compile(r"(?:\\x[0-9a-fA-F]{2}){4,}")),
    ("unicode escape sequence", re.compile(r"(?:\\u[0-9a-fA-F]{4}){4,}")),
    ("zero-width characters", re.compile(r"[​-‏﻿]")),
    ("tag characters", re.compile(r"[\U000e0000-\U000e007f]")),
    ("python dynamic exec", re.compile(r"exec\s*\(\s*(?:compile|__import__)\s*\(", re.I)),
    ("char code round-trip", re.compile(r"charCodeAt\b.*\bfromCharCode\b", re.I)),
]


class ObfuscationDetection:
    meta: RuleMeta = RuleMeta(
        id="security/obfuscation",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Skill content should not contain code obfuscation patterns",
        category=RuleCategory.SECURITY,
        messages={
            "obfuscation_detected": "Line {{line}} contains an obfuscation pattern ('{{label}}'). This may hide malicious behavior.",
            "obfuscation_in_code_block": "Line {{line}} contains '{{label}}' inside a code block — likely documentation, but verify.",
        },
    )

    def create(self, context: RuleContext) -> None:
        skill = context.skill
        if not skill.raw_content:
            return

        lines = skill.raw_content.split("\n")
        in_code_fence = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue

            for label, pattern in _OBFUSCATION_PATTERNS:
                if pattern.search(line):
                    if in_code_fence:
                        message_id = "obfuscation_in_code_block"
                        severity_override = Severity.WARNING
                    else:
                        message_id = "obfuscation_detected"
                        severity_override = None

                    context.report(
                        ReportDescriptor(
                            message_id=message_id,
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=skill.skill_md_path,
                                start_line=i + 1,
                            ),
                            severity_override=severity_override,
                        )
                    )
                    break
