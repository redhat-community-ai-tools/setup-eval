from __future__ import annotations

import re

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_GENERIC_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("write clean code", re.compile(r"write\s+clean[\s,]+readable\s+code", re.I)),
    ("be helpful", re.compile(r"be\s+helpful\s+and\s+thorough", re.I)),
    ("follow best practices", re.compile(r"follow\s+(the\s+)?best\s+practices", re.I)),
    ("think step by step", re.compile(r"think\s+step\s+by\s+step", re.I)),
    ("consider edge cases", re.compile(r"consider\s+(all\s+)?edge\s+cases", re.I)),
    (
        "handle errors properly",
        re.compile(r"handle\s+errors\s+(?:properly|correctly|gracefully)", re.I),
    ),
    ("use proper formatting", re.compile(r"use\s+proper\s+formatting", re.I)),
    ("write maintainable code", re.compile(r"write\s+maintainable\s+code", re.I)),
    ("be concise", re.compile(r"be\s+concise\s+and\s+clear", re.I)),
    ("ensure code quality", re.compile(r"ensure\s+(?:code\s+)?quality", re.I)),
    ("write well-documented code", re.compile(r"write\s+well[- ]documented\s+code", re.I)),
    ("be thorough", re.compile(r"be\s+thorough\s+(?:in|and|with)", re.I)),
]


class ClaudeMdGenericAdvice:
    meta = RuleMeta(
        id="claude-md/generic-advice",
        default_severity=Severity.WARNING,
        fixable=False,
        description="CLAUDE.md should not contain generic advice Claude already follows by default",
        category=RuleCategory.CONTENT,
        messages={
            "generic": "Line {{line}}: '{{label}}' — Claude does this by default. This instruction wastes tokens every session.",
        },
        target_type=ComponentType.CLAUDE_MD,
        tools=("claude",),
    )

    def create(self, context: RuleContext) -> None:
        claude_md = context.claude_md
        if claude_md is None or not claude_md.raw_content:
            return

        lines = claude_md.raw_content.split("\n")
        in_code_fence = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue

            if in_code_fence:
                continue

            for label, pattern in _GENERIC_PATTERNS:
                if pattern.search(line):
                    context.report(
                        ReportDescriptor(
                            message_id="generic",
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=claude_md.file_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break
