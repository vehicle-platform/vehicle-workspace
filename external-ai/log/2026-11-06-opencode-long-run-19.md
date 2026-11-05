---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-19-window-invariants-mobile-demo
repos: [vehicle-workspace, vehicle-server, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-19-log, vehicle-server:ext/opencode-server-window-invariants, vehicle-mobile:ext/opencode-mobile-health-windows, vehicle-server:ext/opencode-server-demo-session]
prs: []
zone: green
review: pending
---

# DeepSeek long run 19 — window invariants, phone card, synthetic demo

## Goal
Test the provisional D-079 state machine against general properties, show the stored window
instances on the phone, and add a synthetic demo session that exercises every window; no window
rule, formula, dependency or real data changes.

## Changes
- `vehicle-server/tests/test_health_windows_properties.py`: added seeded properties over 200
  synthetic series per window (5 windows): closed instances are ordered and non-overlapping,
  reasons are known, `first_qualifying` is the first qualifying instance, the count matches,
  and every qualifying duration is within `min_duration_ms` / `max_duration_ms`. The suite also
  checks determinism, a +1 s time shift (every instance moves by the same offset), and that no
  input or all-stale inputs never qualify. The series are piecewise-constant runs around the
  window's own condition/stable thresholds with random gaps around each input's stale limit;
  `health_windows.py` was not changed.
- `vehicle-mobile/lib/models/health_windows.dart`: pure defensive parser for
  `report.derived_summary.health_windows`; keeps response order and rejects a missing/invalid
  field, `end_ms < start_ms`, a wrong `duration_ms` and more than one `first_qualifying`.
- `vehicle-mobile/lib/services/ride_client.dart`: `getReport()` GETs
  `/sessions/{id}/report` with the bearer token through the existing `RideResult` handling.
- `vehicle-mobile/lib/models/ride_summary.dart`: keeps an optional response `window` field as
  `signalWindowKeys` (no name guessing); the current server sends no such field.
- `vehicle-mobile/test/health_windows_model_test.dart` and `test/ride_client_test.dart`: parser
  cases (valid, missing, every malformed field, order) and report GET/401/404/timeout cases.
- `vehicle-mobile/lib/ui/rides/health_windows_section.dart`: provisional rule chip, one window card
  in response order with counts, a `CustomPaint` timeline on a 0..last-end axis (qualifying filled,
  first qualifying marked), a compact instance table, and no invented signal rows.
- `vehicle-mobile/lib/ui/rides/ride_summary_screen.dart`: loads `/sessions/{id}/report` after the
  summary (one request), keeps the summary on a report failure, and renders the section below it.
- `vehicle-mobile/test/ride_summary_screen_test.dart`: valid section (request order, segment count,
  marker, table, matching signal row), missing block, malformed block, failed report with a working
  summary; the retry test now expects the extra report request.

## Result
In progress. Task list:

- [x] LR19-0 — log first
- [x] LR19-1 — server: property tests for the window state machine
- [x] LR19-2 — mobile: read the block
- [x] LR19-3 — mobile: health windows on the ride summary screen
- [ ] LR19-4 — server: a synthetic demo session
- [ ] LR19-5 — server: test, README, PR
- [ ] LR19-6 — close the log

## Checks
- `uv run pytest tests/test_health_windows_properties.py -q`: pass, 20 passed (5 windows x
  properties + 5 non-vacuous generator checks).
- `uv run pytest -q`: pass, 703 passed, 1 existing Starlette deprecation warning.
- `uv run ruff check .` and `uv run ruff format --check .`: pass.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN.
- `~/development/flutter/bin/flutter analyze`: pass, no issues.
- `~/development/flutter/bin/flutter test test/ride_client_test.dart test/health_windows_model_test.dart`:
  pass, 30 tests.
- `~/development/flutter/bin/flutter test test/ride_summary_screen_test.dart`: pass, 8 tests.
- `~/development/flutter/bin/flutter test`: pass, 340 tests.
- `~/development/flutter/bin/flutter analyze`: pass, no issues.
- `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: GREEN.

## For Claude
- PRs: vehicle-server#56 (LR19-1, no property failed, no xfail), vehicle-mobile#31 (LR19-2/3).
- The phone cannot map `window_*` signals to a window yet: the current `/summary` entries carry no
  `window` field and the mobile defs pin is old (D-089 item 3). The screen shows no signal rows and
  only uses an optional `window` field if a future server sends it; a newer defs/server field is
  needed before signal rows can appear.

## Unsure about
The seeded series do not reach `CLOSE_ENGINE_ZERO`; that branch remains covered only by code
reading, not by these properties. The generator is deterministic and its coverage check only
requires at least one instance and one qualifying instance per window, not every close reason.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
