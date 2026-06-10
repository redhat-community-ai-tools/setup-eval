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


class AgentDataExfiltration:
    meta: RuleMeta = RuleMeta(
        id="agent/data-exfiltration",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Agent definition should not contain data exfiltration patterns",
        category=RuleCategory.SECURITY,
        messages={
            "exfil_detected": "Line {{line}} contains a data exfiltration pattern ('{{label}}'). This is a critical security risk.",
        },
        target_type=ComponentType.AGENT,
    )

    def create(self, context: RuleContext) -> None:
        agent = context.agent
        if not agent or not agent.raw_content:
            return

        lines = agent.raw_content.split("\n")

        for i, line in enumerate(lines):
            for label, pattern in _EXFIL_PATTERNS:
                if pattern.search(line):
                    context.report(
                        ReportDescriptor(
                            message_id="exfil_detected",
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=agent.agent_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break
