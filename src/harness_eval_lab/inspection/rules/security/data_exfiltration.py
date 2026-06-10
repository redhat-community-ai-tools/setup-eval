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

_EXFIL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("curl post file contents", re.compile(r"curl\s+.*-d\s+\"\$\(cat\b", re.I)),
    ("curl with command substitution", re.compile(r"curl\s+.*--data.*\$\(", re.I)),
    ("wget post data", re.compile(r"wget\s+--post-data", re.I)),
    ("dns tunneling dig", re.compile(r"\bdig\s+.*\bTXT\b", re.I)),
    ("dns tunneling nslookup", re.compile(r"\bnslookup\s+.*-type=TXT", re.I)),
    (
        "webhook exfiltration",
        re.compile(r"(?:curl|wget|fetch)\s+.*(?:webhook|hooks\.|pipedream|requestbin|ngrok)", re.I),
    ),
    ("base64 pipe to network", re.compile(r"base64\s+.*\|\s*(?:curl|wget|nc)\b", re.I)),
    ("archive pipe to network", re.compile(r"tar\s+.*\|\s*(?:curl|wget|nc|ssh)\b", re.I)),
]


class DataExfiltration:
    meta: RuleMeta = RuleMeta(
        id="security/data-exfiltration",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Skill content should not contain data exfiltration patterns",
        category=RuleCategory.SECURITY,
        messages={
            "exfil_detected": "Line {{line}} contains a data exfiltration pattern ('{{label}}'). This is a critical security risk.",
            "exfil_in_code_block": "Line {{line}} contains '{{label}}' inside a code block — likely documentation, but verify.",
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

            for label, pattern in _EXFIL_PATTERNS:
                if pattern.search(line):
                    if in_code_fence:
                        message_id = "exfil_in_code_block"
                        severity_override = Severity.WARNING
                    else:
                        message_id = "exfil_detected"
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
