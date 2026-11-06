---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-21
repos: [vehicle-workspace, vehicle-rt-core]
branches: [vehicle-workspace:ext/opencode-long-run-21-log]
prs: []
zone: green
review: pending
---

# Long run 21 — vehicle-rt-core D-103 class-A signals

## Goal
Run LR21-0..LR21-6 from `external-ai/tasks/2026-11-06-deepseek-long-run-21.md`: implement the
21 new D-103 class-A derived signals in vehicle-rt-core and resync the golden vectors from
vehicle-defs v0.24.0. The task's precondition must pass first.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-06-opencode-long-run-21.md`: this log (LR21-0).
- No code change: the run stopped at the precondition before creating the rt-core branch.

## Result
**rt-core#65 not merged.** `vehicle-rt-core` `main` was pulled and its submodule initialised, but
`git -C vehicle-rt-core/external/vehicle-defs describe --tags` returns **v0.23.0**, not the
required **v0.24.0**. The task says to stop and end the run in this case.

Task status:
- LR21-0: done (this log, committed and pushed).
- LR21-1..LR21-5: not started; no `ext/opencode-rtcore-derived-d103` branch, no vector or code
  changes.
- LR21-6: closed early with this log because of the precondition.

## Checks
- `git -C vehicle-rt-core status --short --branch`: clean, on `main`.
- `git -C vehicle-rt-core pull --ff-only`: already up to date.
- `git -C vehicle-rt-core submodule update --init`: completed.
- `git -C vehicle-rt-core/external/vehicle-defs describe --tags`: **v0.23.0** (expected v0.24.0;
  stops the run).
- No rt-core tests, build, cppcheck or coverage run: the precondition failed before LR21-1.
- `python3 scripts/vscode_workspace.py`: run from the workspace root.
- `python3 scripts/check_zones.py . --base origin/main`: GREEN (this log file).

## Unsure about
- The task file is not present on workspace `main` after `git pull`; I read it from
  `origin/claude/lr20-task` (`8a6dd89`). I did not merge or modify that branch.

## For Claude
- Merge rt-core#65 (or otherwise pin vehicle-defs v0.24.0 in rt-core `main`) and then rerun
  LR21; the current submodule tag blocks the whole run.
- Decide whether the LR21 task file should land on workspace `main` before the next dispatch; the
  prompt assumes it is there.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
