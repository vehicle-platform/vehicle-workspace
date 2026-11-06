---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-20
repos: [vehicle-workspace, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-20-log, vehicle-server:ext/opencode-server-demo-session, vehicle-server:ext/opencode-server-summary-window, vehicle-server:ext/opencode-server-window-engine-zero]
prs: [vehicle-server#59]
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
- `vehicle-server/scripts/make_demo_session.py`: rescued the untracked LR19 work as-is
  (`bb346e8`), rebased it onto the updated `main`, then finished it (`d708c2e`). The default date
  is fixed at 2026-01-01; `--date` and `--zip` are optional; all DIDs, scales, gear ratios,
  window durations and thresholds come from `vehicle_defs`.
- `vehicle-server/tests/test_demo_session.py`: imports the generated session and checks the
  windows, per-gear rows, stops, position-free data and run-to-run determinism.
- `vehicle-server/README.md`: "Synthetic demo session" paragraph (command, import, analyzer E,
  phone Server rides, synthetic/no GPS).

## Result
The demo session (20 min, `synthetic-demo-20260101`, session id `20260101-090000-5e55`) opens
every window and stores one qualifying instance per window: W1 one, W2 two (`engine_zero` and
`unknown`), W3 four (one qualifying, one short non-qualifying warm idle), W4 five, W5 two (the
first is the 1 s crank stall, the final 80 s instance qualifies at `session_end`). Close reasons
include `engine_zero` and `unknown`; per-gear has 3 valid gears; `ride_stop_count` is 3; no
derived or derived-summary error. Two folder generations and two zip generations are
byte-identical. PR: vehicle-server#59.

## Checks
- `uv run pytest -q`: 707 passed, 1 warning (Starlette httpx deprecation), 23.8 s.
- `uv run pytest -q tests/test_demo_session.py`: 1 passed, 4.27 s.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: 97 files already formatted.
- `uv run pytest -q tests/test_golden.py tests/test_golden_b.py`: included in the full suite; pass.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN (README,
  scripts/make_demo_session.py, tests/test_demo_session.py).

## Unsure about
- LR20-2 item 2 says an engine stop while a W3 warm idle is open should close an instance with
  `engine_zero`. In `health_windows.py` only an `engine_start` window closes with
  `engine_zero`; a W3 condition window closes with `condition`. I implemented the required
  close via a crank stall (W2) instead and did not touch the state machine (rule 1).
- A crank stall is also a valid `> 0 -> 0` transition, so W5 has a short non-qualifying 1 s
  instance at the stall before the final qualifying post-stop instance. This follows D-079.

## For Claude
- Please confirm the LR20-2 wording should read W2 (crank) rather than W3 for the
  `engine_zero` close; the current state machine cannot produce W3 + `engine_zero` without a
  rule change.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
