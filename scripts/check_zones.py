#!/usr/bin/env python3
"""Report which edit zone (external-ai/zones.json, D-071) each changed file falls in.

For non-Claude AI tools and for Claude's review of their work. A red path means
"Claude only": the change must not be committed by another tool.

Usage (from the workspace root):
    python3 scripts/check_zones.py vehicle-server            # changes vs origin/main + uncommitted
    python3 scripts/check_zones.py vehicle-rt-core --base main
    python3 scripts/check_zones.py .                       # the workspace itself
    python3 scripts/check_zones.py vehicle-mobile --path lib/ui/x.dart   # classify paths, no git

The repo name is taken from the `origin` remote, so a worktree under
<repo>/.claude/worktrees/<topic> works too. Exit code: 2 if any path is red,
1 if any is yellow, 0 if all are green (or nothing changed).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZONES = ROOT / "external-ai" / "zones.json"
RANK = {"green": 0, "yellow": 1, "red": 2}


def load_rules() -> list[dict[str, str]]:
    return json.loads(ZONES.read_text())["rules"]


def classify(repo: str, path: str, rules: list[dict[str, str]]) -> tuple[str, str]:
    for rule in rules:
        if fnmatchcase(repo, rule["repo"]) and fnmatchcase(path, rule["glob"]):
            return rule["zone"], rule["why"]
    return "yellow", "no rule matched"


def git(repo_dir: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo_dir, check=True, capture_output=True, text=True
    ).stdout


def repo_name(repo_dir: Path) -> str:
    try:
        url = git(repo_dir, "remote", "get-url", "origin").strip()
    except subprocess.CalledProcessError:
        return repo_dir.resolve().name
    return url.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]


def parse_porcelain_z(out: str) -> set[str]:
    """Paths from `git status --porcelain -z`: raw (never quoted) names; a rename or copy
    entry is followed by its source path as the next NUL-separated field."""
    paths: set[str] = set()
    fields = out.split("\0")
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        paths.add(entry[3:])
        if entry[0] in "RC" or entry[1] in "RC":
            if i < len(fields) and fields[i]:
                paths.add(fields[i])
            i += 1
    return paths


def changed_paths(repo_dir: Path, base: str) -> list[str]:
    # -z everywhere: without it git quotes names with spaces or non-ASCII bytes
    # ("\"a b.md\""), which then never match a zone glob and fall to a weaker zone.
    paths: set[str] = set()
    merge_base = git(repo_dir, "merge-base", base, "HEAD").strip()
    paths.update(git(repo_dir, "diff", "--name-only", "-z", merge_base).split("\0"))
    paths.update(parse_porcelain_z(git(repo_dir, "status", "--porcelain", "-z", "--untracked-files=all")))
    return sorted(p for p in paths if p)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", help="repo directory (relative to the workspace root or absolute)")
    parser.add_argument("--base", default="origin/main", help="compare against this ref (default origin/main)")
    parser.add_argument("--path", nargs="+", help="classify these repo-relative paths instead of git changes")
    args = parser.parse_args()

    repo_dir = Path(args.repo)
    if not repo_dir.is_absolute():
        repo_dir = (Path.cwd() / repo_dir) if (Path.cwd() / repo_dir).is_dir() else ROOT / repo_dir
    if not repo_dir.is_dir():
        parser.error(f"not a directory: {repo_dir}")

    name = repo_name(repo_dir)
    rules = load_rules()
    paths = args.path or changed_paths(repo_dir, args.base)
    if not paths:
        print(f"{name}: no changes against {args.base}")
        return 0

    worst = "green"
    for path in paths:
        zone, why = classify(name, path, rules)
        if RANK[zone] > RANK[worst]:
            worst = zone
        print(f"{zone.upper():6} {name}/{path}  ({why})")

    print()
    if worst == "red":
        print("RED: Claude-only paths are touched. Do not commit them; revert them and describe the")
        print("wanted change under 'For Claude' in your external-ai/log entry.")
    elif worst == "yellow":
        print("YELLOW: allowed, but the PR needs a Claude review (mark it 'needs-claude-review').")
    else:
        print("GREEN: allowed. Log the session in external-ai/log.")
    return RANK[worst]


if __name__ == "__main__":
    sys.exit(main())
