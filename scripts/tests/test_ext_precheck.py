"""Tests for scripts/ext_precheck.py (T71). Run: python3 -m unittest scripts/tests/test_ext_precheck.py"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ext_precheck  # noqa: E402

LOG = """---
date: 2026-11-28
tool: gemini-cli/gemini-4
branches:
  - vehicle-server:ext/gemini-a
  - vehicle-mcp:ext/gemini-b   # comment
review: pending
---
body
"""


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def commit(repo: Path, name: str, msg: str) -> None:
    (repo / name).write_text(name)
    sh(repo, "add", name)
    sh(repo, "commit", "-q", "-m", msg)


def make_repo(root: Path, name: str) -> Path:
    repo = root / name
    repo.mkdir()
    sh(repo, "init", "-q", "-b", "main")
    sh(repo, "config", "user.email", "t@example.invalid")
    sh(repo, "config", "user.name", "t")
    commit(repo, "README.md", "chore: init")
    sh(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


class ParseBranches(unittest.TestCase):
    def test_block_inline_and_none(self) -> None:
        self.assertEqual(ext_precheck.parse_branches(LOG), ["vehicle-server:ext/gemini-a", "vehicle-mcp:ext/gemini-b"])
        self.assertEqual(ext_precheck.parse_branches("---\nbranches: [a:b, c:d]\n---\n"), ["a:b", "c:d"])
        self.assertEqual(ext_precheck.parse_branches("no front matter"), [])


class Trailer(unittest.TestCase):
    def test_with_and_without(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(Path(d), "r")
            sh(repo, "checkout", "-q", "-b", "ext/gemini-a")
            commit(repo, "a.txt", "feat: a\n\nAI-Agent: gemini-cli/gemini-4")
            self.assertTrue(ext_precheck.check_trailer(repo, "origin/main")[0])
            commit(repo, "b.txt", "feat: b")
            ok, msgs = ext_precheck.check_trailer(repo, "origin/main")
            self.assertFalse(ok)
            self.assertIn("feat: b", "\n".join(msgs))

    def test_merge_commit_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(Path(d), "r")
            sh(repo, "checkout", "-q", "-b", "ext/x")
            commit(repo, "a.txt", "feat: a\n\nAI-Agent: opencode/deepseek-v3")
            sh(repo, "checkout", "-q", "main")
            commit(repo, "m.txt", "chore: m")
            sh(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
            sh(repo, "checkout", "-q", "ext/x")
            sh(repo, "merge", "-q", "--no-ff", "-m", "Merge main", "main")
            self.assertTrue(ext_precheck.check_trailer(repo, "origin/main")[0])

    def test_malformed_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = make_repo(Path(d), "r")
            sh(repo, "checkout", "-q", "-b", "ext/x")
            commit(repo, "a.txt", "feat: a\n\nAI-Agent: gemini")
            self.assertFalse(ext_precheck.check_trailer(repo, "origin/main")[0])


class Log(unittest.TestCase):
    def test_on_main_on_ext_branch_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = make_repo(Path(d), "ws")
            (ws / "external-ai/log").mkdir(parents=True)
            self.assertFalse(ext_precheck.check_log(ws, "vehicle-server", "ext/gemini-a")[0])
            sh(ws, "checkout", "-q", "-b", "ext/gemini-a-log")
            (ws / "external-ai/log/2026-11-28-gemini-a.md").write_text(LOG)
            sh(ws, "add", "-A")
            sh(ws, "commit", "-q", "-m", "docs(log): a")
            sh(ws, "update-ref", "refs/remotes/origin/ext/gemini-a-log", "HEAD")
            self.assertTrue(ext_precheck.check_log(ws, "vehicle-server", "ext/gemini-a")[0])
            self.assertFalse(ext_precheck.check_log(ws, "vehicle-server", "ext/other")[0])
            self.assertFalse(ext_precheck.check_log(ws, "vehicle-ml", "ext/gemini-a")[0])
            sh(ws, "checkout", "-q", "main")
            sh(ws, "merge", "-q", "--ff-only", "ext/gemini-a-log")
            sh(ws, "update-ref", "refs/remotes/origin/main", "HEAD")
            sh(ws, "update-ref", "-d", "refs/remotes/origin/ext/gemini-a-log")
            self.assertTrue(ext_precheck.check_log(ws, "vehicle-mcp", "ext/gemini-b")[0])


if __name__ == "__main__":
    unittest.main()
