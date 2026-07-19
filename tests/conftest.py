"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def setup_a_path() -> str:
    return str(FIXTURES_DIR / "sample-setup-a")


@pytest.fixture
def setup_b_path() -> str:
    return str(FIXTURES_DIR / "sample-setup-b")


@pytest.fixture
def tmp_experiment_yaml(tmp_path: Path, setup_a_path: str, setup_b_path: str) -> str:
    config = f"""\
apiVersion: harness-eval/v1
experiment:
  name: test-experiment
  description: Test experiment
  setups:
    - name: setup-a
      path: {setup_a_path}
    - name: setup-b
      path: {setup_b_path}
  probes:
    source: generate
    count: 2
    types:
      - review
  judge:
    provider: gemini
    model: gemini-3-flash-preview
    votes_per_probe: 1
  inspect:
    enabled: true
    preset: recommended
  rubric:
    enabled: false
  cross_analysis:
    enabled: false
"""
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(config)
    return str(config_path)
