#!/usr/bin/env python3
"""Read-only cross-platform preflight for collage-broll-shorts projects."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA = "collage-broll-shorts/preflight-1"
LAYOUT = (
    "config",
    "input/source",
    "input/transcript",
    "input/brief",
    "input/references",
    "work",
    "output",
)


def resolve_path(value: Optional[str], base: Path) -> Path:
    """Resolve a user path relative to base without touching the filesystem."""
    if not value:
        return base
    path = Path(value).expanduser()
    return path if path.is_absolute() else base / path


def locate_tool(
    env_name: str,
    names: Iterable[str],
    root: Path,
    local_relative: Iterable[str] = (),
) -> Optional[Path]:
    """Find an executable from an explicit path, local project path, or PATH."""
    override = os.environ.get(env_name)
    if override:
        override_path = Path(override).expanduser()
        try:
            if override_path.is_file():
                return override_path
        except OSError:
            # Preserve the explicit candidate so run_version can report the
            # access error instead of making the preflight crash.
            return override_path
        path_result = shutil.which(override)
        if path_result:
            return Path(path_result)

    for relative in local_relative:
        local_path = root / relative
        try:
            if local_path.is_file():
                return local_path
        except OSError:
            continue

    for name in names:
        path_result = shutil.which(name)
        if path_result:
            return Path(path_result)
    return None


def run_version(path: Path, args: Sequence[str]) -> Dict[str, Any]:
    """Read a short version string without writing or changing project files."""
    try:
        completed = subprocess.run(
            [str(path), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "error": str(exc)}

    combined = (completed.stdout or "") + (completed.stderr or "")
    first_line = next((line.strip() for line in combined.splitlines() if line.strip()), "")
    result: Dict[str, Any] = {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
    }
    if first_line:
        result["version"] = first_line[:200]
    if completed.returncode != 0 and first_line:
        result["error"] = first_line[:200]
    return result


def tool_check(
    label: str,
    env_name: str,
    names: Iterable[str],
    root: Path,
    required: bool,
    version_args: Sequence[str],
    local_relative: Iterable[str] = (),
) -> Tuple[Dict[str, Any], Optional[str]]:
    path = locate_tool(env_name, names, root, local_relative)
    result: Dict[str, Any] = {"required": required, "found": path is not None}
    if path is None:
        message = f"Missing {label} ({env_name} or PATH)"
        return result, message if required else None

    result["path"] = str(path)
    version_result = run_version(path, version_args)
    result.update(version_result)
    if required and not version_result.get("ok", False):
        return result, f"{label} was found but did not answer {list(version_args)}"
    return result, None


def platform_family() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "macos"
    return system or "unknown"


def directory_check(root: Path, require_layout: bool) -> Tuple[Dict[str, Any], List[str]]:
    layout: Dict[str, Any] = {}
    errors: List[str] = []
    if not root.exists():
        if require_layout:
            errors.append(f"Project root does not exist: {root}")
        return {"root_exists": False, "directories": layout}, errors

    if not root.is_dir():
        errors.append(f"Project root is not a directory: {root}")
        return {"root_exists": True, "directories": layout}, errors

    for relative in LAYOUT:
        path = root / relative
        exists = path.is_dir()
        layout[relative] = {"exists": exists, "path": str(path)}
        if require_layout and not exists:
            errors.append(f"Missing required project directory: {relative}")
    return {"root_exists": True, "directories": layout}, errors


def build_report(args: argparse.Namespace) -> Dict[str, Any]:
    raw_root = args.root or os.environ.get("COLLAGE_BROLL_ROOT") or os.getcwd()
    root = resolve_path(raw_root, Path.cwd()).resolve()
    input_value = args.input or os.environ.get("COLLAGE_BROLL_INPUT")
    output_value = args.output or os.environ.get("COLLAGE_BROLL_OUTPUT")
    input_dir = (resolve_path(input_value, root) if input_value else root / "input").resolve()
    output_dir = (resolve_path(output_value, root) if output_value else root / "output").resolve()

    errors: List[str] = []
    warnings: List[str] = []
    layout_report, layout_errors = directory_check(root, args.require_layout)
    errors.extend(layout_errors)

    python_ok = sys.version_info >= (3, 10)
    python_report: Dict[str, Any] = {
        "required": True,
        "found": True,
        "ok": python_ok,
        "version": platform.python_version(),
        "executable": sys.executable,
    }
    if not python_ok:
        errors.append("Python 3.10 or newer is required")

    ffmpeg_report, ffmpeg_error = tool_check(
        "ffmpeg", "FFMPEG_BIN", ("ffmpeg",), root, True, ("-version",)
    )
    ffprobe_report, ffprobe_error = tool_check(
        "ffprobe", "FFPROBE_BIN", ("ffprobe",), root, True, ("-version",)
    )
    for message in (ffmpeg_error, ffprobe_error):
        if message:
            errors.append(message)

    renderer = (args.renderer or os.environ.get("COLLAGE_BROLL_RENDERER") or "ffmpeg").lower()
    if renderer not in {"ffmpeg", "remotion", "adapter"}:
        errors.append(f"Unsupported renderer: {renderer}")
        renderer = "invalid"

    node_required = args.require_node or renderer == "remotion"
    node_report, node_error = tool_check(
        "node", "NODE_BIN", ("node",), root, node_required, ("--version",)
    )
    if node_error:
        errors.append(node_error)
    elif not node_report.get("found"):
        warnings.append("Node is not available; it is optional unless the Remotion renderer is selected")

    remotion_required = args.require_remotion or renderer == "remotion"
    remotion_report, remotion_error = tool_check(
        "Remotion CLI",
        "REMOTION_BIN",
        ("remotion",),
        root,
        remotion_required,
        ("--version",),
        local_relative=(
            "node_modules/.bin/remotion",
            "node_modules/.bin/remotion.cmd",
        ),
    )
    if remotion_error:
        errors.append(remotion_error)
    elif not remotion_report.get("found"):
        warnings.append("Remotion CLI is not available; it is optional unless the Remotion renderer is selected")

    return {
        "schema": SCHEMA,
        "ok": not errors,
        "platform": {
            "family": platform_family(),
            "system": platform.system(),
            "release": platform.release(),
        },
        "paths": {
            "root": str(root),
            "input": str(input_dir),
            "output": str(output_dir),
        },
        "renderer": renderer,
        "dependencies": {
            "python": python_report,
            "ffmpeg": ffmpeg_report,
            "ffprobe": ffprobe_report,
            "node": node_report,
            "remotion": remotion_report,
        },
        "layout": layout_report,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="project root; defaults to COLLAGE_BROLL_ROOT or cwd")
    parser.add_argument("--input", help="input directory override")
    parser.add_argument("--output", help="output directory override")
    parser.add_argument(
        "--renderer",
        choices=("ffmpeg", "remotion", "adapter"),
        help="selected renderer; remotion makes Node and Remotion required",
    )
    parser.add_argument("--require-node", action="store_true", help="fail if Node is missing")
    parser.add_argument("--require-remotion", action="store_true", help="fail if Remotion is missing")
    parser.add_argument("--require-layout", action="store_true", help="fail if the standard directories are missing")
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        print(f"{status}: {report['platform']['family']} / renderer={report['renderer']}")
        for label, item in report["dependencies"].items():
            state = "ok" if item.get("ok") else "missing/failed"
            print(f"- {label}: {state}")
        for message in report["errors"]:
            print(f"ERROR: {message}")
        for message in report["warnings"]:
            print(f"WARNING: {message}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
