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
- LR16-1 (vehicle-analyzer, `ext/opencode-analyzer-per-gear`): added `PerGearSummary` and its
  strict parser to `src/services/sessionClient.ts`; a malformed `gears` list becomes that one
  signal's `error` row instead of failing the card. View E (`RideSummary.tsx`) renders a per-gear
  table (`gear n`, value, unit, flag) in gear order with the response range precision. Tests:
  valid/null/empty/malformed parse cases and a component test for order, unit, flag, precision and
  the malformed-entry fallback.
- LR16-2: pending.
- LR16-3 (vehicle-mobile, `ext/opencode-mobile-per-gear`): pending.
- LR16-4: pending.
- LR16-5: pending.

## Result
- Task progress: LR16-0 and LR16-1 done. LR16-2..LR16-5 pending.

## Checks
- LR16-0 `python3 scripts/check_zones.py . --base origin/main`: GREEN (log path only).
- LR16-1 `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: GREEN (four changed
  files). `npm test`: 42 files, 328 tests passed. `npm run build`: passed.

## Unsure about
- None yet.

## For Claude
- None yet.

## Claude review
(Filled by Claude's /external-review.)
