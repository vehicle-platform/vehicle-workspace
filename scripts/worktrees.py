#!/usr/bin/env python3
"""Track and clean up the git worktrees of the workspace and the platform repos.

Claude sessions work in `<repo>/.claude/worktrees/<name>` on a `claude/<name>`
branch. Once that branch is merged the worktree is dead weight (disk, a stale
copy to edit by mistake, `?? .claude/worktrees/` noise in `git status`). This
script derives each worktree's state from git and GitHub and writes the
report to WORKTREES.md (gitignored, regenerated on every run, never edited).

A worktree is removable only when all of these hold:
- its branch is merged (an ancestor of origin/main, or its PR is MERGED),
- `git status` is clean, submodules included (ignored files such as .venv or
  build/ do not count),
- it has no commits that exist neither on origin/main nor on its remote branch.

Usage:
    python3 scripts/worktrees.py           # write WORKTREES.md and print it
    python3 scripts/worktrees.py --check   # same, exit 1 if anything is removable
    python3 scripts/worktrees.py --prune   # remove removable worktrees + their local branches
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from _common import ROOT, git as _git, repos, worktree_list

REPORT = ROOT / "WORKTREES.md"
EXCLUDE_LINE = ".claude/worktrees/"


def git(repo: Path, *args: str, check: bool = True) -> str:
    return _git(repo, *args, check=check)


def repo_slug(repo: Path) -> str:
    return "vehicle-workspace" if repo == ROOT else repo.name


def ensure_excluded(repo: Path) -> None:
    """Hide .claude/worktrees/ from `git status` locally (.git/info/exclude, not committed)."""
    exclude = Path(git(repo, "rev-parse", "--git-path", "info/exclude"))
    if not exclude.is_absolute():
        exclude = repo / exclude
    text = exclude.read_text() if exclude.exists() else ""
    if EXCLUDE_LINE not in text.splitlines():
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(text + ("" if text.endswith("\n") or not text else "\n") + EXCLUDE_LINE + "\n")


def pr_for(slug: str, branch: str) -> tuple[str, str]:
    """(number, state) of the newest PR from this branch, or ("", "") if none / gh unavailable."""
    try:
        out = subprocess.run(
            ["gh", "pr", "list", "-R", f"vehicle-platform/{slug}", "--head", branch, "--state", "all",
             "--json", "number,state", "--limit", "1"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "", ""
    if out.returncode != 0 or not out.stdout.strip():
        return "", ""
    prs = json.loads(out.stdout)
    return (str(prs[0]["number"]), prs[0]["state"]) if prs else ("", "")


@dataclass
class Worktree:
    repo: Path
    path: Path
    branch: str
    pr: str
    pr_state: str
    last_commit: str
    verdict: str
    reason: str

    @property
    def removable(self) -> bool:
        return self.verdict == "remove"


def in_origin_main(cwd: Path, rev: str) -> bool:
    return subprocess.run(["git", "-C", str(cwd), "merge-base", "--is-ancestor", rev, "origin/main"],
                          capture_output=True).returncode == 0


def inspect(repo: Path, path: Path, branch: str) -> Worktree:
    slug = repo_slug(repo)
    pr, pr_state = pr_for(slug, branch) if branch else ("", "")
    last = git(path, "log", "-1", "--format=%cs", check=False) if path.exists() else ""

    def wt(verdict: str, reason: str) -> Worktree:
        return Worktree(repo, path, branch or "(detached)", pr, pr_state, last, verdict, reason)

    if not path.exists():
        # Only the stale worktree record is pruned; the branch (and its commits) is kept unless
        # it is already contained in origin/main (checked again in prune()).
        return wt("prune-record", "directory is gone (record only, branch kept unless merged)")
    if not branch:
        return wt("keep", "detached HEAD, check by hand")
    dirty = git(path, "status", "--porcelain", "--ignore-submodules=none", check=False)
    if dirty:
        return wt("keep", f"{len(dirty.splitlines())} uncommitted change(s)")
    remote_ref = f"origin/{branch}"
    has_remote = git(repo, "rev-parse", "--verify", "--quiet", remote_ref, check=False) != ""
    unpushed_range = ["HEAD", "^origin/main"] + ([f"^{remote_ref}"] if has_remote else [])
    unpushed = git(path, "rev-list", "--count", *unpushed_range, check=False)
    head_in_main = in_origin_main(path, "HEAD")
    if unpushed not in ("", "0") and not head_in_main:
        return wt("keep", f"{unpushed} commit(s) not pushed")
    if pr_state == "MERGED" and head_in_main:
        return wt("remove", "merged, clean")
    if pr_state == "MERGED":
        return wt("review", "PR merged but the branch has commits that are not in origin/main")
    if pr_state == "OPEN":
        return wt("keep", "PR open")
    if pr_state == "CLOSED":
        return wt("review", "PR closed without merge")
    if head_in_main:
        # A worktree just created from origin/main (e.g. a subagent about to start) looks exactly
        # like this; never auto-remove it.
        return wt("keep", "no commits beyond origin/main and no PR (fresh or abandoned)")
    return wt("keep", "no PR yet")


def collect() -> list[Worktree]:
    found: list[Worktree] = []
    for repo in repos():
        ensure_excluded(repo)
        git(repo, "fetch", "--quiet", "--prune", "origin", check=False)
        for path, branch in worktree_list(repo, check=True)[1:]:  # the first entry is the main checkout
            found.append(inspect(repo, path, branch))
    return found


def render(items: list[Worktree]) -> str:
    lines = [
        "# WORKTREES — generated by `python3 scripts/worktrees.py`, do not edit",
        "",
        f"Generated {date.today().isoformat()}. `--prune` removes the rows marked **remove**.",
        "",
    ]
    if not items:
        return "\n".join(lines + ["No worktrees besides the main checkouts.", ""])
    lines += ["| Repo | Worktree | Branch | PR | Last commit | Verdict | Why |",
              "|---|---|---|---|---|---|---|"]
    for w in items:
        pr = f"#{w.pr} {w.pr_state.lower()}" if w.pr else "—"
        verdict = f"**{w.verdict}**" if w.removable or w.verdict == "prune-record" else w.verdict
        lines.append(f"| {repo_slug(w.repo)} | `{w.path.relative_to(w.repo) if w.path.is_relative_to(w.repo) else w.path}` "
                     f"| `{w.branch}` | {pr} | {w.last_commit or '—'} | {verdict} | {w.reason} |")
    return "\n".join(lines + [""])


def prune(items: list[Worktree]) -> None:
    for w in items:
        if w.verdict == "prune-record":
            git(w.repo, "worktree", "prune")
            print(f"pruned stale record {repo_slug(w.repo)}: {w.path.name} ({w.branch})")
        elif not w.removable:
            continue
        else:
            # --force: clean state was verified above; plain remove refuses worktrees with submodules.
            git(w.repo, "worktree", "remove", "--force", str(w.path), check=False)
            git(w.repo, "worktree", "prune")
            print(f"removed {repo_slug(w.repo)}: {w.path.name} ({w.branch})")
        # Delete the local branch only when every commit on it is in origin/main.
        if w.branch != "(detached)" and in_origin_main(w.repo, f"refs/heads/{w.branch}"):
            git(w.repo, "branch", "-D", w.branch, check=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if a worktree is removable")
    mode.add_argument("--prune", action="store_true", help="remove removable worktrees and their local branches")
    args = ap.parse_args()

    items = collect()
    if args.prune:
        prune(items)
        items = collect()
    report = render(items)
    REPORT.write_text(report)
    print(report)
    if args.check and any(w.removable or w.verdict == "prune-record" for w in items):
        print("Removable worktrees found: run `python3 scripts/worktrees.py --prune`.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
