from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security.reverse_shell_detection import (
    _REVERSE_SHELL_PATTERNS,
)
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class CommandReverseShellDetection:
    meta: RuleMeta = RuleMeta(
        id="command/reverse-shell",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Command definition should not contain reverse shell patterns",
        category=RuleCategory.SECURITY,
        messages={
            "shell_detected": "Line {{line}} contains a reverse shell pattern ('{{label}}'). This is a critical security risk.",
        },
        target_type=ComponentType.COMMAND,
    )

    def create(self, context: RuleContext) -> None:
        cmd = context.command
        if not cmd or not cmd.raw_content:
            return

        lines = cmd.raw_content.split("\n")

        for i, line in enumerate(lines):
            for label, pattern in _REVERSE_SHELL_PATTERNS:
                if pattern.search(line):
                    context.report(ReportDescriptor(
                        message_id="shell_detected",
                        data={"label": label, "line": str(i + 1)},
                        location=Location(
                            file=cmd.command_md_path, start_line=i + 1,
                        ),
                    ))
                    break
