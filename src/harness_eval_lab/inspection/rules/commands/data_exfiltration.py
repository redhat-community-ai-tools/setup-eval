from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security.data_exfiltration import _EXFIL_PATTERNS
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class CommandDataExfiltration:
    meta: RuleMeta = RuleMeta(
        id="command/data-exfiltration",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Command definition should not contain data exfiltration patterns",
        category=RuleCategory.SECURITY,
        messages={
            "exfil_detected": "Line {{line}} contains a data exfiltration pattern ('{{label}}'). This is a critical security risk.",
        },
        target_type=ComponentType.COMMAND,
    )

    def create(self, context: RuleContext) -> None:
        cmd = context.command
        if not cmd or not cmd.raw_content:
            return

        lines = cmd.raw_content.split("\n")

        for i, line in enumerate(lines):
            for label, pattern in _EXFIL_PATTERNS:
                if pattern.search(line):
                    context.report(
                        ReportDescriptor(
                            message_id="exfil_detected",
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=cmd.command_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break
