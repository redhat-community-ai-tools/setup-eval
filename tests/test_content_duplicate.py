"""Tests for content/duplicate-detection rule."""

from __future__ import annotations

from pathlib import Path

from harness_eval.core.setup import discover_setup
from harness_eval.inspection.engine import inspect_setup


def _diags_for(results, rule_id: str):
    return [d for r in results for d in r.diagnostics if d.rule_id == rule_id]


class TestContentDuplicateDetection:
    def test_duplicate_skills_flagged(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        body = (
            "Deploy the application to production using the deploy script. "
            "Run tests first, then build, then push to the registry. "
            "Monitor the deployment for errors and rollback if needed."
        )
        for name in ("deploy-a", "deploy-b"):
            d = skills_dir / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"---\ndescription: Deploy to production\n---\n\n{body}\n")
        (tmp_path / "CLAUDE.md").write_text("# Test project\n")

        setup = discover_setup(name="test", path=str(tmp_path))
        results = inspect_setup(setup, {"content/duplicate-detection": "warning"})
        diags = _diags_for(results, "content/duplicate-detection")
        assert len(diags) >= 1

    def test_unique_skills_clean(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        for name, desc, body in [
            ("deploy", "Deploy to prod", "Deploy using CI pipeline and Docker."),
            ("test", "Run tests", "Run pytest with coverage reporting."),
        ]:
            d = skills_dir / name
            d.mkdir()
            (d / "SKILL.md").write_text(f"---\ndescription: {desc}\n---\n\n{body}\n")
        (tmp_path / "CLAUDE.md").write_text("# Test project\n")

        setup = discover_setup(name="test", path=str(tmp_path))
        results = inspect_setup(setup, {"content/duplicate-detection": "warning"})
        diags = _diags_for(results, "content/duplicate-detection")
        assert len(diags) == 0
