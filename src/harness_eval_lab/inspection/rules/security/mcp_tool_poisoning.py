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

_HIDDEN_INSTRUCTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("HTML comment with instruction", re.compile(r"<!--\s*(?:system|instruction|ignore|override|you\s+are)", re.I)),
    ("markdown comment", re.compile(r"\[//\]:\s*#\s*\(.*(?:ignore|override|instruction)", re.I)),
    ("base64 blob in text", re.compile(r"(?:data:text/[^;]+;base64,|[A-Za-z0-9+/]{40,}={0,2})")),
    ("data URI with script", re.compile(r"data:\s*(?:text/javascript|application/javascript|text/html)", re.I)),
]

_ZERO_WIDTH_CHARS = {
    "​": "zero-width space",
    "‌": "zero-width non-joiner",
    "‍": "zero-width joiner",
    "⁠": "word joiner",
    "﻿": "BOM / zero-width no-break space",
    "­": "soft hyphen",
}

_RTL_OVERRIDE_CHARS = {
    "‪": "LRE",
    "‫": "RLE",
    "‬": "PDF",
    "‭": "LRO",
    "‮": "RLO",
    "⁦": "LRI",
    "⁧": "RLI",
    "⁨": "FSI",
    "⁩": "PDI",
}

_HOMOGLYPH_MAP: dict[str, str] = {
    "А": "A (Cyrillic)",
    "В": "B (Cyrillic)",
    "С": "C (Cyrillic)",
    "Е": "E (Cyrillic)",
    "Н": "H (Cyrillic)",
    "К": "K (Cyrillic)",
    "М": "M (Cyrillic)",
    "О": "O (Cyrillic)",
    "Р": "P (Cyrillic)",
    "Т": "T (Cyrillic)",
    "Х": "X (Cyrillic)",
    "а": "a (Cyrillic)",
    "е": "e (Cyrillic)",
    "о": "o (Cyrillic)",
    "р": "p (Cyrillic)",
    "с": "c (Cyrillic)",
    "у": "y (Cyrillic)",
    "х": "x (Cyrillic)",
    "Α": "A (Greek)",
    "Β": "B (Greek)",
    "Ε": "E (Greek)",
    "Η": "H (Greek)",
    "Κ": "K (Greek)",
    "Μ": "M (Greek)",
    "Ο": "O (Greek)",
    "Ρ": "P (Greek)",
    "Τ": "T (Greek)",
    "Χ": "X (Greek)",
    "ο": "o (Greek)",
}


class McpToolPoisoning:
    meta: RuleMeta = RuleMeta(
        id="security/mcp-tool-poisoning",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Detect hidden instructions, Unicode deception, and suspicious embedded content",
        category=RuleCategory.SECURITY,
        messages={
            "mcp_hidden_instruction": "Line {{line}}: {{label}}. Hidden instructions can manipulate agent behavior.",
            "mcp_unicode_deception": "Line {{line}}: contains {{label}} (U+{{codepoint}}). Unicode deception can disguise malicious content as benign.",
            "mcp_suspicious_default": "Line {{line}}: {{label}}. Suspicious content pattern detected.",
        },
    )

    def create(self, context: RuleContext) -> None:
        skill = context.skill
        if not skill.raw_content:
            return

        lines = skill.raw_content.split("\n")

        for i, line in enumerate(lines):
            for label, pattern in _HIDDEN_INSTRUCTION_PATTERNS:
                if pattern.search(line):
                    context.report(
                        ReportDescriptor(
                            message_id="mcp_hidden_instruction",
                            data={"label": label, "line": str(i + 1)},
                            location=Location(
                                file=skill.skill_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break

            for char, char_name in _ZERO_WIDTH_CHARS.items():
                if char in line:
                    context.report(
                        ReportDescriptor(
                            message_id="mcp_unicode_deception",
                            data={
                                "label": char_name,
                                "codepoint": f"{ord(char):04X}",
                                "line": str(i + 1),
                            },
                            location=Location(
                                file=skill.skill_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )

            for char, char_name in _RTL_OVERRIDE_CHARS.items():
                if char in line:
                    context.report(
                        ReportDescriptor(
                            message_id="mcp_unicode_deception",
                            data={
                                "label": f"RTL override ({char_name})",
                                "codepoint": f"{ord(char):04X}",
                                "line": str(i + 1),
                            },
                            location=Location(
                                file=skill.skill_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )

            for char, char_name in _HOMOGLYPH_MAP.items():
                if char in line:
                    context.report(
                        ReportDescriptor(
                            message_id="mcp_unicode_deception",
                            data={
                                "label": f"homoglyph: looks like {char_name}",
                                "codepoint": f"{ord(char):04X}",
                                "line": str(i + 1),
                            },
                            location=Location(
                                file=skill.skill_md_path,
                                start_line=i + 1,
                            ),
                            severity_override=Severity.WARNING,
                        )
                    )
