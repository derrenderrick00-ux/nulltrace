"""Lightweight, read-only environment diagnostics. Never scans networks."""
from __future__ import annotations

import argparse
import importlib.util
import platform
import shutil
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 16)
TOOLS = ("git", "nmap", "tshark", "john")


def inspect_environment() -> dict[str, object]:
    """Collect status without launching external tools or modifying the machine."""
    return {
        "python": platform.python_version(),
        "python_supported": MIN_PYTHON <= sys.version_info[:2] < MAX_PYTHON,
        "platform": platform.platform(),
        "pygame_available": importlib.util.find_spec("pygame") is not None,
        "pytest_available": importlib.util.find_spec("pytest") is not None,
        "tools": {tool: shutil.which(tool) for tool in TOOLS},
    }


def check_project_manifest(root: Path) -> list[str]:
    """Identify missing Phase 0 content and structure."""
    expected = (
        "pyproject.toml", "README.md", "content/missions/catalog.json",
        "docs/NULLTRACE_Master_System_Design_v1.0.md",
        "src/nulltrace/doctor.py", "tests/test_phase0.py",
    )
    return [part for part in expected if not (root / part).is_file()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only NULLTRACE Phase 0 environment check")
    parser.add_argument("--strict", action="store_true", help="Require Pygame and a valid starter manifest")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    status = inspect_environment()
    missing = check_project_manifest(root)
    print("NULLTRACE / Phase 0 environment report")
    print("- Python:", status["python"], "(supported)" if status["python_supported"] else "(unsupported)")
    print("- Platform:", status["platform"])
    print("- Pygame-CE import:", "available" if status["pygame_available"] else "not installed")
    print("- pytest import:", "available" if status["pytest_available"] else "not installed")
    print("- Tools (optional until later phases):")
    for tool, path in status["tools"].items():  # type: ignore[union-attr]
        print(f"  {tool}: {path or 'not installed'}")
    print("- Manifest:", "complete" if not missing else "missing " + ", ".join(missing))
    if not status["python_supported"]:
        return 2
    if args.strict and (not status["pygame_available"] or missing):
        return 2
    return 0
