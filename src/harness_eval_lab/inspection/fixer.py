from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_eval_lab.inspection.types import Finding


@dataclass
class FixResult:
    file_path: str
    fixes_applied: int
    rule_ids: list[str]


def apply_fixes(diagnostics: list[Finding]) -> list[FixResult]:
    """Apply auto-fixes for diagnostics that have fix information.

    Groups fixes by file, applies in reverse line order to preserve line numbers.
    """
    fixable = [d for d in diagnostics if d.fix is not None and d.fix.replacement is not None]
    if not fixable:
        return []

    by_file: dict[str, list[Finding]] = {}
    for diag in fixable:
        by_file.setdefault(diag.location.file, []).append(diag)

    results = []
    for file_path, diags in by_file.items():
        path = Path(file_path)
        if not path.exists():
            continue

        content = path.read_text()
        lines = content.split("\n")
        rule_ids = []

        sorted_diags = sorted(
            diags,
            key=lambda d: d.location.start_line or 0,
            reverse=True,
        )

        for diag in sorted_diags:
            if diag.fix is None or diag.fix.replacement is None:
                continue
            line_num = diag.location.start_line
            if line_num is None or line_num < 1 or line_num > len(lines):
                continue
            lines[line_num - 1] = diag.fix.replacement
            rule_ids.append(diag.rule_id)

        path.write_text("\n".join(lines))
        results.append(
            FixResult(
                file_path=file_path,
                fixes_applied=len(rule_ids),
                rule_ids=rule_ids,
            )
        )

    return results
