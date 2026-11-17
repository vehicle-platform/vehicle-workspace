"""Tests for the workspace scripts (audit B-1, B-2, B-3, B-9). Run: python3 -m pytest scripts/tests"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_zones  # noqa: E402
import sync_claude  # noqa: E402
import worktrees  # noqa: E402


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo_with_origin(tmp_path: Path) -> Path:
    """A clone of a bare origin with one commit on main and origin/main fetched."""
    origin = tmp_path / "origin.git"
    sh(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    repo = tmp_path / "repo"
    sh(tmp_path, "clone", "-q", str(origin), str(repo))
    sh(repo, "config", "user.email", "t@example.invalid")
    sh(repo, "config", "user.name", "t")
    sh(repo, "checkout", "-q", "-b", "main")
    (repo / "README.md").write_text("x\n")
    sh(repo, "add", "README.md")
    sh(repo, "commit", "-q", "-m", "init")
    sh(repo, "push", "-q", "origin", "main")
    sh(repo, "fetch", "-q", "origin")
    return repo


# --- B-1: check_zones must see raw path names --------------------------------------------

def test_porcelain_z_keeps_spaces_non_ascii_and_both_rename_names() -> None:
    out = "?? .claude/evil file.md\0 M src/é.c\0R  new name.c\0old name.c\0"
    assert check_zones.parse_porcelain_z(out) == {".claude/evil file.md", "src/é.c", "new name.c", "old name.c"}


def test_changed_paths_are_unquoted(repo_with_origin: Path) -> None:
    (repo_with_origin / ".claude").mkdir()
    (repo_with_origin / ".claude" / "evil file.md").write_text("x")
    (repo_with_origin / "é.md").write_text("x")
    paths = check_zones.changed_paths(repo_with_origin, "HEAD")
    assert ".claude/evil file.md" in paths
    assert "é.md" in paths
    assert not any(p.startswith('"') for p in paths)


# --- B-2 / B-3: worktree verdicts never lose work -----------------------------------------

@pytest.fixture
def no_gh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worktrees, "pr_for", lambda slug, branch: ("", ""))


def test_fresh_worktree_is_kept(repo_with_origin: Path, no_gh: None) -> None:
    wt = repo_with_origin.parent / "wt-fresh"
    sh(repo_with_origin, "worktree", "add", "-q", "-b", "claude/fresh", str(wt), "origin/main")
    w = worktrees.inspect(repo_with_origin, wt, "claude/fresh")
    assert w.verdict == "keep" and not w.removable


def test_missing_directory_keeps_unmerged_branch(repo_with_origin: Path, no_gh: None) -> None:
    wt = repo_with_origin.parent / "wt-gone"
    sh(repo_with_origin, "worktree", "add", "-q", "-b", "claude/work", str(wt), "origin/main")
    (wt / "f.txt").write_text("work\n")
    sh(wt, "add", "f.txt")
    sh(wt, "commit", "-q", "-m", "unmerged work")
    subprocess.run(["rm", "-rf", str(wt)], check=True)
    w = worktrees.inspect(repo_with_origin, wt, "claude/work")
    assert w.verdict == "prune-record"
    worktrees.prune([w])
    assert "claude/work" in sh(repo_with_origin, "branch", "--list", "claude/work")


def test_merged_pr_with_commits_after_merge_is_review(repo_with_origin: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worktrees, "pr_for", lambda slug, branch: ("1", "MERGED"))
    wt = repo_with_origin.parent / "wt-after"
    sh(repo_with_origin, "worktree", "add", "-q", "-b", "claude/after", str(wt), "origin/main")
    (wt / "g.txt").write_text("later\n")
    sh(wt, "add", "g.txt")
    sh(wt, "commit", "-q", "-m", "after merge")
    sh(wt, "push", "-q", "origin", "claude/after")
    w = worktrees.inspect(repo_with_origin, wt, "claude/after")
    assert w.verdict == "review"


def test_merged_pr_contained_in_main_is_removed(repo_with_origin: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worktrees, "pr_for", lambda slug, branch: ("1", "MERGED"))
    wt = repo_with_origin.parent / "wt-done"
    sh(repo_with_origin, "worktree", "add", "-q", "-b", "claude/done", str(wt), "origin/main")
    w = worktrees.inspect(repo_with_origin, wt, "claude/done")
    assert w.removable
    worktrees.prune([w])
    assert not wt.exists()
    assert sh(repo_with_origin, "branch", "--list", "claude/done") == ""


# --- B-9: the sync ledger cannot delete outside what the script owns ----------------------

@pytest.mark.parametrize(
    ("rel", "ok"),
    [
        (".claude/agents/x.md", True),
        ("AGENTS.md", True),
        ("GEMINI.md", True),
        ("../outside.txt", False),
        (".claude/../src/main.c", False),
        ("/etc/hosts", False),
        ("src/main.c", False),
        ("", False),
    ],
)
def test_ledger_entry_is_safe(tmp_path: Path, rel: str, ok: bool) -> None:
    (tmp_path / ".claude").mkdir()
    assert sync_claude.ledger_entry_is_safe(tmp_path, rel) is ok
