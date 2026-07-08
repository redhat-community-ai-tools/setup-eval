"""Registry of all tool discoverers."""

from __future__ import annotations

from setup_eval.core.discoverers.base import ToolDiscoverer
from setup_eval.core.discoverers.claude import ClaudeCodeDiscoverer
from setup_eval.core.discoverers.copilot import CopilotDiscoverer
from setup_eval.core.discoverers.cursor import CursorDiscoverer
from setup_eval.core.discoverers.gemini import GeminiDiscoverer
from setup_eval.core.discoverers.opencode import OpenCodeDiscoverer
from setup_eval.core.discoverers.third_party import ThirdPartyDiscoverer

DISCOVERERS: list[ToolDiscoverer] = [
    ClaudeCodeDiscoverer(),
    CursorDiscoverer(),
    CopilotDiscoverer(),
    GeminiDiscoverer(),
    OpenCodeDiscoverer(),
    ThirdPartyDiscoverer(),
]


def get_all_discoverers() -> list[ToolDiscoverer]:
    """Return all registered tool discoverers."""
    return DISCOVERERS
