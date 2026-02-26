#!/usr/bin/env python3
"""Run the workspace PageSpeed analyzer with pass-through arguments."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _unique_paths(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def find_analyzer_path(explicit_path: str | None) -> Path:
    if explicit_path:
        candidate = Path(explicit_path).expanduser().resolve()
        if candidate.is_file():
            return candidate
        raise SystemExit(f"Analyzer not found at --analyzer-path: {candidate}")

    this_file = Path(__file__).resolve()
    candidate_bases = [
        this_file.parent,
        *this_file.parents,
        Path.cwd().resolve(),
        *Path.cwd().resolve().parents,
    ]

    for base in _unique_paths(candidate_bases):
        candidate = base / "websites" / "pagespeed_analyzer.py"
        if candidate.is_file():
            return candidate

    raise SystemExit(
        "Could not find websites/pagespeed_analyzer.py. "
        "Run from the workspace root or pass --analyzer-path explicitly."
    )


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run websites/pagespeed_analyzer.py with pass-through flags."
    )
    parser.add_argument("url", help="Target URL to audit")
    parser.add_argument(
        "--analyzer-path",
        default=None,
        help="Optional explicit path to pagespeed_analyzer.py",
    )
    return parser.parse_known_args()


def main() -> int:
    args, passthrough = parse_args()
    analyzer_path = find_analyzer_path(args.analyzer_path)

    cmd = [sys.executable, str(analyzer_path), args.url, *passthrough]
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
