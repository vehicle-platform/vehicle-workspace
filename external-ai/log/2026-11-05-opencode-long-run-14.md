---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-14-analyzer-signal-coverage
repos: [vehicle-workspace, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-long-run-14-log, vehicle-analyzer:ext/opencode-analyzer-coverage]
prs: [https://github.com/vehicle-platform/vehicle-analyzer/pull/44]
zone: green
review: done 2026-11-05 (finished by Claude after the run stopped at LR14-3: vehicle-analyzer#44 merged)
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
- LR14-1 (vehicle-analyzer, `ext/opencode-analyzer-coverage`): extended `src/defs/model.ts` with
  `SensorDef`, `DerivedSignalDef`, identification `description`, and strict parsing of the
  pinned `derived/cl250_derived.yaml` `sensors`/`signals` blocks. Added the pure
  `src/services/coverage.ts` model (`buildCoverage`, `waitingFor`, `applySession`, `summarize`,
  `coverageToCsv`) and `tests/coverage.test.ts` plus defs assertions. The report cell reads
  `valid_ratios` for polled DIDs (not `range_checks`), the `imu`/`gps`/`can_health`/`tester_stats`
  blocks for sensors, and `derived`/`derived_summary` for A/B signals.
- LR14-2 (vehicle-analyzer): added `CoveragePanel` (key I) with defs/session header, per-group chips,
  sortable/filterable/scrolling table, Load session through the existing client, and CSV export of
  the visible rows. Wired the tab, global key I, App render and help.
- LR14-3: pending.
- LR14-4: pending.
- LR14-5: pending.
- LR14-6: pending.

## Result
- Task progress: LR14-0, LR14-1, LR14-2 done. LR14-3..LR14-6 pending.

## Checks
- LR14-0 `python3 scripts/check_zones.py . --base origin/main`: pending.
- LR14-1 `npm test`: 41 files, 314 tests passed.
- LR14-1 `npm run build`: passed (tsc -b + vite build; existing >500 kB chunk warning only).
- LR14-1 `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: YELLOW
  `src/defs/model.ts` (allowed, PR needs Claude review); GREEN for the new coverage service and tests.
- LR14-2 `npm test`: 41 files, 314 tests passed (before the LR14-3 view tests).
- LR14-2 `npm run build`: passed.

## Unsure about
- The task says `range_checks` carries `valid_percent`; the checked-in server actually puts it in
  `valid_ratios` and `range_checks` only holds `checked_count`/`out_of_range_count`. I used the
  actual server keys and mark missing keys `not in report`. Please confirm this is the intended
  contract for the coverage cell.
- `ble.telemetry.leanAngle` is deprecated and has no matching report summary block, so the
  `lean_angle` sensor row shows `not in report` rather than guessing a key.

## For Claude
- None yet.

## Claude review
2026-11-05, Claude:
- **Run state:** stopped after LR14-2 with an uncommitted view test draft; Claude committed the draft as DeepSeek's (it only failed because the worktree submodule was empty) and finished LR14-3..5 on `claude/review-lr14` (vehicle-analyzer#44, merged).
- **Zones:** only `src/defs/model.ts` yellow (allowed; strict parsers for `sensors`/`signals`, no existing field changed, reviewed), the rest green, `package.json` untouched.
- **Fixed:** `sensorReportKey` in `src/services/coverage.ts` had hand-written BLE field-name lists mapping to `can_health`/`tester_stats` (invariant 2; those blocks do not map by field name): removed, only block-level presence for `ble.imuBlock.*` / `ble.gpsBlock.*`, telemetry sensors read "not in report"; Playwright `ui-tests/coverage.spec.ts` (key I, mocked report, only app + server requested), the view in `ui-tests/views.spec.ts`, ROADMAP A13, README. 320 unit + 20 Playwright tests, build green.
- **Unsure about answered:** `valid_ratios` (not `range_checks`) is the right report key for polled DIDs (checked against `report.py`); `lean_angle` stays "not in report".

