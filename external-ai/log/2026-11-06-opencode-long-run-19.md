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

## Result
In progress. Task list:

- [x] LR19-0 — log first
- [x] LR19-1 — server: property tests for the window state machine
- [ ] LR19-2 — mobile: read the block
- [ ] LR19-3 — mobile: health windows on the ride summary screen
- [ ] LR19-4 — server: a synthetic demo session
- [ ] LR19-5 — server: test, README, PR
- [ ] LR19-6 — close the log

## Checks
- `uv run pytest tests/test_health_windows_properties.py -q`: pass, 20 passed (5 windows x
  properties + 5 non-vacuous generator checks).
- `uv run pytest -q`: pass, 703 passed, 1 existing Starlette deprecation warning.
- `uv run ruff check .` and `uv run ruff format --check .`: pass.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN.

## For Claude
- vehicle-server#56 (LR19-1) is open; no property failed, so there is no xfail.

## Unsure about
The seeded series do not reach `CLOSE_ENGINE_ZERO`; that branch remains covered only by code
reading, not by these properties. The generator is deterministic and its coverage check only
requires at least one instance and one qualifying instance per window, not every close reason.

## For Claude
Red-zone requests (path + wanted change), signals or decisions that would be needed, suspected conflicts with PLATFORM-RULES or DECISIONS.md, refactors you would suggest.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
