from __future__ import annotations

import ast
from pathlib import Path

from harness_eval_lab.inspection.types import (
    Location,
    ReportDescriptor,
    RuleCategory,
    RuleContext,
    RuleMeta,
    Severity,
)

_DANGEROUS_BUILTINS = {"exec", "eval", "compile", "__import__"}

_SUBPROCESS_CALLS = {
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "subprocess.check_output",
    "subprocess.check_call",
    "subprocess.getoutput",
    "subprocess.getstatusoutput",
}

_OS_EXEC_CALLS = {
    "os.system",
    "os.popen",
    "os.exec",
    "os.execl",
    "os.execle",
    "os.execlp",
    "os.execlpe",
    "os.execv",
    "os.execve",
    "os.execvp",
    "os.execvpe",
    "os.spawnl",
    "os.spawnle",
    "os.spawnlp",
    "os.spawnlpe",
    "os.spawnv",
    "os.spawnve",
    "os.spawnvp",
    "os.spawnvpe",
}


def _get_call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return f"{node.func.value.id}.{node.func.attr}"
    return None


def _is_dynamic_source(node: ast.expr) -> bool:
    if isinstance(node, ast.Call):
        name = _get_call_name(node)
        if name and any(
            kw in name.lower()
            for kw in ["decode", "b64decode", "urlopen", "read", "recv", "get"]
        ):
            return True
    return isinstance(node, ast.Subscript)


def _analyze_file(py_path: Path, context: RuleContext, skill_md_path: str) -> None:
    try:
        source = py_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(py_path))
    except SyntaxError:
        return

    rel_path = py_path.name

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = _get_call_name(node)
        if call_name is None:
            continue

        line = getattr(node, "lineno", 0)

        if call_name in _DANGEROUS_BUILTINS:
            has_dynamic = any(_is_dynamic_source(arg) for arg in node.args)
            if has_dynamic:
                context.report(
                    ReportDescriptor(
                        message_id="ast_exec_chain",
                        data={
                            "call": call_name,
                            "file": rel_path,
                            "line": str(line),
                        },
                        location=Location(file=skill_md_path, start_line=line),
                    )
                )
            else:
                context.report(
                    ReportDescriptor(
                        message_id="ast_dangerous_call",
                        data={
                            "call": call_name,
                            "file": rel_path,
                            "line": str(line),
                        },
                        location=Location(file=skill_md_path, start_line=line),
                    )
                )
        elif call_name in _SUBPROCESS_CALLS or call_name in _OS_EXEC_CALLS:
            context.report(
                ReportDescriptor(
                    message_id="ast_dangerous_call",
                    data={
                        "call": call_name,
                        "file": rel_path,
                        "line": str(line),
                    },
                    location=Location(file=skill_md_path, start_line=line),
                )
            )
        elif call_name == "getattr" and len(node.args) >= 2:
            if not isinstance(node.args[1], ast.Constant):
                context.report(
                    ReportDescriptor(
                        message_id="ast_dynamic_import",
                        data={
                            "call": "getattr (non-literal)",
                            "file": rel_path,
                            "line": str(line),
                        },
                        location=Location(file=skill_md_path, start_line=line),
                        severity_override=Severity.WARNING,
                    )
                )


class AstBehavioral:
    meta: RuleMeta = RuleMeta(
        id="security/ast-behavioral",
        default_severity=Severity.ERROR,
        fixable=False,
        description="Detect dangerous function calls in Python scripts via AST analysis",
        category=RuleCategory.SECURITY,
        messages={
            "ast_dangerous_call": "{{file}}:{{line}} calls {{call}}, which can execute arbitrary code.",
            "ast_dynamic_import": "{{file}}:{{line}} uses {{call}}, which can load arbitrary modules.",
            "ast_exec_chain": "{{file}}:{{line}} calls {{call}} with a dynamic source (decoded/fetched data), a high-risk execution chain.",
        },
    )

    def create(self, context: RuleContext) -> None:
        skill = context.skill
        if not skill.dir_path:
            return
        skill_dir = Path(skill.dir_path)
        if not skill_dir.is_dir():
            return

        for py_file in sorted(skill_dir.rglob("*.py")):
            if ".git" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            _analyze_file(py_file, context, skill.skill_md_path)
