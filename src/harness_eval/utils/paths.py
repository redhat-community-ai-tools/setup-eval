"""Path validation utilities to prevent path traversal attacks."""

from __future__ import annotations

from pathlib import Path


def is_within(path: Path, root: Path) -> bool:
    """Check that path resolves to a location within root.

    Resolves symlinks before checking. Returns False if the resolved
    path escapes root or if the path does not exist and contains '..'
    components that would escape.
    """
    try:
        resolved = path.resolve()
        resolved_root = root.resolve()
        return resolved.is_relative_to(resolved_root)
    except (OSError, ValueError):
        return False


def safe_join(root: Path, untrusted: str) -> Path | None:
    """Join an untrusted relative path to a root, returning None if it escapes.

    Does NOT require the path to exist (for checking references that may be broken).
    Normalizes '..' components and checks the result stays within root.
    """
    if not untrusted or untrusted.startswith("/"):
        return None
    candidate = (root / untrusted).resolve()
    resolved_root = root.resolve()
    if candidate.is_relative_to(resolved_root):
        return candidate
    return None
