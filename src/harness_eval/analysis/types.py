"""Types for cross-analysis."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SetupComparison:
    """Comparison of inspection results between two setups."""

    setup_a: str
    setup_b: str
    shared_components: list[str] = field(default_factory=list)
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)
    score_deltas: dict[str, int] = field(default_factory=dict)


@dataclass
class Correlation:
    """A correlation between a component difference and an inspection score difference."""

    component_name: str
    component_type: str
    setup_name: str
    error_count: int
    warning_count: int
    impact: str  # "positive", "negative", "neutral"
    explanation: str


@dataclass
class CrossAnalysisResult:
    """Complete cross-analysis result."""

    comparison: SetupComparison
    correlations: list[Correlation] = field(default_factory=list)
    summary: str = ""
    setup_scores: dict[str, dict[str, int]] = field(default_factory=dict)
