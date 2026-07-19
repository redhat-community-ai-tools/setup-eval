"""Tests for setup fingerprinting."""

from __future__ import annotations

import pytest

from harness_eval.core.fingerprint import fingerprint_setup, fingerprints_match


def test_fingerprint_deterministic(setup_a_path: str) -> None:
    fp1 = fingerprint_setup(setup_a_path)
    fp2 = fingerprint_setup(setup_a_path)
    assert fp1 == fp2


def test_fingerprint_differs_between_setups(setup_a_path: str, setup_b_path: str) -> None:
    fp_a = fingerprint_setup(setup_a_path)
    fp_b = fingerprint_setup(setup_b_path)
    assert fp_a != fp_b


def test_fingerprint_is_sha256(setup_a_path: str) -> None:
    fp = fingerprint_setup(setup_a_path)
    assert len(fp) == 64
    assert all(c in "0123456789abcdef" for c in fp)


def test_fingerprints_match_identical(setup_a_path: str) -> None:
    fp = fingerprint_setup(setup_a_path)
    assert fingerprints_match(fp, fp)


def test_fingerprints_match_different(setup_a_path: str, setup_b_path: str) -> None:
    fp_a = fingerprint_setup(setup_a_path)
    fp_b = fingerprint_setup(setup_b_path)
    assert not fingerprints_match(fp_a, fp_b)


def test_fingerprint_nonexistent_path() -> None:
    with pytest.raises(FileNotFoundError):
        fingerprint_setup("/nonexistent/path")
