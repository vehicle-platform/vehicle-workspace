#!/usr/bin/env python3
"""Write a VS Code multi-root workspace that shows every repo and every agent worktree.

Claude Code works in `<repo>/.claude/worktrees/<topic>` (gitignored, three levels
deep), so VS Code's Source Control view and GitLens never open those checkouts on
their own. External AI tools (D-071) switch a main clone to an `ext/<tool>-<topic>`
branch. This script lists the workspace, the cloned platform repos and every linked
worktree as separate workspace folders, named after the agent that owns the branch,
and writes `vehicle-platform.code-workspace` (gitignored) in the main workspace
checkout. VS Code reloads the folder list when the file changes.

Folder names: `🤖 rt-core ⎇ claude/<topic>` (Claude Code), `🐋 server ⎇ ext/opencode-<topic>`
(DeepSeek via opencode), `✳️` for other external tools, plain `rt-core · main` otherwise.
Agent work is listed first. The file is rewritten only when its content changes.

Usage:
    python3 scripts/vscode_workspace.py          # write the file and print the folders
    python3 scripts/vscode_workspace.py --quiet  # write silently
    python3 scripts/vscode_workspace.py --hook   # Claude Code PostToolUse hook: reads the
                                                 # hook JSON on stdin, runs only after git
                                                 # worktree/checkout/switch commands
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
# The main workspace checkout, also when this script runs from a workspace worktree.
ROOT = Path(subprocess.run(["git", "-C", str(_HERE), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                           capture_output=True, text=True, check=True).stdout.strip()).parent
OUT = ROOT / "vehicle-platform.code-workspace"
HOOK_PATTERN = re.compile(r"\bgit\b.*\b(worktree|checkout|switch)|worktrees\.py")

SETTINGS = {
    # Each repo and worktree is its own folder; submodules (external/vehicle-defs in every
    # consumer) would add a dozen identical defs repos to Source Control.
    "git.detectSubmodules": False,
    "git.repositoryScanMaxDepth": 1,
    "git.detectWorktrees": True,
    "git.autofetch": True,
    "git.blame.editorDecoration.enabled": True,
    "git.blame.statusBarItem.enabled": True,
    "scm.alwaysShowRepositories": True,
    "scm.repositories.visible": 30,
    # The root folder holds the repos and every repo holds its worktrees; both are
    # shown as their own folders, so hide the nested copies from the explorer and search.
    "files.exclude": {"vehicle-*": True, "**/.claude/worktrees": True},
    "search.exclude": {"vehicle-*": True, "**/.claude/worktrees": True},
}


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def repos() -> list[Path]:
    return [ROOT] + sorted(p for p in ROOT.glob("vehicle-*") if (p / ".git").exists())


def short(repo: Path) -> str:
    return "workspace" if repo == ROOT else repo.name.removeprefix("vehicle-")


def owner_mark(branch: str) -> str:
    if branch.startswith("claude/"):
        return "🤖"
    if branch.startswith(("ext/opencode-", "ext/deepseek-")):
        return "🐋"
    if branch.startswith("ext/"):
        return "✳️"
    return ""


def worktrees(repo: Path) -> list[tuple[Path, str]]:
    """(path, branch) for every checkout of `repo`, main clone first."""
    result: list[tuple[Path, str]] = []
    path: Path | None = None
    branch = ""
    for line in git(repo, "worktree", "list", "--porcelain").splitlines() + [""]:
        if line.startswith("worktree "):
            path = Path(line.removeprefix("worktree "))
        elif line.startswith("branch "):
            branch = line.removeprefix("branch refs/heads/")
        elif line == "detached":
            branch = "(detached)"
        elif not line and path is not None:
            if path.exists():
                result.append((path, branch))
            path, branch = None, ""
    return result


def build() -> dict:
    agent: list[dict] = []
    plain: list[dict] = []
    for repo in repos():
        for index, (path, branch) in enumerate(worktrees(repo)):
            mark = owner_mark(branch)
            rel = os.path.relpath(path, ROOT)
            if index == 0:
                folder = {"name": f"{mark + ' ' if mark else ''}{short(repo)} · {branch}", "path": rel}
                (agent if mark else plain).append(folder)
            else:
                agent.append({"name": f"{mark or '⎇'} {short(repo)} ⎇ {branch}", "path": rel})
    # The workspace root stays first so the shared scripts and STATUS.md are at the top.
    root = [f for f in plain if f["path"] == "."]
    rest = [f for f in plain if f["path"] != "."]
    return {
        "folders": root + agent + rest,
        "settings": SETTINGS,
        "extensions": {"recommendations": ["eamodio.gitlens"]},
        "tasks": {
            "version": "2.0.0",
            "tasks": [{
                "label": "Refresh agent worktree folders",
                "type": "shell",
                "command": "python3 scripts/vscode_workspace.py",
                "options": {"cwd": "${workspaceFolder:" + root[0]["name"] + "}"} if root else {},
                "problemMatcher": [],
            }],
        },
    }


def write(quiet: bool) -> None:
    content = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
        OUT.write_text(content, encoding="utf-8")
    if not quiet:
        print(OUT)
        for folder in json.loads(content)["folders"]:
            print(f"  {folder['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--quiet", action="store_true", help="write without printing")
    parser.add_argument("--hook", action="store_true", help="Claude Code PostToolUse mode (stdin JSON)")
    args = parser.parse_args()
    if args.hook:
        try:
            command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
        except (json.JSONDecodeError, AttributeError):
            return 0
        if not HOOK_PATTERN.search(command):
            return 0
        try:
            write(quiet=True)
        except OSError:
            pass  # a hook never fails the tool call
        return 0
    write(quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
