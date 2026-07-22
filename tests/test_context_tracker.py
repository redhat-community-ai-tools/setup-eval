"""Tests for the shared ContextTracker utility."""

from __future__ import annotations

from harness_eval.inspection.rules._context import ContextTracker


class TestIsFenced:
    def test_outside_fence(self) -> None:
        tracker = ContextTracker()
        tracker.update("normal line")
        assert not tracker.is_fenced()

    def test_inside_fence(self) -> None:
        tracker = ContextTracker()
        tracker.update("```python")
        assert tracker.is_fenced()

    def test_exits_fence(self) -> None:
        tracker = ContextTracker()
        tracker.update("```")
        assert tracker.is_fenced()
        tracker.update("some code")
        assert tracker.is_fenced()
        tracker.update("```")
        assert not tracker.is_fenced()

    def test_multiple_fences(self) -> None:
        tracker = ContextTracker()
        tracker.update("```")
        tracker.update("```")
        assert not tracker.is_fenced()
        tracker.update("```bash")
        assert tracker.is_fenced()

    def test_indented_fence(self) -> None:
        tracker = ContextTracker()
        tracker.update("  ```")
        assert tracker.is_fenced()


class TestIsContextual:
    def test_code_fence_is_contextual(self) -> None:
        tracker = ContextTracker()
        tracker.update("```")
        assert tracker.is_contextual("anything inside")

    def test_blockquote_is_contextual(self) -> None:
        tracker = ContextTracker()
        assert tracker.is_contextual("> quoted text")
        assert tracker.is_contextual("  > indented quote")

    def test_example_line_is_contextual(self) -> None:
        tracker = ContextTracker()
        assert tracker.is_contextual("for example, do this")
        assert tracker.is_contextual("use e.g. this approach")
        assert tracker.is_contextual("such as the following")
        assert tracker.is_contextual("like: this pattern")

    def test_normal_line_not_contextual(self) -> None:
        tracker = ContextTracker()
        assert not tracker.is_contextual("Always use strict mode.")

    def test_not_contextual_outside_fence(self) -> None:
        tracker = ContextTracker()
        tracker.update("```")
        tracker.update("```")
        assert not tracker.is_contextual("back to normal")
