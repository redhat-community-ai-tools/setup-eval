# /// script
# requires-python = ">=3.11"
# dependencies = ["setup-eval"]
# ///
"""Run full setup assessment and output JSON results."""

import sys
from pathlib import Path


def main() -> None:
    setup_path = sys.argv[1] if len(sys.argv) > 1 else "."
    preset = sys.argv[2] if len(sys.argv) > 2 else "recommended"
    user_config = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None

    from setup_eval.analysis.system import analyze_system
    from setup_eval.config.presets import PRESETS
    from setup_eval.core.setup import discover_setup
    from setup_eval.inspection.engine import inspect_setup
    from setup_eval.output.report import format_json

    config_rules = PRESETS.get(preset, {})
    setup = discover_setup(name=Path(setup_path).name, path=setup_path, user_config_dir=user_config)
    results = inspect_setup(setup, config_rules)
    system = analyze_system(setup)

    print(format_json(system, results))


if __name__ == "__main__":
    main()
