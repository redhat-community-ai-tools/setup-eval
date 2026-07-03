"""Registry of all tool discoverers."""

from __future__ import annotations

from harness_eval_lab.core.discoverers.base import ToolDiscoverer
from harness_eval_lab.core.discoverers.claude import ClaudeCodeDiscoverer
from harness_eval_lab.core.discoverers.copilot import CopilotDiscoverer
from harness_eval_lab.core.discoverers.cursor import CursorDiscoverer
from harness_eval_lab.core.discoverers.gemini import GeminiDiscoverer
from harness_eval_lab.core.discoverers.opencode import OpenCodeDiscoverer
from harness_eval_lab.core.discoverers.third_party import ThirdPartyDiscoverer

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
