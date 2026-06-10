from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security.no_prompt_injection import _INJECTION_PATTERNS
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class AgentNoPromptInjection:
    meta: RuleMeta = RuleMeta(
        id="agent/no-prompt-injection",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Agent definition should not contain prompt injection patterns",
        category=RuleCategory.SECURITY,
        messages={
            "injection_detected": "Line {{line}} contains a word pattern ('{{label}}') that could be used to manipulate Claude. Check if this is intentional content or an actual risk.",
            "injection_in_code_block": "Line {{line}} contains '{{label}}' inside a code block — likely safe (documentation or example).",
            "injection_in_example": "Line {{line}} contains '{{label}}' in a quote or example — likely safe.",
        },
        target_type=ComponentType.AGENT,
    )

    def create(self, context: RuleContext) -> None:
        agent = context.agent
        if not agent or not agent.raw_content:
            return

        lines = agent.raw_content.split("\n")
        in_code_fence = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue

            for label, pattern in _INJECTION_PATTERNS:
                if pattern.search(line):
                    is_quoted = stripped.startswith(">") or stripped.startswith('"')
                    is_example = any(
                        w in line.lower() for w in ["for example", "e.g.", "such as", "like:"]
                    )

                    if in_code_fence:
                        message_id = "injection_in_code_block"
                        severity_override = Severity.WARNING
                    elif is_quoted or is_example:
                        message_id = "injection_in_example"
                        severity_override = Severity.WARNING
                    else:
                        message_id = "injection_detected"
                        severity_override = None

                    context.report(
                        ReportDescriptor(
                            message_id=message_id,
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=agent.agent_md_path,
                                start_line=i + 1,
                            ),
                            severity_override=severity_override,
                        )
                    )
                    break
