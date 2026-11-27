#!/usr/bin/env python3
"""CI pre-checks for branches of non-Claude AI tools (`ext/**`, D-071, T71).

Run by .github/workflows/ext-precheck.yml in the caller repo's CI so that Claude's review
starts from a green baseline. Stdlib only; every check can also be run locally.

Checks:
  zones    scripts/check_zones.py on the caller diff vs the base ref: red fails; yellow passes
           with a warning and, on a pull request, needs the label `needs-claude-review`.
  trailer  every non-merge commit in <base>..HEAD carries `AI-Agent: <tool>/<model>`.
  log      an external-ai/log/*.md whose front matter `branches:` lists `<repo>:<branch>` exists
           on workspace main or on an origin/ext/* branch of the workspace.

Usage:
    python3 scripts/ext_precheck.py --repo vehicle-server --caller-dir . --branch ext/gemini-x
Exit code 0 = all checks passed, 1 = at least one failed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LABEL = "needs-claude-review"
TRAILER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._:+-]*$")
LOG_DIR = "external-ai/log"
HERE = Path(__file__).resolve().parent


def git(cwd: Path, *args: str, check: bool = True) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout


def parse_branches(text: str) -> list[str]:
    """The `branches:` list of a log's front matter (inline `[a, b]` or block `- a` form)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    out: list[str] = []
    in_list = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if in_list:
            m = re.match(r"^\s+-\s+(\S+)", line)
            if m:
                out.append(m.group(1).strip("'\""))
                continue
            if line.strip() and not line.startswith((" ", "\t")):
                in_list = False
        m = re.match(r"^branches:\s*(.*?)\s*(#.*)?$", line)
        if m:
            rest = m.group(1)
            if rest.startswith("["):
                out += [b.strip().strip("'\"") for b in rest.strip("[]").split(",") if b.strip()]
            elif not rest:
                in_list = True
    return out


# ---- zones -------------------------------------------------------------------------------


def check_zones(caller: Path, base: str, workspace: Path, event: dict | None) -> tuple[bool, list[str]]:
    res = subprocess.run(
        [sys.executable, str(workspace / "scripts" / "check_zones.py"), str(caller), "--base", base],
        capture_output=True, text=True, check=False,
    )
    msgs = [res.stdout.rstrip()]
    if res.returncode == 0:
        return True, msgs
    if res.returncode == 2:
        msgs.append("::error::red-zone path(s) touched: Claude-only (external-ai/zones.json); revert them")
        return False, msgs
    if res.returncode == 1:
        msgs.append("::warning::yellow-zone path(s) touched: the change needs a Claude review")
        if event and event.get("pull_request"):
            labels = {lb.get("name") for lb in event["pull_request"].get("labels", [])}
            if LABEL not in labels:
                msgs.append(f"::error::yellow zone: add the label `{LABEL}` to this pull request")
                return False, msgs
        return True, msgs
    msgs.append(f"::error::check_zones.py failed: {res.stderr.strip()}")
    return False, msgs


# ---- trailer -----------------------------------------------------------------------------


def check_trailer(caller: Path, base: str) -> tuple[bool, list[str]]:
    out = git(caller, "log", "--no-merges", f"{base}..HEAD", "--format=%H%x1f%s%x1f%(trailers:key=AI-Agent,valueonly,separator=%x2C)%x1e")
    bad: list[str] = []
    n = 0
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        n += 1
        sha, subject, value = (rec.split("\x1f") + ["", ""])[:3]
        value = value.strip()
        if not value or not all(TRAILER_RE.match(v.strip()) for v in value.split(",")):
            bad.append(f"{sha[:10]} {subject}  (trailer: {value or 'missing'})")
    if bad:
        return False, [f"::error::{len(bad)} of {n} commit(s) lack a valid `AI-Agent: <tool>/<model>` trailer:"] + [f"  {b}" for b in bad]
    return True, [f"{n} commit(s), all carry an AI-Agent trailer"]


# ---- log ---------------------------------------------------------------------------------


def find_log(workspace: Path, repo: str, branch: str) -> str | None:
    """Name `<ref>:<file>` of a log listing `<repo>:<branch>`, or None."""
    want = f"{repo}:{branch}"
    refs = ["origin/main"]
    refs += git(workspace, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/ext/", check=False).split()
    for ref in refs:
        files = git(workspace, "ls-tree", "--name-only", ref, f"{LOG_DIR}/", check=False).split("\n")
        for f in files:
            if not f.endswith(".md") or f.endswith("/TEMPLATE.md"):
                continue
            if want in parse_branches(git(workspace, "show", f"{ref}:{f}", check=False)):
                return f"{ref}:{f}"
    return None


def check_log(workspace: Path, repo: str, branch: str) -> tuple[bool, list[str]]:
    found = find_log(workspace, repo, branch)
    if found:
        return True, [f"session log: {found}"]
    return False, [
        f"::error::no session log lists `{repo}:{branch}` under `branches:` (vehicle-workspace main or an ext/* log branch). "
        f"Copy {LOG_DIR}/TEMPLATE.md to {LOG_DIR}/YYYY-MM-DD-<tool>-<topic>.md, set `branches:` and push it (AGENTS.md section 5)."
    ]


# ---- main --------------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="caller repo name, e.g. vehicle-server")
    ap.add_argument("--caller-dir", default=".", type=Path, help="checkout of the caller repo (full history)")
    ap.add_argument("--workspace-dir", default=HERE.parent, type=Path, help="checkout of vehicle-workspace (full history)")
    ap.add_argument("--branch", default=os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or "")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--event-file", default=os.environ.get("GITHUB_EVENT_PATH"), help="GitHub event payload (labels)")
    args = ap.parse_args()

    if not args.branch.startswith("ext/"):
        print(f"{args.branch or '(no branch)'} is not an ext/ branch: nothing to check")
        return 0
    event = json.loads(Path(args.event_file).read_text()) if args.event_file and Path(args.event_file).is_file() else None

    results = {
        "zones": check_zones(args.caller_dir, args.base, args.workspace_dir, event),
        "trailer": check_trailer(args.caller_dir, args.base),
        "log": check_log(args.workspace_dir, args.repo, args.branch),
    }
    failed = False
    for name, (ok, msgs) in results.items():
        print(f"::group::{name}: {'PASS' if ok else 'FAIL'}")
        print("\n".join(m for m in msgs if m))
        print("::endgroup::")
        failed |= not ok
    print("\n".join(f"{n:8} {'PASS' if ok else 'FAIL'}" for n, (ok, _) in results.items()))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
