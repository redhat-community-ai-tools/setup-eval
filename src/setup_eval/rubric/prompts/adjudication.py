from __future__ import annotations

ADJUDICATION_SYSTEM = (
    "You are a security reviewer adjudicating automated scanner findings.\n"
    "For each finding, determine whether it represents a genuine security "
    "risk or a false positive.\n\n"
    "Verdicts:\n"
    "- CONFIRMED: The finding is a genuine security concern.\n"
    "- FALSE_POSITIVE: The finding is triggered by benign content "
    "(documentation, examples, hardcoded safe commands, file paths "
    "that match patterns). It should not affect the risk assessment.\n"
    "- DOWNGRADED: The finding has some basis but is lower severity "
    "than reported.\n\n"
    "Be conservative: when uncertain, lean toward CONFIRMED. Only mark "
    "FALSE_POSITIVE when you can clearly explain why the flagged content "
    "is not a security risk.\n\n"
    "Respond with a JSON array. Each element must have: "
    "finding_index (int), verdict (string), reasoning (string, one sentence)."
)

ADJUDICATION_TEMPLATE = """## Component
Type: {component_type}
Name: {component_name}

## Content
{content}

## Scanner Findings to Adjudicate
{findings_text}

Respond with a JSON array. Example:
```json
[
  {{"finding_index": 0, "verdict": "FALSE_POSITIVE", "reasoning": "File path."}},
  {{"finding_index": 1, "verdict": "CONFIRMED", "reasoning": "Sends env vars."}}
]
```"""


def build_adjudication_prompt(
    component_type: str,
    component_name: str,
    content: str,
    findings: list[dict[str, str]],
) -> str:
    findings_lines: list[str] = []
    for i, f in enumerate(findings):
        findings_lines.append(
            f"[{i}] Rule: {f['rule_id']} | Severity: {f['severity']} | {f['message']}"
        )
    return ADJUDICATION_TEMPLATE.format(
        component_type=component_type,
        component_name=component_name,
        content=content[:8000],
        findings_text="\n".join(findings_lines),
    )
