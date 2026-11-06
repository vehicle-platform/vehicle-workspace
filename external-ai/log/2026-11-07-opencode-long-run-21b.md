---
date: 2026-11-07
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-21b
repos: [vehicle-workspace, vehicle-rt-core, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-21b-log, vehicle-rt-core:ext/opencode-rtcore-derived-d103]
prs: []
zone: yellow
review: pending
---

# Long run 21b — vehicle-rt-core D-103 class-A signals (rerun)

## Goal
Rerun `external-ai/tasks/2026-11-06-deepseek-long-run-21.md` after rt-core#65: implement the 21
new D-103 class-A derived signals in vehicle-rt-core and resync the golden vectors from
vehicle-defs v0.24.0.

Task list:
- LR21-0: this log on `ext/opencode-long-run-21b-log`.
- LR21-1: baseline build/tests/cppcheck/size and the class-A inventory.
- LR21-2: point and state signals with unit tests.
- LR21-3: window statistics and events with unit tests.
- LR21-4: resync the golden vectors and fix mismatches.
- LR21-5: full CI, size delta, zone check, one PR.
- LR21-6: close this log and refresh the VS Code workspace.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-07-opencode-long-run-21b.md`: this log (LR21-0).

## Result
Precondition passed: `vehicle-rt-core/external/vehicle-defs` describes **v0.24.0** after pulling
rt-core `main` and initialising the submodule.

## Checks
- `git -C vehicle-rt-core/external/vehicle-defs describe --tags`: v0.24.0.
- `git -C vehicle-rt-core status --short --branch`: clean, on `main`.
- `python3 scripts/check_zones.py . --base origin/main`: YELLOW, only because the
  pre-existing `STATUS.md` edit is yellow; this log file itself is GREEN.

## Unsure about
- `STATUS.md` in the workspace is already modified before this run; I did not touch or commit it.

## For Claude
- None yet.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
