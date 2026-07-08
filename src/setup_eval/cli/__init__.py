"""CLI entry point for setup-eval."""

from __future__ import annotations

import click

cli = click.Group(name="setup-eval", help="Evaluate AI agent setups.")
click.version_option(package_name="setup-eval")(cli)

from setup_eval.cli import lint as _lint  # noqa: E402, F401
from setup_eval.cli import review as _review  # noqa: E402, F401
from setup_eval.cli import security as _security  # noqa: E402, F401
from setup_eval.cli import skill as _skill  # noqa: E402, F401
