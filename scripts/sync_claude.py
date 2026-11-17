#!/usr/bin/env python3
"""Copy shared Claude Code assets from vehicle-workspace into each platform repo.

Single-repo cloud sessions only see the repo they clone, so every repo carries
copies of PLATFORM-RULES.md and the agents/skills relevant to it. The source of
truth is this workspace; copies are overwritten and must not be edited in place.

It also renders AGENTS.md and GEMINI.md (rules for AI tools other than Claude
Code, D-071) from external-ai/AGENTS.base.md, external-ai/zones.json and
PLATFORM-RULES.md, into the workspace root and every repo.

Usage:
    python3 scripts/sync_claude.py            # write copies
    python3 scripts/sync_claude.py --check    # exit 1 if any copy is missing/stale
    python3 scripts/sync_claude.py --workspace                 # AGENTS.md/GEMINI.md at the root only
    python3 scripts/sync_claude.py vehicle-server --into <worktree>  # one repo, into its worktree
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- Synced from vehicle-workspace/{src} by scripts/sync_claude.py. Do not edit here; edit the source and re-run the sync. -->"
IMPORT_LINE = "@.claude/PLATFORM-RULES.md"
LEDGER = ".claude/.synced"  # list of files this script owns in the repo

COMMON_AGENTS = ["docs-researcher", "vss-schema-guardian", "architecture-guard"]
SAFETY_AGENTS = COMMON_AGENTS + ["safety-reviewer"]
FIRMWARE = {"agents": SAFETY_AGENTS, "skills": ["repo-bootstrap", "feature-module"]}
SOFTWARE = {"agents": COMMON_AGENTS, "skills": ["repo-bootstrap"]}
# Software repos with invariant-8 code: linux-node's OTA, server's OTA packages (ISSUES C-3)
SAFETY_SOFTWARE = {"agents": SAFETY_AGENTS, "skills": ["repo-bootstrap"]}

REPO_ASSETS: dict[str, dict[str, list[str]]] = {
    "vehicle-defs": {"agents": COMMON_AGENTS, "skills": ["signal-change", "repo-bootstrap"]},
    "vehicle-rt-core": FIRMWARE,
    "vehicle-safety-node": FIRMWARE,
    "vehicle-io-node": FIRMWARE,
    "vehicle-hil-bench": FIRMWARE,
    "vehicle-connectivity-node": FIRMWARE,  # temporary sole vehicle-bus tester (D-023): tester latch
    "vehicle-linux-node": SAFETY_SOFTWARE,
    "vehicle-mcp": SOFTWARE,
    "vehicle-server": SAFETY_SOFTWARE,
    "vehicle-ml": SOFTWARE,
    "vehicle-mobile": SOFTWARE,
    "vehicle-analyzer": SAFETY_SOFTWARE,  # listen-only adapters and HAL (D-081)
}


def ledger_entry_is_safe(repo_dir: Path, rel: str) -> bool:
    """A stale ledger entry may only name a file this script can own: under the repo's
    `.claude/` or one of the rendered root files, never absolute or escaping the repo."""
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return False
    target = (repo_dir / rel).resolve()
    root = repo_dir.resolve()
    if not target.is_relative_to(root):
        return False
    return target.is_relative_to(root / ".claude") or rel in ("AGENTS.md", "GEMINI.md")


def with_marker(text: str, src: str) -> str:
    """Insert the marker after YAML frontmatter (or at the top if there is none)."""
    marker = MARKER.format(src=src)
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4) + 5
        return text[:end] + "\n" + marker + "\n" + text[end:]
    return marker + "\n\n" + text


def zones_summary() -> str:
    """One line per repo: its red/yellow/green globs, in rule order (first match wins)."""
    rules = json.loads((ROOT / "external-ai" / "zones.json").read_text())["rules"]
    order: list[str] = []
    groups: dict[str, dict[str, list[str]]] = {}
    default: dict[str, str] = {}
    for rule in rules:
        repo = rule["repo"]
        if repo == "*" and rule["glob"] == "*":
            continue  # the catch-all, stated in the last line
        if repo not in groups:
            order.append(repo)
            groups[repo] = {"red": [], "yellow": [], "green": []}
        if rule["glob"] == "*":
            default[repo] = rule["zone"]
        else:
            groups[repo][rule["zone"]].append(f"`{rule['glob']}`")
    lines = []
    for repo in order:
        label = "All repos (checked first)" if repo == "*" else repo
        parts = [f"{zone}: {', '.join(globs)}" for zone, globs in groups[repo].items() if globs]
        if repo in default:
            parts.append(f"{'everything else' if parts else 'everything'}: **{default[repo]}**")
        lines.append(f"- **{label}** — " + "; ".join(parts))
    lines.append("- Unlisted repos and paths: yellow. Where two globs match, the more specific one listed first in")
    lines.append("  `external-ai/zones.json` wins (e.g. `docs/ideas/*` before `docs/*`); the file also gives each rule's reason.")
    return "\n".join(lines)


def agents_md() -> str:
    """AGENTS.md for non-Claude AI tools: base text + zone summary + PLATFORM-RULES.md."""
    base = (ROOT / "external-ai" / "AGENTS.base.md").read_text()
    rules = (ROOT / "PLATFORM-RULES.md").read_text().splitlines()
    body = [("#" + line) if line.startswith("## ") else line for line in rules[1:]]  # drop title, demote
    text = base.replace("{{ZONES}}", zones_summary())
    return text.replace("{{PLATFORM_RULES}}", "\n".join(body).strip() + "\n")


def agent_files() -> dict[str, str]:
    src = "external-ai/AGENTS.base.md"
    content = with_marker(agents_md(), src)
    return {"AGENTS.md": content, "GEMINI.md": content}


def planned_files(repo: str) -> dict[str, str]:
    """Map repo-relative destination path -> file content."""
    files: dict[str, str] = dict(agent_files())
    rules = (ROOT / "PLATFORM-RULES.md").read_text()
    files[".claude/PLATFORM-RULES.md"] = with_marker(rules, "PLATFORM-RULES.md")
    assets = REPO_ASSETS[repo]
    for name in assets["agents"]:
        src = f".claude/agents/{name}.md"
        files[src] = with_marker((ROOT / src).read_text(), src)
    for name in assets["skills"]:
        src = f".claude/skills/{name}/SKILL.md"
        files[src] = with_marker((ROOT / src).read_text(), src)
    return files


def claude_md_with_import(text: str) -> str:
    if IMPORT_LINE in text:
        return text
    lines = text.splitlines(keepends=True)
    # keep the "# CLAUDE.md — <repo>" title first, import right below it
    return lines[0] + "\n" + IMPORT_LINE + "\n" + "".join(lines[1:])


def sync_repo(repo: str, check: bool, repo_dir: Path | None = None) -> list[str]:
    repo_dir = repo_dir or ROOT / repo
    if not repo_dir.is_dir():
        return [f"{repo}: not cloned (run ./setup.sh)"]
    problems: list[str] = []
    files = planned_files(repo)

    ledger_path = repo_dir / LEDGER
    previous = set(ledger_path.read_text().split()) if ledger_path.exists() else set()
    stale = sorted(previous - set(files))

    for rel, content in files.items():
        dest = repo_dir / rel
        if dest.exists() and dest.read_text() == content:
            continue
        problems.append(f"{repo}: {rel} {'stale' if dest.exists() else 'missing'}")
        if not check:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)

    for rel in stale:
        if not ledger_entry_is_safe(repo_dir, rel):
            # The ledger lives in the target repo and could be edited by anyone with commit
            # access there: never let it point the cleanup outside the files this script owns.
            problems.append(f"{repo}: ledger entry {rel!r} refused (outside .claude/ or the rendered files)")
            continue
        problems.append(f"{repo}: {rel} no longer mapped")
        if not check:
            (repo_dir / rel).unlink(missing_ok=True)

    claude_md = repo_dir / "CLAUDE.md"
    if claude_md.exists():
        text = claude_md.read_text()
        if IMPORT_LINE not in text:
            problems.append(f"{repo}: CLAUDE.md lacks {IMPORT_LINE}")
            if not check:
                claude_md.write_text(claude_md_with_import(text))

    ledger = "\n".join(sorted(files)) + "\n"
    if not check and (not ledger_path.exists() or ledger_path.read_text() != ledger):
        ledger_path.write_text(ledger)
    return problems


def sync_workspace(check: bool) -> list[str]:
    """AGENTS.md / GEMINI.md at the workspace root (committed in vehicle-workspace)."""
    problems: list[str] = []
    for rel, content in agent_files().items():
        dest = ROOT / rel
        if dest.exists() and dest.read_text() == content:
            continue
        problems.append(f"vehicle-workspace: {rel} {'stale' if dest.exists() else 'missing'}")
        if not check:
            dest.write_text(content)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report drift, write nothing")
    parser.add_argument("--workspace", action="store_true", help="only AGENTS.md/GEMINI.md at the workspace root")
    parser.add_argument("--into", type=Path, help="write the one named repo's copies into this directory (e.g. its worktree)")
    parser.add_argument("repos", nargs="*", help="limit to these repos (default: all)")
    args = parser.parse_args()
    if args.into and len(args.repos) != 1:
        parser.error("--into needs exactly one repo")

    unknown = set(args.repos) - set(REPO_ASSETS)
    if unknown:
        parser.error(f"unknown repo(s): {', '.join(sorted(unknown))}")

    problems: list[str] = [] if args.repos else sync_workspace(args.check)
    for repo in [] if args.workspace else (args.repos or REPO_ASSETS):
        problems += sync_repo(repo, args.check, args.into.resolve() if args.into else None)

    for p in problems:
        print(("DRIFT " if args.check else "synced ") + p)
    if not problems:
        print("all repos in sync")
    return 1 if (args.check and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
