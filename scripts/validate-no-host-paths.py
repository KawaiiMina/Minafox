#!/usr/bin/env python3
"""Fail if MinaFox source files contain host-specific absolute paths.

The repo should be portable to Mina's Arch PC and must not bake in paths from the
machine where the project was authored. Install scripts may compute paths from
$HOME at runtime instead.
"""
from __future__ import annotations

import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "/" + "home" + "/" + "hermes",
    "/" + "hermes" + "/" + "home",
)
ABSOLUTE_HOME_RE = re.compile(r"/home/[A-Za-z0-9._-]+")
SKIP_PARTS = {
    ".git",
    ".hermes",
    "__pycache__",
}
TEXT_SUFFIXES = {
    ".css",
    ".desktop",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yml",
    ".yaml",
}


def is_checked_file(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    if any(part in SKIP_PARTS for part in rel_parts):
        return False
    return path.is_file() and path.suffix in TEXT_SUFFIXES


def main() -> int:
    violations: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not is_checked_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for forbidden in FORBIDDEN:
                if forbidden in line:
                    rel = path.relative_to(ROOT)
                    violations.append(f"{rel}:{line_no}: contains {forbidden!r}")
            if ABSOLUTE_HOME_RE.search(line):
                rel = path.relative_to(ROOT)
                violations.append(f"{rel}:{line_no}: contains an absolute /home/<user> path")

    if violations:
        print("MinaFox host path validation: FAIL", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print("MinaFox host path validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
