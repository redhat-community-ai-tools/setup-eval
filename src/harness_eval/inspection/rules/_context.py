"""Shared context-aware line tracking for rule implementations.

Provides consistent code-fence, blockquote, and example detection
across all rules that need to adjust severity or skip lines based
on surrounding context.
"""

from __future__ import annotations

import re

_EXAMPLE_RE = re.compile(r"(?:for\s+example|e\.g\.|such\s+as|like:)", re.I)


class ContextTracker:
    """Tracks whether the current line is inside a code fence, blockquote, or example."""

    def __init__(self) -> None:
        self.in_code_fence: bool = False

    def update(self, line: str) -> None:
        """Update state based on the current line. Call before checking."""
        if line.strip().startswith("```"):
            self.in_code_fence = not self.in_code_fence

    def is_contextual(self, line: str) -> bool:
        """Return True if the line is inside a code fence, blockquote, or example."""
        if self.in_code_fence:
            return True
        stripped = line.lstrip()
        if stripped.startswith(">"):
            return True
        return bool(_EXAMPLE_RE.search(line))

    def is_fenced(self) -> bool:
        """Return True if currently inside a code fence."""
        return self.in_code_fence
