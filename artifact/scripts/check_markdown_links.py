#!/usr/bin/env python3
"""Check repository Markdown links without network access."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {
    ".git",
    ".local_archive",
    "local_archive",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "site",
    ".cache",
    ".external_audit_tmp",
}

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
RAW_URL_RE = re.compile(r"https?://[^\s)>\"]+")


def tracked_markdown_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "*.md"],
            cwd=REPO_ROOT,
            text=True,
        )
        paths = [REPO_ROOT / line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        paths = list(REPO_ROOT.rglob("*.md"))

    # Include newly created reviewer-facing Markdown files before they are tracked.
    for candidate in [
        REPO_ROOT / "README.md",
        REPO_ROOT / "paper" / "README.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "CLEANUP_REPORT.md",
    ]:
        if candidate.exists() and candidate not in paths:
            paths.append(candidate)

    return sorted(p for p in paths if is_scannable(p))


def is_scannable(path: Path) -> bool:
    rel_parts = path.relative_to(REPO_ROOT).parts
    return not any(part in EXCLUDED_PARTS for part in rel_parts)


def strip_fragment(target: str) -> str:
    return target.split("#", 1)[0]


def is_external(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto"}


def validate_external(target: str) -> bool:
    parsed = urlparse(target)
    if parsed.scheme == "mailto":
        return bool(parsed.path)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_local(source: Path, target: str) -> tuple[bool, str]:
    clean = strip_fragment(target).strip()
    if not clean:
        return True, "anchor-only"
    if clean.startswith("<") and clean.endswith(">"):
        clean = clean[1:-1]
    if clean.startswith("/"):
        return False, "absolute repository paths are not portable in Markdown links"
    resolved = (source.parent / clean).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        return False, "link points outside repository"
    if resolved.exists():
        return True, "exists"
    return False, "missing target"


def collect_links(text: str) -> list[str]:
    links = [match.group(1).strip() for match in MARKDOWN_LINK_RE.finditer(text)]
    # Raw URLs are allowed but syntax-checked.
    links.extend(match.group(0).strip() for match in RAW_URL_RE.finditer(text))
    return links


def main() -> int:
    failures: list[str] = []
    checked_links = 0
    files = tracked_markdown_files()
    for path in files:
        text = path.read_text(errors="ignore")
        for target in collect_links(text):
            if not target or target.startswith("#"):
                continue
            checked_links += 1
            if is_external(target):
                if not validate_external(target):
                    failures.append(f"{path.relative_to(REPO_ROOT)}: malformed external URL `{target}`")
                continue
            ok, reason = validate_local(path, target)
            if not ok:
                failures.append(f"{path.relative_to(REPO_ROOT)}: broken link `{target}` ({reason})")

    print(f"Checked {checked_links} Markdown links across {len(files)} files.")
    if failures:
        print("Broken or malformed links:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("All checked Markdown links are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
