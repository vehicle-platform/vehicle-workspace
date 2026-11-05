---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-17-d079-health-windows
repos: [vehicle-workspace, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-17-log, vehicle-server:ext/opencode-server-health-windows]
prs: []
zone: green
review: pending
---

# DeepSeek long run 17 — D-079 health windows in the vehicle-server reference

## Goal
Implement the D-079 health-window state machine and the 17 ready window summaries in
vehicle-server, with the workspace log first (LR17-0) and last (LR17-6), and document the
provisional reference rules. Grid-connect via the existing class-B machinery only.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-05-opencode-long-run-17.md`: this session log.
- `vehicle-server/src/vehicle_server/derived/health_windows.py`: pure D-079 window state
  machine (conditions, stable bands, max duration, key-on/engine transitions, re-arm, session
  end, first qualifying instance and count). Definitions come from `WINDOWS`; no signal-name,
  threshold or duration literals.
- `vehicle-server/tests/test_health_windows.py`: synthetic tests for every `opens_on` kind,
  flicker re-arm, stable break, max-duration close/re-arm, stale input, session end, min
  duration boundary, engine-start consecutive samples, unknown trigger and a patched threshold.

## Result
In progress. Task list:

- [x] LR17-0 — log first
- [x] LR17-1 — pure state machine `derived/health_windows.py` + unit tests
- [ ] LR17-2 — window signals in `derived/health_window_summaries.py`, golden skip, tests
- [ ] LR17-3 — synthetic ingest + API/CLI end to end
- [ ] LR17-4 — README "D-079 health windows" subsection
- [ ] LR17-5 — full checks, zone check, open one server PR (do not merge)
- [ ] LR17-6 — close the log

## Checks
- `uv run pytest tests/test_health_windows.py -q`: pass (11 tests).
- `uv run ruff check src/vehicle_server/derived/health_windows.py tests/test_health_windows.py`:
  pass.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: green (two files).

## Unsure about
- The task file was requested from `main`, but it is not on `origin/main`; it exists only on
  `claude/lr17-task` (`5fd4083`) and in `.claude/worktrees/lr17-task/`. I read it from the
  worktree and did not edit it.
- The full pre-start reading (section 0) was completed before code.

## For Claude
- Task-file location conflict: `external-ai/tasks/2026-11-05-deepseek-long-run-17.md` is absent
  from `main`; the run uses the `claude/lr17-task` copy.
- Will list the two W4 cruise residuals and the proposed `CLAUDE.md` line here when LR17-4/6 are
  done.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
