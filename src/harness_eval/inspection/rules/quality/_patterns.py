from __future__ import annotations

import re

from harness_eval.data import load_tautological_patterns

TAUTOLOGICAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = load_tautological_patterns()

_SPECIFICITY_MARKERS = re.compile(
    r"(?:"
    r"`[^`]+`"  # backtick-quoted terms
    r"|\.(?:py|ts|js|tsx|jsx|rs|go|rb|java|yaml|yml|toml|json|md)\b"  # file extensions
    r"|(?:^|[\s(])\.?/"  # path-like strings
    r")",
    re.M,
)


def has_project_specificity(line: str) -> bool:
    return bool(_SPECIFICITY_MARKERS.search(line))
