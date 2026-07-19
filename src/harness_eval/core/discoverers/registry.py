"""Registry of all tool discoverers."""

from __future__ import annotations

from harness_eval.core.discoverers.base import ToolDiscoverer
from harness_eval.core.discoverers.claude import ClaudeCodeDiscoverer
from harness_eval.core.discoverers.copilot import CopilotDiscoverer
from harness_eval.core.discoverers.cursor import CursorDiscoverer
from harness_eval.core.discoverers.gemini import GeminiDiscoverer
from harness_eval.core.discoverers.opencode import OpenCodeDiscoverer
from harness_eval.core.discoverers.third_party import ThirdPartyDiscoverer

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
