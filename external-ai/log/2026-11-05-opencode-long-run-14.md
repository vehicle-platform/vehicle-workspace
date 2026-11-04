---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-14-analyzer-signal-coverage
repos: [vehicle-workspace, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-long-run-14-log, vehicle-analyzer:ext/opencode-analyzer-coverage]
prs: []
zone: green
review: pending
---

# Signal coverage view in vehicle-analyzer

## Goal
Add a **Signal coverage** view (key I) to vehicle-analyzer: every value in the bundled
vehicle-defs in one table, the raw YAML facts about what it waits for, and — for a selected
recorded session — whether the server report has data for it. No hand-written signal list or
count, no `ready_phase0`/`ready_rt_core` computation on the phone/analyzer, read-only.

Task file: `external-ai/tasks/2026-11-05-deepseek-long-run-14.md`.

## Changes
- LR14-0 (vehicle-workspace, `ext/opencode-long-run-14-log`): created this log first, before code.
- LR14-1 (vehicle-analyzer, `ext/opencode-analyzer-coverage`): pending.
- LR14-2: pending.
- LR14-3: pending.
- LR14-4: pending.
- LR14-5: pending.
- LR14-6: pending.

## Result
- Task progress: LR14-0 done. LR14-1..LR14-6 pending.

## Checks
- LR14-0 `python3 scripts/check_zones.py . --base origin/main`: pending.

## Unsure about
- None yet.

## For Claude
- None yet.

## Claude review
(Filled by Claude's /external-review.)
