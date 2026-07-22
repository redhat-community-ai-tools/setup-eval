"""Shared skill-reference patterns for content rules."""

from __future__ import annotations

import re
from pathlib import Path

SKILL_REF_PATTERNS = [
    re.compile(r"/(\w[\w-]+)(?:\s|$|[),\]])"),
    re.compile(r"(?:skill|command)[:\s]+[\"']?(\w[\w-]+)[\"']?", re.IGNORECASE),
    re.compile(
        r"(?:invokes?|calls?|triggers?|runs?)\s+[\"'`]?/?(\w[\w-]+)[\"'`]?",
        re.IGNORECASE,
    ),
]


def extract_references(body: str, own_name: str) -> set[str]:
    """Extract skill/command references from body text, excluding self-references."""
    refs: set[str] = set()
    for pattern in SKILL_REF_PATTERNS:
        for match in pattern.finditer(body):
            name = match.group(1)
            if name != own_name and len(name) > 1:
                refs.add(name)
    return refs


def find_project_root(start_path: str) -> Path | None:
    """Walk up from a path to find the project root (containing CLAUDE.md or .claude/)."""
    current = Path(start_path).resolve()
    for _ in range(10):
        if (current / "CLAUDE.md").is_file() or (current / ".claude").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None
