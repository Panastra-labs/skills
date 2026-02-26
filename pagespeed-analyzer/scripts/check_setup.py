#!/usr/bin/env python3
"""Validate local setup for websites/pagespeed_analyzer.py."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

KEY_CANDIDATES = [
    "PAGE_SPEED_INSIGHTS_API_KEY",
    "PAGESPEED_API_KEY",
    "GOOGLE_API_KEY",
]


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


def find_workspace_root() -> Path | None:
    this_file = Path(__file__).resolve()
    candidate_bases = [
        this_file.parent,
        *this_file.parents,
        Path.cwd().resolve(),
        *Path.cwd().resolve().parents,
    ]

    for base in _unique_paths(candidate_bases):
        if (base / "websites" / "pagespeed_analyzer.py").is_file():
            return base
    return None


def parse_env_keys(env_path: Path) -> set[str]:
    keys: set[str] = set()
    if not env_path.is_file():
        return keys

    pattern = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def detect_api_key(env_keys: set[str]) -> str | None:
    for name in KEY_CANDIDATES:
        if os.getenv(name):
            return f"{name} (environment)"
    for name in KEY_CANDIDATES:
        if name in env_keys:
            return f"{name} (.env)"
    return None


def main() -> int:
    workspace_root = find_workspace_root()
    if workspace_root is None:
        print("[FAIL] Could not locate workspace root containing websites/pagespeed_analyzer.py")
        return 1

    analyzer_path = workspace_root / "websites" / "pagespeed_analyzer.py"
    env_path = workspace_root / ".env"
    env_keys = parse_env_keys(env_path)

    print(f"[INFO] Workspace root: {workspace_root}")
    print(f"[INFO] Analyzer path: {analyzer_path}")
    print(f"[INFO] Root .env path: {env_path}")

    ok = True

    if analyzer_path.is_file():
        print("[OK] Analyzer script found")
    else:
        print("[FAIL] Analyzer script missing")
        ok = False

    try:
        import requests  # noqa: F401

        print("[OK] Python dependency 'requests' is available")
    except Exception:
        print("[FAIL] Python dependency 'requests' is missing. Install with: pip install requests")
        ok = False

    key_source = detect_api_key(env_keys)
    if key_source:
        print(f"[OK] API key detected: {key_source}")
    else:
        print(
            "[FAIL] No API key found. Add one of "
            f"{', '.join(KEY_CANDIDATES)} to environment or root .env"
        )
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
