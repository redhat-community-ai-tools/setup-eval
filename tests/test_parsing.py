"""Tests for parsing utilities."""

from __future__ import annotations

from harness_eval.utils.parsing import parse_frontmatter


def test_parse_frontmatter_basic() -> None:
    content = "---\nname: test\ndescription: A test\n---\n\nBody content here."
    fm, body = parse_frontmatter(content)
    assert fm is not None
    assert fm["name"] == "test"
    assert fm["description"] == "A test"
    assert body.strip() == "Body content here."


def test_parse_frontmatter_none() -> None:
    content = "No frontmatter here."
    fm, body = parse_frontmatter(content)
    assert fm is None
    assert body == content


def test_parse_frontmatter_invalid_yaml() -> None:
    content = "---\n[invalid: yaml: content\n---\n\nBody."
    fm, body = parse_frontmatter(content)
    assert fm is None
    assert body == content


def test_parse_frontmatter_non_dict() -> None:
    content = "---\n- list\n- not dict\n---\n\nBody."
    fm, body = parse_frontmatter(content)
    assert fm is None
    assert body == content
