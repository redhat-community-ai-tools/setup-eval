"""Prompt templates for LLM-based rubric issue detection."""

from __future__ import annotations

from pathlib import Path

from harness_eval_lab.rubric.types import IssueCategory

_PROMPTS_DIR = Path(__file__).parent / "prompts"

SYSTEM_PROMPT = (_PROMPTS_DIR / "system.md").read_text().strip()
ISSUE_TEMPLATE = (_PROMPTS_DIR / "issue-template.md").read_text()


def build_issue_prompt(
    component_type: str,
    component_name: str,
    content: str,
    categories: list[IssueCategory],
    context: str | None = None,
) -> str:
    cats_text = "\n".join(f"- **{c.name}**: {c.description}" for c in categories)

    context_section = ""
    if context:
        context_section = f"### Context (other components in the setup):\n{context}\n"

    return ISSUE_TEMPLATE.format(
        component_type=component_type,
        component_name=component_name,
        content=content,
        context_section=context_section,
        categories_section=cats_text,
    )
