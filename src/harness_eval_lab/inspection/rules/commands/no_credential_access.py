from __future__ import annotations

from harness_eval_lab.core.types import ComponentType
from harness_eval_lab.inspection.rules.security.no_credential_access import (
    _DANGEROUS_COMMANDS,
    _SENSITIVE_ENV_VARS,
    _SENSITIVE_PATHS,
)
from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)


class CommandNoCredentialAccess:
    meta: RuleMeta = RuleMeta(
        id="command/no-credential-access",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Command definition should not reference sensitive file paths or environment variables",
        category=RuleCategory.SECURITY,
        messages={
            "sensitive_path": "References sensitive path '{{match}}' at line {{line}}",
            "sensitive_env": "References sensitive environment variable '{{match}}' at line {{line}}",
            "dangerous_command": "Contains dangerous command '{{match}}' at line {{line}}",
        },
        target_type=ComponentType.COMMAND,
    )

    def create(self, context: RuleContext) -> None:
        cmd = context.command
        if not cmd or not cmd.raw_content:
            return

        lines = cmd.raw_content.split("\n")

        for i, line in enumerate(lines):
            for pattern in _SENSITIVE_PATHS:
                match = pattern.search(line)
                if match:
                    context.report(
                        ReportDescriptor(
                            message_id="sensitive_path",
                            data={"match": match.group(0), "line": str(i + 1)},
                            location=Location(
                                file=cmd.command_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break

            for pattern in _SENSITIVE_ENV_VARS:
                match = pattern.search(line)
                if match:
                    context.report(
                        ReportDescriptor(
                            message_id="sensitive_env",
                            data={"match": match.group(0), "line": str(i + 1)},
                            location=Location(
                                file=cmd.command_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break

            for pattern, label in _DANGEROUS_COMMANDS:
                match = pattern.search(line)
                if match:
                    context.report(
                        ReportDescriptor(
                            message_id="dangerous_command",
                            data={"match": label, "line": str(i + 1)},
                            location=Location(
                                file=cmd.command_md_path,
                                start_line=i + 1,
                            ),
                        )
                    )
                    break
