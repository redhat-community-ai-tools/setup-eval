from __future__ import annotations

from setup_eval.core.types import ComponentType
from setup_eval.inspection.rules.security._shared import (
    extract_content_and_path,
    scan_lines_for_patterns,
)
from setup_eval.inspection.rules.security.obfuscation_detection import _OBFUSCATION_PATTERNS
from setup_eval.inspection.types import (
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
        result = extract_content_and_path(context, ComponentType.AGENT)
        if result is None:
            return
        content, file_path = result
        scan_lines_for_patterns(
            content,
            file_path,
            context,
            _OBFUSCATION_PATTERNS,
            detected_msg="obfuscation_detected",
        )
