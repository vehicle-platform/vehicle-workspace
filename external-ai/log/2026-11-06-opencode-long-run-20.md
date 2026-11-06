---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-20
repos: [vehicle-workspace, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-20-log, vehicle-server:ext/opencode-server-demo-session, vehicle-server:ext/opencode-server-summary-window, vehicle-server:ext/opencode-server-window-engine-zero]
prs: []
zone: green
review: pending
---

# Long run 20 — finish LR19-4/5 + summary window key + engine_zero properties

## Goal
Finish the synthetic demo session (generator, tests, README, PR), add the defs `window` key to
`/summary` signal entries, and extend the seeded window property tests to the `engine_zero` close.

Task list (from `external-ai/tasks/2026-11-06-deepseek-long-run-20.md`, workspace PR #179):
- LR20-0: this log on `ext/opencode-long-run-20-log`.
- LR20-1: commit the untracked LR19 demo generator, rebase onto `origin/main`, push.
- LR20-2/3: finish the generator, add `tests/test_demo_session.py`, README, one server PR.
- LR20-4: `window` key in `/summary` entries from `vehicle_derived`, tests, one server PR.
- LR20-5: seeded property tests reach `engine_zero`, one server PR.
- LR20-6: close this log and refresh the VS Code workspace.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-06-opencode-long-run-20.md`: opened before code (LR20-0).

## Result
(In progress.)

## Checks
- `python3 scripts/check_zones.py . --base origin/main`: (pending)

## Unsure about
(Pending.)

## For Claude
(Pending.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
