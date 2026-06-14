#!/usr/bin/env python3
"""Install or uninstall the harness-eval-lab plugin into a Claude Code workspace.

Copies skills and commands into the target workspace and installs the
harness-eval-lab Python package. No external dependencies required.

Usage:
    python install.py                              # install into current directory
    python install.py --target /path/to/workspace  # install into specific workspace
    python install.py --uninstall                  # remove from current directory
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

SKILLS = [
    "eval-setup-lint",
    "eval-setup-review",
    "eval-setup-security",
    "eval-skill",
]

COMMANDS = [
    "eval-setup-lint",
    "eval-setup-review",
    "eval-setup-security",
    "eval-skill",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

SYMLINK_SOURCE = "eval-skill/rubric/skills-rubric.md"
SYMLINK_TARGET = "../../eval-setup-review/rubric/skills-rubric.md"


def find_package_manager():
    """Find uv or pip. Returns (command, args_prefix)."""
    uv = shutil.which("uv")
    if uv:
        return "uv", [uv, "pip"]
    pip = shutil.which("pip")
    if pip:
        return "pip", [pip]
    return None, None


def install_skills(target: Path):
    """Copy skill directories into <target>/skills/."""
    skills_dir = target / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for skill in SKILLS:
        src = REPO_ROOT / "skills" / skill
        dst = skills_dir / skill

        if not src.exists():
            print(f"  WARNING: skill source not found: {src}", file=sys.stderr)
            continue

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, symlinks=False)
        print(f"  skills/{skill}/")

    # Recreate the symlink in eval-skill/rubric/
    symlink_path = skills_dir / SYMLINK_SOURCE
    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()
    symlink_path.symlink_to(SYMLINK_TARGET)


def install_commands(target: Path):
    """Copy command files into <target>/.claude/commands/."""
    commands_dir = target / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    for cmd in COMMANDS:
        src = REPO_ROOT / "commands" / cmd / "command.md"
        dst = commands_dir / f"{cmd}.md"

        if not src.exists():
            print(f"  WARNING: command source not found: {src}", file=sys.stderr)
            continue

        shutil.copy2(src, dst)
        print(f"  .claude/commands/{cmd}.md")


def install_package():
    """Install the harness-eval-lab Python package from local checkout."""
    manager, prefix = find_package_manager()
    if not prefix:
        print(
            "  WARNING: neither uv nor pip found, skipping package install.",
            file=sys.stderr,
        )
        print("  Install manually: pip install <path-to-harness-eval-lab>")
        return False

    print(f"  installing harness-eval-lab via {manager}...")
    cmd = [*prefix, "install", str(REPO_ROOT)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  WARNING: package install failed: {result.stderr}", file=sys.stderr)
        return False

    print("  harness-eval-lab package installed")
    return True


def uninstall_skills(target: Path):
    """Remove skill directories from <target>/skills/."""
    for skill in SKILLS:
        path = target / "skills" / skill
        if path.exists():
            shutil.rmtree(path)
            print(f"  removed skills/{skill}/")


def uninstall_commands(target: Path):
    """Remove command files from <target>/.claude/commands/."""
    for cmd in COMMANDS:
        path = target / ".claude" / "commands" / f"{cmd}.md"
        if path.exists():
            path.unlink()
            print(f"  removed .claude/commands/{cmd}.md")


def uninstall_package():
    """Uninstall the harness-eval-lab Python package."""
    manager, prefix = find_package_manager()
    if not prefix:
        return

    cmd = [*prefix, "uninstall", "harness-eval-lab"]
    if manager == "pip":
        cmd.append("-y")
    subprocess.run(cmd, capture_output=True, text=True)
    print("  harness-eval-lab package uninstalled")


def main():
    parser = argparse.ArgumentParser(
        description="Install or uninstall harness-eval-lab plugin into a Claude Code workspace.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.cwd(),
        help="Workspace directory to install into (default: current directory)",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove installed skills, commands, and package",
    )
    args = parser.parse_args()

    target = args.target.resolve()

    if args.uninstall:
        print(f"Uninstalling harness-eval-lab from {target}\n")
        uninstall_skills(target)
        uninstall_commands(target)
        uninstall_package()
        print("\nDone. Restart Claude Code to apply changes.")
        return

    print(f"Installing harness-eval-lab into {target}\n")

    print("Skills:")
    install_skills(target)

    print("\nCommands:")
    install_commands(target)

    print("\nPackage:")
    install_package()

    print(f"""
Done. Restart Claude Code to pick up the new commands.

Available commands after restart:
  /eval-setup-lint      fast static analysis (no LLM)
  /eval-setup-review    full qualitative review
  /eval-setup-security  deep security audit
  /eval-skill           evaluate a single skill
""")


if __name__ == "__main__":
    main()
