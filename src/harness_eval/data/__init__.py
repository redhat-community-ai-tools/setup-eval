"""Versioned data files for knowledge that decays over time."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DATA_DIR = Path(__file__).parent


def load_builtins() -> set[str]:
    data = json.loads((_DATA_DIR / "builtins.json").read_text())
    return set(data["claude_code_commands"])


def load_tautological_patterns(
    *,
    generic_advice_only: bool = False,
) -> list[tuple[str, re.Pattern[str]]]:
    data = json.loads((_DATA_DIR / "tautological_patterns.json").read_text())
    patterns = data["patterns"]
    if generic_advice_only:
        patterns = [p for p in patterns if p.get("generic_advice")]
    return [(p["label"], re.compile(p["regex"], re.I)) for p in patterns]
