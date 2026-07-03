from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security._shared import (
    extract_content_and_path,
    scan_lines_for_patterns,
)
from harness_eval_lab.inspection.rules.security.obfuscation_detection import _OBFUSCATION_PATTERNS
from harness_eval_lab.inspection.types import (
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class CommandObfuscationDetection:
    meta: RuleMeta = RuleMeta(
        id="command/obfuscation",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Command definition should not contain code obfuscation patterns",
        category=RuleCategory.SECURITY,
        messages={
            "obfuscation_detected": "Line {{line}} contains an obfuscation pattern ('{{label}}'). This may hide malicious behavior.",
        },
        target_type=ComponentType.COMMAND,
    )

    def create(self, context: RuleContext) -> None:
        result = extract_content_and_path(context, ComponentType.COMMAND)
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
