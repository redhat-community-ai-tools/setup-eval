from __future__ import annotations

import re
from pathlib import Path

from harness_eval.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_SOURCE_PATTERNS = [
    re.compile(r"\$[1-9]"),
    re.compile(r"\$[@*]"),
    re.compile(r"\$\{!\w+\}"),
    re.compile(r"\bread\b"),
    re.compile(r"\$\([^)]+\)"),
]

_SINK_PATTERNS = [
    (re.compile(r"\beval\b"), "eval"),
    (re.compile(r"\bexec\b"), "exec"),
    (re.compile(r"`[^`]+`"), "backtick execution"),
    (re.compile(r"\bsource\b"), "source"),
    (re.compile(r"\bbash\s+-c\b"), "bash -c"),
    (re.compile(r"\bsh\s+-c\b"), "sh -c"),
]

# Patterns that are self-contained taint flows (source + sink in one pattern)
_SELF_CONTAINED_PATTERNS = [
    (re.compile(r"\bcurl\b.*\|\s*(?:bash|sh)\b"), "curl | bash"),
    (re.compile(r"\bwget\b.*\|\s*(?:bash|sh)\b"), "wget | bash"),
]

_ASSIGNMENT_RE = re.compile(r"^(\w+)=(.+)$")
_READ_CMD_RE = re.compile(r"\bread\s+(?:-\w+\s+)*(\w+)")


def _has_source(line: str) -> bool:
    """Check if a line contains an untrusted source pattern."""
    return any(p.search(line) for p in _SOURCE_PATTERNS)


def _find_sink(line: str) -> str | None:
    """Return the sink label if a line contains a dangerous sink, else None."""
    for pattern, label in _SINK_PATTERNS:
        if pattern.search(line):
            return label
    return None


def _analyze_bash_file(bash_path: Path, context: RuleContext, skill_md_path: str) -> None:
    try:
        source = bash_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return

    lines = source.split("\n")
    rel_path = bash_path.name

    # Track variables assigned from tainted sources
    tainted_vars: dict[str, int] = {}  # var_name -> line_number

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Track assignments from tainted sources
        assign_match = _ASSIGNMENT_RE.match(stripped)
        if assign_match:
            var_name, value = assign_match.group(1), assign_match.group(2)
            if _has_source(value):
                tainted_vars[var_name] = i

        # Track read command: `read VAR` taints VAR
        read_match = _READ_CMD_RE.search(stripped)
        if read_match:
            tainted_vars[read_match.group(1)] = i

        # Self-contained taint flows (e.g., curl | bash)
        for pattern, label in _SELF_CONTAINED_PATTERNS:
            if pattern.search(stripped):
                context.report(
                    ReportDescriptor(
                        message_id="bash_taint_flow",
                        data={
                            "file": rel_path,
                            "sink": label,
                            "line": str(i),
                        },
                        location=Location(file=skill_md_path, start_line=i),
                    )
                )
                continue

        # Check if this line has a sink
        sink = _find_sink(stripped)
        if sink is None:
            continue

        # Direct: line has both source and sink
        if _has_source(stripped):
            context.report(
                ReportDescriptor(
                    message_id="bash_taint_flow",
                    data={
                        "file": rel_path,
                        "sink": sink,
                        "line": str(i),
                    },
                    location=Location(file=skill_md_path, start_line=i),
                )
            )
            continue

        # Indirect: line uses a tainted variable in a sink
        for var_name, source_line in tainted_vars.items():
            if f"${var_name}" in stripped or f"${{{var_name}}}" in stripped:
                context.report(
                    ReportDescriptor(
                        message_id="bash_taint_indirect",
                        data={
                            "file": rel_path,
                            "var": var_name,
                            "source_line": str(source_line),
                            "sink": sink,
                            "sink_line": str(i),
                        },
                        location=Location(file=skill_md_path, start_line=i),
                    )
                )
                break


class BashTaintTracking:
    meta: RuleMeta = RuleMeta(
        id="security/bash-taint-flow",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Detect data flows from untrusted sources to dangerous sinks in bash scripts",
        category=RuleCategory.SECURITY,
        messages={
            "bash_taint_flow": "{{file}}: untrusted input flows to {{sink}} (line {{line}}). Possible injection vector.",
            "bash_taint_indirect": "{{file}}: tainted variable '${{var}}' (from line {{source_line}}) flows to {{sink}} (line {{sink_line}}). Possible injection vector.",
        },
    )

    def create(self, context: RuleContext) -> None:
        skill = context.skill
        if not skill.dir_path:
            return
        skill_dir = Path(skill.dir_path)
        if not skill_dir.is_dir():
            return

        for bash_file in sorted(skill_dir.rglob("*.sh")):
            if ".git" in bash_file.parts or "__pycache__" in bash_file.parts:
                continue
            _analyze_bash_file(bash_file, context, skill.skill_md_path)

        for bash_file in sorted(skill_dir.rglob("*.bash")):
            if ".git" in bash_file.parts or "__pycache__" in bash_file.parts:
                continue
            _analyze_bash_file(bash_file, context, skill.skill_md_path)
