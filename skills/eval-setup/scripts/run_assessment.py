# /// script
# requires-python = ">=3.11"
# dependencies = ["harness-eval-lab"]
# ///
"""Run full setup assessment and output JSON results."""

import sys
from pathlib import Path


def main() -> None:
    setup_path = sys.argv[1] if len(sys.argv) > 1 else "."
    preset = sys.argv[2] if len(sys.argv) > 2 else "recommended"

    from harness_eval_lab.analysis.system import analyze_system
    from harness_eval_lab.config.presets import PRESETS
    from harness_eval_lab.core.setup import discover_setup
    from harness_eval_lab.core.types import ComponentType
    from harness_eval_lab.inspection.engine import (
        lint,
        lint_agent,
        lint_claude_md,
        lint_command,
        lint_hooks,
    )
    from harness_eval_lab.output.report import format_json

    config_rules = PRESETS.get(preset, {})
    setup = discover_setup(name=Path(setup_path).name, path=setup_path)

    results = []
    for comp in setup.by_type(ComponentType.SKILL):
        results.append(lint(str(Path(comp.path).parent), config_rules))
    for comp in setup.by_type(ComponentType.COMMAND):
        results.append(lint_command(str(Path(comp.path).parent), config_rules))
    for comp in setup.by_type(ComponentType.CLAUDE_MD):
        results.append(lint_claude_md(comp.path, config_rules))
    for comp in setup.by_type(ComponentType.HOOKS):
        results.append(lint_hooks(comp.path, config_rules))
    for comp in setup.by_type(ComponentType.AGENT):
        results.append(lint_agent(comp.path, config_rules))

    system = analyze_system(setup)
    system.compute_scores(results)

    print(format_json(system, results))


if __name__ == "__main__":
    main()
