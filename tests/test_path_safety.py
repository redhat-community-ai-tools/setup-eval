"""Tests for path traversal prevention."""

from pathlib import Path

from setup_eval.utils.paths import is_within, safe_join


class TestIsWithin:
    def test_child_path(self, tmp_path: Path) -> None:
        child = tmp_path / "subdir" / "file.txt"
        child.parent.mkdir(parents=True)
        child.touch()
        assert is_within(child, tmp_path) is True

    def test_same_path(self, tmp_path: Path) -> None:
        assert is_within(tmp_path, tmp_path) is True

    def test_parent_escapes(self, tmp_path: Path) -> None:
        escaped = tmp_path / ".." / ".." / "etc" / "passwd"
        assert is_within(escaped, tmp_path) is False

    def test_symlink_escape(self, tmp_path: Path) -> None:
        target = Path("/tmp")
        link = tmp_path / "escape_link"
        link.symlink_to(target)
        assert is_within(link, tmp_path) is False

    def test_symlink_within(self, tmp_path: Path) -> None:
        target = tmp_path / "real_file.txt"
        target.touch()
        link = tmp_path / "link_file.txt"
        link.symlink_to(target)
        assert is_within(link, tmp_path) is True


class TestSafeJoin:
    def test_simple_relative(self, tmp_path: Path) -> None:
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "run.sh").touch()
        result = safe_join(tmp_path, "scripts/run.sh")
        assert result is not None
        assert result == (tmp_path / "scripts" / "run.sh").resolve()

    def test_traversal_blocked(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "../../etc/passwd")
        assert result is None

    def test_absolute_path_blocked(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "/etc/passwd")
        assert result is None

    def test_empty_string_blocked(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "")
        assert result is None

    def test_dotdot_in_middle(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "scripts/../../../etc/passwd")
        assert result is None

    def test_nonexistent_but_safe(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "does/not/exist.txt")
        assert result is not None

    def test_hidden_ssh_traversal(self, tmp_path: Path) -> None:
        result = safe_join(tmp_path, "../../.ssh/id_rsa")
        assert result is None
