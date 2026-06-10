from __future__ import annotations

import re
from pathlib import Path

from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_FILE_REF_PATTERNS = [
    re.compile(r"\[.*?\]\(([^)]+)\)"),  # markdown links [text](path)
    re.compile(r"`([^`]+\.\w{1,5})`"),  # inline code with extension `file.py`
    re.compile(r"(?:scripts|references|assets)/[\w./-]+"),  # directory references
]


class BrokenReferences:
    meta: RuleMeta = RuleMeta(
        id="content/broken-references",
        default_severity=Severity.ERROR,
        fixable=False,
        description="File references in skill content must point to existing files",
        category=RuleCategory.CONTENT,
        messages={
            "broken_ref": "Referenced file '{{ref}}' does not exist",
        },
    )

    def create(self, context: RuleContext) -> None:
        skill = context.skill
        if not skill.body:
            return

        skill_dir = Path(skill.dir_path)
        lines = skill.body.split("\n")
        checked: set[str] = set()

        for i, line in enumerate(lines):
            for pattern in _FILE_REF_PATTERNS:
                for match in pattern.finditer(line):
                    ref = match.group(1) if match.lastindex else match.group(0)
                    ref = ref.strip()

                    if ref.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    if ref in checked:
                        continue
                    checked.add(ref)

                    ref_path = skill_dir / ref
                    if not ref_path.exists():
                        context.report(
                            ReportDescriptor(
                                message_id="broken_ref",
                                data={"ref": ref},
                                location=Location(
                                    file=skill.skill_md_path,
                                    start_line=skill.body_start_line + i,
                                ),
                            )
                        )
