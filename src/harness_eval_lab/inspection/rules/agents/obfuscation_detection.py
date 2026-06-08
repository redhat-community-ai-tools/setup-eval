from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security.obfuscation_detection import _OBFUSCATION_PATTERNS
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class AgentObfuscationDetection:
    meta: RuleMeta = RuleMeta(
        id="agent/obfuscation",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Agent definition should not contain code obfuscation patterns",
        category=RuleCategory.SECURITY,
        messages={
            "obfuscation_detected": "Line {{line}} contains an obfuscation pattern ('{{label}}'). This may hide malicious behavior.",
        },
        target_type=ComponentType.AGENT,
    )

    def create(self, context: RuleContext) -> None:
        agent = context.agent
        if not agent or not agent.raw_content:
            return

        lines = agent.raw_content.split("\n")

        for i, line in enumerate(lines):
            for label, pattern in _OBFUSCATION_PATTERNS:
                if pattern.search(line):
                    context.report(ReportDescriptor(
                        message_id="obfuscation_detected",
                        data={"label": label, "line": str(i + 1)},
                        location=Location(
                            file=agent.agent_md_path, start_line=i + 1,
                        ),
                    ))
                    break
