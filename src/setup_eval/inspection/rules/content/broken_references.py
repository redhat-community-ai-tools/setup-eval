from __future__ import annotations

import re
from pathlib import Path

from setup_eval.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)
from setup_eval.utils.paths import safe_join

_FILE_REF_PATTERNS = [
    re.compile(r"\[.*?\]\(([^)]+)\)"),  # markdown links [text](path)
    re.compile(r"`([^`]+\.\w{1,5})`"),  # inline code with extension `file.py`
    re.compile(r"(?:scripts|references|assets)/[\w./-]+"),  # directory references
]

_VERSION_RE = re.compile(r"^\d+(\.\d+)+$")
_GIT_REF_RE = re.compile(r"(\.\.\.?|@\{|HEAD|upstream|origin|main|master)")
_TEMPLATE_VAR_RE = re.compile(r"\$\{|<[a-z_-]+>|\{\{")
_GLOB_RE = re.compile(r"[*?]")
_COMMAND_RE = re.compile(r"^(git|bash|uv|npm|curl|grep|tail|mv|cat|echo|find|sed|awk)\s")


def _is_not_a_file_ref(ref: str) -> bool:
    if _VERSION_RE.match(ref):
        return True
    if _GIT_REF_RE.search(ref):
        return True
    if _TEMPLATE_VAR_RE.search(ref):
        return True
    if _GLOB_RE.search(ref):
        return True
    if _COMMAND_RE.match(ref):
        return True
    if " " in ref and not ref.startswith(("scripts/", "references/", "assets/")):
        return True
    return ref.startswith("~")


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
                    if _is_not_a_file_ref(ref):
                        continue
                    if ref in checked:
                        continue
                    checked.add(ref)

                    ref_path = safe_join(skill_dir, ref)
                    if ref_path is None or not ref_path.exists():
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
