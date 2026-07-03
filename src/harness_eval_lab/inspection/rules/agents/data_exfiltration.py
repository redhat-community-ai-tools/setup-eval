from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security._shared import (
    extract_content_and_path,
    scan_lines_for_patterns,
)
from harness_eval_lab.inspection.rules.security.data_exfiltration import _EXFIL_PATTERNS
from harness_eval_lab.inspection.types import (
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
        result = extract_content_and_path(context, ComponentType.AGENT)
        if result is None:
            return
        content, file_path = result
        scan_lines_for_patterns(
            content,
            file_path,
            context,
            _EXFIL_PATTERNS,
            detected_msg="exfil_detected",
        )
