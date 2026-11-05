---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-16-per-gear-summaries
repos: [vehicle-workspace, vehicle-analyzer, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-16-log, vehicle-analyzer:ext/opencode-analyzer-per-gear, vehicle-mobile:ext/opencode-mobile-per-gear]
prs: []
zone: green
review: pending
---

# Per-gear ride summaries in the analyzer and the phone

## Goal
Render the server's `per_gear` class-A ride summary (`ride_final_drive_ratio`, D-103) in
vehicle-analyzer (view E card and Compare A) and vehicle-mobile, using the server's gears,
values and flags verbatim. Read-only: no computation, no new route, no new dependency.

Task file: `external-ai/tasks/2026-11-05-deepseek-long-run-16.md`.

## Changes
- LR16-0 (vehicle-workspace, `ext/opencode-long-run-16-log`): created this log first, before code.
- LR16-1 (vehicle-analyzer, `ext/opencode-analyzer-per-gear`): pending.
- LR16-2: pending.
- LR16-3 (vehicle-mobile, `ext/opencode-mobile-per-gear`): pending.
- LR16-4: pending.
- LR16-5: pending.

## Result
- Task progress: LR16-0 done. LR16-1..LR16-5 pending.

## Checks
- LR16-0 `python3 scripts/check_zones.py . --base origin/main`: pending.

## Unsure about
- None yet.

## For Claude
- None yet.

## Claude review
(Filled by Claude's /external-review.)
