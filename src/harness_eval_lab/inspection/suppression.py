from __future__ import annotations

import re

_FILE_WIDE_RE = re.compile(r"<!--\s*evaluator-ignore:\s*([\w/,\s-]+)\s*-->", re.IGNORECASE)
_NEXT_LINE_RE = re.compile(
    r"<!--\s*evaluator-ignore-next-line:\s*([\w/,\s-]+)\s*-->", re.IGNORECASE
)


def parse_suppressions(raw_content: str) -> dict[int | None, set[str]]:
    """Parse suppression comments from skill content.

    Returns a dict mapping:
      - line number (1-indexed) -> set of suppressed rule IDs (next-line suppression)
      - None -> set of suppressed rule IDs (file-wide suppression)
    """
    suppressions: dict[int | None, set[str]] = {}
    lines = raw_content.split("\n")

    for i, line in enumerate(lines):
        file_match = _FILE_WIDE_RE.search(line)
        if file_match:
            rule_ids = {r.strip() for r in file_match.group(1).split(",")}
            suppressions.setdefault(None, set()).update(rule_ids)
            continue

        next_line_match = _NEXT_LINE_RE.search(line)
        if next_line_match:
            rule_ids = {r.strip() for r in next_line_match.group(1).split(",")}
            target_line = i + 2  # 1-indexed, next line
            suppressions.setdefault(target_line, set()).update(rule_ids)

    return suppressions


def is_suppressed(
    suppressions: dict[int | None, set[str]],
    rule_id: str,
    line: int | None,
) -> bool:
    """Check if a rule is suppressed at a given line."""
    file_wide = suppressions.get(None, set())
    if rule_id in file_wide:
        return True

    if line is not None:
        line_specific = suppressions.get(line, set())
        if rule_id in line_specific:
            return True

    return False
