# /// script
# requires-python = ">=3.11"
# dependencies = ["harness-eval"]
# ///
"""Run deep skill evaluation and output JSON results."""

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: run_skill_eval.py <skill-path> [context-path] [preset]"}))
        sys.exit(1)

    skill_path = sys.argv[1]
    context_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    preset = sys.argv[3] if len(sys.argv) > 3 else "recommended"
    user_config = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None

    from harness_eval.analysis.triggers import analyze_triggers
    from harness_eval.config.presets import PRESETS
    from harness_eval.core.setup import discover_setup
    from harness_eval.core.types import ComponentType
    from harness_eval.inspection.engine import lint
    from harness_eval.inspection.parsers import parse_skill
    from harness_eval.utils.similarity import tfidf_similarity

    config_rules = PRESETS.get(preset, {})

    target = Path(skill_path)
    if target.is_file() and target.name.lower() == "skill.md":
        target = target.parent

    skill = parse_skill(str(target))
    result = lint(str(target), config_rules)

    output = {
        "skill": skill.dir_name,
        "tokens": skill.tokens,
        "files": skill.files,
        "frontmatter": dict(skill.frontmatter) if skill.frontmatter else {},
        "errors": result.error_count,
        "warnings": result.warning_count,
        "findings": [
            {"rule": d.rule_id, "severity": d.severity.value, "message": d.message}
            for d in result.diagnostics
        ],
        "context_findings": [],
    }

    if context_path:
        setup = discover_setup(name="context", path=context_path, user_config_dir=user_config)
        context_findings = []

        for comp in setup.by_type(ComponentType.SKILL):
            if comp.name == skill.dir_name:
                continue
            sim = tfidf_similarity(skill.body, comp.content)
            if sim >= 0.60:
                context_findings.append(
                    f"Content overlap: {sim:.0%} similar to skill '{comp.name}'"
                )

        for comp in setup.by_type(ComponentType.CLAUDE_MD):
            for section in comp.content.split("\n#"):
                if len(section.split()) < 20:
                    continue
                sim = tfidf_similarity(skill.body, section)
                if sim >= 0.50:
                    context_findings.append(
                        f"Overlaps with CLAUDE.md content ({sim:.0%} similar)"
                    )
                    break

        triggers = analyze_triggers(setup)
        for name_a, name_b, sim in triggers.overlap_pairs:
            if skill.dir_name in (name_a, name_b):
                other = name_b if name_a == skill.dir_name else name_a
                context_findings.append(
                    f"Trigger overlap with '{other}' ({sim:.0%} similar descriptions)"
                )

        if skill.frontmatter:
            desc = skill.frontmatter.get("description", "")
            if isinstance(desc, str):
                desc_lower = desc.lower()
                if not any(p in desc_lower for p in ["use when", "use for", "applies to", "relevant for"]):
                    context_findings.append(
                        "Missing activation context (no 'use when' phrasing)"
                    )

        output["context_findings"] = context_findings

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
