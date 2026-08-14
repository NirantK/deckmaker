#!/usr/bin/env python3
"""Find repository files likely to contain facts relevant to a presentation brief."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


KEYWORDS = {
    "audience",
    "brand",
    "brief",
    "customer",
    "deck",
    "demo",
    "design",
    "launch",
    "market",
    "narrative",
    "pitch",
    "presentation",
    "product",
    "roadmap",
    "slide",
    "strategy",
}
PRIORITY_NAMES = {
    "agents.md",
    "brief.md",
    "cargo.toml",
    "go.mod",
    "package.json",
    "pyproject.toml",
    "readme.md",
    "readme.rst",
    "readme.txt",
}
TEXT_SUFFIXES = {
    ".css",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".rb",
    ".rs",
    ".rst",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
SENSITIVE_PARTS = {"credential", "password", "secret", "token"}
MAX_BYTES = 512_000
SKILL_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rank repository files that may contain presentation-relevant facts."
    )
    parser.add_argument("root", nargs="?", default=".", help="repository root (default: .)")
    parser.add_argument("--deep", action="store_true", help="scan beyond the top two levels")
    parser.add_argument("--limit", type=int, default=20, help="maximum candidates to print")
    return parser.parse_args()


def is_sensitive(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered.startswith(".env") or any(part in lowered for part in SENSITIVE_PARTS)


def candidates(root: Path, deep: bool):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        relative_dir = Path(current).relative_to(root)
        depth = len(relative_dir.parts)
        if not deep and depth >= 2:
            dirs[:] = []
        for name in sorted(files):
            path = Path(current, name)
            relative = path.relative_to(root)
            if path.is_relative_to(SKILL_ROOT):
                continue
            if is_sensitive(path):
                continue
            if name.lower() not in PRIORITY_NAMES and path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path, relative


def score_file(path: Path, relative: Path) -> tuple[int, set[str]]:
    path_words = {word for word in KEYWORDS if word in str(relative).lower()}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return 0, set()
    content_words = {word for word in KEYWORDS if word in text}
    score = len(path_words) * 4 + len(content_words)
    if path.name.lower() in PRIORITY_NAMES:
        score += 3
    return score, path_words | content_words


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    ranked = []
    for path, relative in candidates(root, args.deep):
        score, words = score_file(path, relative)
        if score:
            ranked.append((score, str(relative), words))
    ranked.sort(key=lambda item: (-item[0], item[1]))

    direct = any(score >= 5 for score, _, _ in ranked)
    print(f"Repository: {root}")
    print(f"Mode: {'deep' if args.deep else 'light'}")
    print(f"Direct relevance: {'yes' if direct else 'no'}")
    print("Candidates (paths and matched topics only; inspect files to establish facts):")
    for score, relative, words in ranked[: max(args.limit, 0)]:
        print(f"{score:>3}  {relative}  [{', '.join(sorted(words))}]")
    if not ranked:
        print("  none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
