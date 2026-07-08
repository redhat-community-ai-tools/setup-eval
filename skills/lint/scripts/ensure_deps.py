# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install setup-eval dependencies into an isolated venv.

Creates .harness-venv/ in the plugin data directory (if provided as argv[1])
or at the project root. Installs the core dependencies from pyproject.toml.

Prefers uv for speed, falls back to stdlib venv + pip.

Uses a stamp file (SHA256 hash of the dep list) to skip re-installation
when nothing has changed. Validates all deps are importable before
considering the install complete.
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

VENV_DIR_NAME = ".harness-venv"

# Core dependencies from pyproject.toml (spec, import_name).
# Keep this in sync with pyproject.toml [project.dependencies].
DEPS = [
    ("click>=8.0", "click"),
    ("pydantic>=2.0", "pydantic"),
    ("pyyaml>=6.0", "yaml"),
    ("tiktoken>=0.7", "tiktoken"),
    ("scikit-learn>=1.0", "sklearn"),
]


def main():
    plugin_data = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    plugin_root = Path(__file__).resolve().parent.parent.parent.parent

    # Decide where the venv lives
    if plugin_data:
        plugin_data.mkdir(parents=True, exist_ok=True)
        venv_dir = plugin_data / VENV_DIR_NAME
    else:
        venv_dir = plugin_root / VENV_DIR_NAME

    stamp = _compute_stamp(DEPS)
    stamp_file = venv_dir / "deps.stamp"

    # Fast path: stamp matches and all deps importable, nothing to do
    venv_python = _find_venv_python(venv_dir)
    if (
        venv_python
        and stamp_file.exists()
        and stamp_file.read_text().strip() == stamp
        and _all_importable(venv_python, DEPS)
    ):
        return

    # Create venv if needed
    _ensure_venv(venv_dir)

    # Install deps
    _install_deps(venv_dir, [spec for spec, _ in DEPS])

    # Validate imports work
    venv_python = _find_venv_python(venv_dir)
    if not venv_python or not _all_importable(venv_python, DEPS):
        print(
            "setup-eval: deps installed but some imports failed",
            file=sys.stderr,
        )
        sys.exit(1)

    # Write stamp on success
    stamp_file.write_text(stamp)


def _find_venv_python(venv_dir):
    """Find the python binary in a venv (handles uv naming variations)."""
    for name in (
        "python3",
        "python",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        candidate = venv_dir / "bin" / name
        if candidate.exists():
            return candidate
    return None


def _ensure_venv(venv_dir):
    """Create the venv if it doesn't exist."""
    if _find_venv_python(venv_dir):
        return

    uv = shutil.which("uv")
    if uv:
        print(f"setup-eval: creating venv with uv: {venv_dir}")
        subprocess.run(
            [uv, "venv", str(venv_dir), "--seed", "--python", sys.executable],
            check=True,
            capture_output=True,
            text=True,
        )
        # uv sometimes names the binary "python" instead of "python3"
        venv_py = _find_venv_python(venv_dir)
        if venv_py and venv_py.name != "python3":
            link = venv_dir / "bin" / "python3"
            if not link.exists():
                link.symlink_to(venv_py.name)
    else:
        print(f"setup-eval: creating venv: {venv_dir}")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
            text=True,
        )


def _install_deps(venv_dir, specs):
    """Install packages into the venv."""
    if not specs:
        return

    venv_python = _find_venv_python(venv_dir)
    if not venv_python:
        print("setup-eval: no python found in venv", file=sys.stderr)
        sys.exit(1)

    uv = shutil.which("uv")
    venv_pip = venv_dir / "bin" / "pip"

    print(f"setup-eval: installing {', '.join(specs)}")

    if uv:
        result = subprocess.run(
            [uv, "pip", "install", "-q", "--python", str(venv_python), *specs],
            capture_output=True,
            text=True,
        )
    elif venv_pip.exists():
        result = subprocess.run(
            [str(venv_pip), "install", "-q", *specs],
            capture_output=True,
            text=True,
        )
    else:
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-q", *specs],
            capture_output=True,
            text=True,
        )

    if result.returncode != 0:
        print(f"setup-eval: install failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def _all_importable(venv_python, deps):
    """Check all deps are importable in the venv python."""
    imports = ";".join(f"__import__('{mod}')" for _, mod in deps)
    result = subprocess.run(
        [str(venv_python), "-c", imports],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _compute_stamp(deps):
    """SHA256 hash of sorted dep specs. Changes when deps change."""
    blob = "|".join(sorted(spec for spec, _ in deps)).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


if __name__ == "__main__":
    main()
