"""Tests for quality/negative-only rule."""

from __future__ import annotations

from pathlib import Path

from harness_eval.inspection.engine import lint


def _diags_for(result, rule_id: str):
    return [d for d in result.diagnostics if d.rule_id == rule_id]


def _make_skill(tmp_path: Path, body: str) -> str:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"---\ndescription: Test skill\n---\n\n{body}\n")
    return str(skill_dir)


class TestNegativeOnly:
    def test_prohibition_without_alternative_flagged(self, tmp_path: Path) -> None:
        path = _make_skill(tmp_path, "Don't use var in JavaScript.")
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) >= 1

    def test_prohibition_with_alternative_clean(self, tmp_path: Path) -> None:
        path = _make_skill(tmp_path, "Don't use var in JavaScript. Use const or let instead.")
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) == 0

    def test_prohibition_with_alternative_in_next_line_clean(self, tmp_path: Path) -> None:
        path = _make_skill(
            tmp_path, "Never use console.log for debugging.\nUse the logger utility instead."
        )
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) == 0

    def test_code_block_skipped(self, tmp_path: Path) -> None:
        path = _make_skill(tmp_path, "```\nDon't use var.\n```")
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) == 0

    def test_blockquote_skipped(self, tmp_path: Path) -> None:
        path = _make_skill(tmp_path, "> Don't use var.")
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) == 0

    def test_clean_content_no_findings(self, tmp_path: Path) -> None:
        path = _make_skill(
            tmp_path, "Use const for variables that don't change. Use let for mutable bindings."
        )
        result = lint(path, {"quality/negative-only": "warning"})
        assert len(_diags_for(result, "quality/negative-only")) == 0
