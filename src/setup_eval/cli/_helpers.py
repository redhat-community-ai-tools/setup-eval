"""Shared CLI helpers."""

from __future__ import annotations

from pathlib import Path

import click


def emit_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text)
    else:
        click.echo(text)
