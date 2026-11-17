"""Helpers shared by worktrees.py and vscode_workspace.py (stdlib only)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def find_root(script_dir: Path) -> Path:
    """The main workspace checkout, also when the script runs from a workspace worktree."""
    common = subprocess.run(
        ["git", "-C", str(script_dir), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return Path(common).parent


ROOT = find_root(Path(__file__).resolve().parent)


def git(repo: Path, *args: str, check: bool = False) -> str:
    """Stripped stdout of `git -C repo ...`. Failure gives "" or, with check=True, RuntimeError."""
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if out.returncode != 0:
        if check:
            raise RuntimeError(f"git -C {repo} {' '.join(args)}: {out.stderr.strip()}")
        return ""
    return out.stdout.strip()


def repos() -> list[Path]:
    """The workspace itself plus every cloned platform repo (own .git)."""
    return [ROOT] + sorted(p for p in ROOT.glob("vehicle-*") if (p / ".git").exists())


def worktree_list(repo: Path, check: bool = False) -> list[tuple[Path, str]]:
    """(path, branch) of every checkout of `repo`, main clone first.

    Parsed from `git worktree list --porcelain -z` (NUL-separated, safe for odd paths).
    The branch is "" for a detached or bare entry.
    """
    out = subprocess.run(["git", "-C", str(repo), "worktree", "list", "--porcelain", "-z"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        if check:
            raise RuntimeError(f"git -C {repo} worktree list: {out.stderr.strip()}")
        return []
    result: list[tuple[Path, str]] = []
    path: Path | None = None
    branch = ""
    # Fields end with NUL and each entry ends with an extra NUL, so entries split on an empty field.
    for field in out.stdout.split("\0") + [""]:
        if field.startswith("worktree "):
            path = Path(field.removeprefix("worktree "))
        elif field.startswith("branch "):
            branch = field.removeprefix("branch ").removeprefix("refs/heads/")
        elif not field and path is not None:
            result.append((path, branch))
            path, branch = None, ""
    return result
