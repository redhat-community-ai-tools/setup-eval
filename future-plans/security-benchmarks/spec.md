# Security Rule Benchmarks

**Status:** planned
**Created:** 2026-07-06

## Problem

harness-eval-lab includes security rules covering prompt injection, credential access, data exfiltration, obfuscation, reverse shells, taint flows, and more. But there is no systematic way to measure how well these rules perform. Detection rates, false positive rates, and per-rule precision are unknown. New rules ship without validated coverage, regressions go unnoticed, and claims about security capabilities are feature-counts rather than evidence.

Without benchmarks, the security evaluation is "trust me, it works." That is not good enough for a tool that tells users their setup is safe.

## Goal

Measure detection rate and false positive rate for each security rule. Provide a regression-testing baseline so that rule changes never silently degrade detection quality.

## Proposal

Build a benchmark suite with a curated corpus of known-malicious, known-clean, and edge-case fixtures. Run all security rules against the corpus and report per-rule and aggregate metrics.

### Corpus structure

```
benchmarks/
    malicious/              # Known-bad patterns, labeled with expected findings
        prompt-injection/   # Direct and indirect injection variants
        credential-access/  # Hardcoded secrets, env leaks, credential exfiltration
        data-exfiltration/  # Unauthorized data transmission patterns
        obfuscation/        # Base64, rot13, unicode tricks, encoding evasion
        reverse-shells/     # Shell spawning and reverse connection patterns
        taint-flows/        # Unsanitized data flowing from input to sensitive sink
    clean/                  # Fixtures that look suspicious but are actually safe
        legitimate-eval/    # Safe use of eval-like constructs in appropriate contexts
        safe-network/       # Network calls with proper authorization and scoping
        sanitized-input/    # User input that passes through proper validation
        security-docs/      # Documentation discussing attacks (should not trigger)
    edge-cases/             # Boundary cases that test rule precision
        partial-matches/    # Patterns that partially resemble threats
        context-dependent/  # Patterns safe in one context, dangerous in another
        multi-rule/         # Fixtures that should trigger some rules but not others
```

Each fixture file includes a YAML frontmatter block with expected findings:

```yaml
---
expected:
  - rule: security/no-prompt-injection
    line: 8
    label: ignore_instructions
  - rule: security/no-credential-access
    line: 15
    label: hardcoded_api_key
---
```

Clean fixtures use `expected: []` to assert no findings.

### Sources for the malicious corpus

1. **OWASP LLM Top 10 prompt injection patterns.** The OWASP Foundation maintains a taxonomy of LLM-specific attacks including direct prompt injection, indirect prompt injection via external content, and instruction hierarchy violations.

2. **Published research.** Greshake et al. (2023) on indirect prompt injection via retrieval-augmented generation. Perez and Ribeiro on red-teaming LLMs for harmful outputs. These papers include concrete attack strings and evasion techniques that make good test cases.

3. **Real-world CTF challenges.** AI agent exploitation challenges from CTF competitions (e.g., LLM-specific challenges from DEF CON AI Village, HackAPrompt). These test realistic adversarial scenarios rather than synthetic examples.

4. **Patterns discovered during setup-eval development.** Rules were written in response to real attack patterns found in the wild. The original motivating examples for each rule become the seed corpus for that rule's benchmarks.

### Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Per-rule detection rate | true positives / total positives in corpus | >= 80% per rule |
| Per-rule false positive rate | false positives / total clean fixtures | <= 5% per rule |
| Aggregate detection rate | total true positives / total expected positives across all rules | >= 90% |
| Time to scan | wall clock for full corpus | < 30s (baseline, no LLM) |

### Running the benchmark

```bash
uv run pytest tests/security_benchmarks/ --benchmark
```

The benchmark runner:
1. Discovers all fixtures in `benchmarks/`
2. Parses expected findings from YAML frontmatter
3. Runs security rules against each fixture
4. Compares actual findings to expected findings
5. Produces per-rule and aggregate metrics in both terminal and JSON output

### CI integration

Run the benchmark on every PR that modifies security rules (files under `src/harness_eval_lab/inspection/rules/security/`). The CI job fails if:

- Any rule's detection rate drops below 80%
- Any rule's false positive rate exceeds 5%
- Aggregate detection rate drops below 90%

This prevents rule changes from silently degrading detection quality.

## User stories

### Story 1: Validate a new security rule

**Given** a developer adds a new security rule
**When** they add corresponding fixtures to the malicious corpus and run the benchmark
**Then** they see the rule's detection rate and false positive rate, confirming it meets thresholds before merging.

### Story 2: Catch regressions in pattern matching

**Given** a developer modifies an existing security rule's regex
**When** CI runs the benchmark suite
**Then** any drop in detection rate is surfaced as a test failure, preventing the regression from merging.

### Story 3: Demonstrate coverage to adopters

**Given** a potential user evaluates harness-eval-lab for their team
**When** they review the benchmark results
**Then** they see concrete per-rule detection rates, not just a feature list.

## Requirements

1. Malicious corpus must include at least 50 fixtures spanning all 6 attack categories.
2. Clean corpus must include at least 20 fixtures covering legitimate patterns that resemble threats.
3. Edge-case corpus must include at least 10 boundary fixtures.
4. Each fixture must be labeled with expected findings (rule ID, line number, pattern label).
5. Benchmark runner must be deterministic (no LLM calls, pure static analysis).
6. Benchmark must produce both human-readable and machine-readable (JSON) output.
7. CI must run the benchmark on every PR that touches security rule files.
8. CI must fail if any per-rule detection rate drops below 80%.

## Success criteria

- Benchmark suite runs in under 30 seconds on the full corpus.
- Aggregate detection rate >= 90% against the malicious corpus.
- Aggregate false positive rate <= 5% against the clean corpus.
- Every security rule has at least 3 corresponding fixtures in the malicious corpus.
- Benchmark report is reproducible (same corpus + same rules = same results).

## Open questions

1. **Corpus maintenance:** As new attack techniques emerge, how often should the corpus be updated? A quarterly review cycle, or ad-hoc when new patterns are discovered?

2. **Semantic review benchmarking:** The LLM-based semantic security review is non-deterministic. Should it be benchmarked separately with averaged results across multiple runs, or excluded from this deterministic benchmark suite entirely?

3. **Evasion resistance scoring:** Should obfuscated variants of known attacks be tracked as a separate metric, or folded into the per-rule detection rate? Tracking separately would highlight which rules are robust to evasion and which are brittle.

4. **Cross-tool comparison:** Should the benchmark include runs of other security scanners (Semgrep, CodeQL custom rules) against the same corpus? Useful for positioning but adds maintenance burden.
