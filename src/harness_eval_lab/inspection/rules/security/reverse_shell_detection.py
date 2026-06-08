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

_REVERSE_SHELL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bash reverse shell", re.compile(r"bash\s+-i\s+>&\s*/dev/tcp/", re.I)),
    ("netcat exec", re.compile(r"\bnc\s+.*-e\s+/bin/", re.I)),
    ("ncat exec", re.compile(r"\bncat\s+.*--exec", re.I)),
    ("python socket shell", re.compile(r"python[23]?\s+-c\s+.*(?:socket|subprocess)", re.I)),
    ("perl socket shell", re.compile(r"perl\s+-e\s+.*(?:socket|Socket)", re.I)),
    ("ruby socket shell", re.compile(r"ruby\s+-rsocket\s+-e", re.I)),
    ("php socket shell", re.compile(r"php\s+-r\s+.*fsockopen", re.I)),
    ("socat exec", re.compile(r"\bsocat\s+.*exec:", re.I)),
    ("named pipe shell", re.compile(r"\bmknod\s+.*\bp\b.*(?:/bin/sh|bash)", re.I)),
    ("powershell reverse shell", re.compile(r"\bpowershell\s+.*(?:Net\.Sockets|TCPClient)", re.I)),
]


class ReverseShellDetection:
    meta: RuleMeta = RuleMeta(
        id="security/reverse-shell",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Skill content should not contain reverse shell patterns",
        category=RuleCategory.SECURITY,
        messages={
            "shell_detected": "Line {{line}} contains a reverse shell pattern ('{{label}}'). This is a critical security risk.",
            "shell_in_code_block": "Line {{line}} contains '{{label}}' inside a code block — likely documentation, but verify.",
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

            for label, pattern in _REVERSE_SHELL_PATTERNS:
                if pattern.search(line):
                    if in_code_fence:
                        message_id = "shell_in_code_block"
                        severity_override = Severity.WARNING
                    else:
                        message_id = "shell_detected"
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
