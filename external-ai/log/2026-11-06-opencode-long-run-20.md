---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-20
repos: [vehicle-workspace, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-20-log, vehicle-server:ext/opencode-server-demo-session, vehicle-server:ext/opencode-server-summary-window, vehicle-server:ext/opencode-server-window-engine-zero]
prs: [vehicle-server#59, vehicle-server#60, vehicle-server#62]
zone: green
review: done 2026-11-06 (zones green, no BLOCKER; Claude server#63 supersedes #59, server#64 supersedes #62, #60 as is)
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
- `vehicle-server/src/vehicle_server/ride_summary.py`: every `/summary` signal entry with a
  defs `window` key now carries it in every status; non-window entries are unchanged
  (`7a0dc39`).
- `vehicle-server/tests/test_ride_summary.py`: API and function-level coverage for computed,
  `not_implemented` and non-window entries; every returned window is checked against
  `vehicle_derived.WINDOWS`.
- `vehicle-server/README.md`: one sentence on the optional `/summary` `window` key.
- `vehicle-server/tests/test_health_windows_properties.py`: forced trigger scenarios give W2
  an open instance followed by an exact 0 (plus W2 `session_end`/`unknown` and W5
  `max_duration`), and the test asserts first-zero `engine_zero` timing, no trigger-0 open
  except for `engine_stop`, and per-window close-reason coverage over all 200 seeds
  (`9f91936`).
- `vehicle-workspace/external-ai/log/2026-11-06-opencode-long-run-20.md`: this final LR20-6
  entry (commits, checks, PR links, xfails and doubts); `vehicle-platform.code-workspace`
  refreshed with `python3 scripts/vscode_workspace.py` (gitignored).

## Result
The demo session (20 min, `synthetic-demo-20260101`, session id `20260101-090000-5e55`) opens
every window and stores one qualifying instance per window: W1 one, W2 two (`engine_zero` and
`unknown`), W3 four (one qualifying, one short non-qualifying warm idle), W4 five, W5 two (the
first is the 1 s crank stall, the final 80 s instance qualifies at `session_end`). Close reasons
include `engine_zero` and `unknown`; per-gear has 3 valid gears; `ride_stop_count` is 3; no
derived or derived-summary error. Two folder generations and two zip generations are
byte-identical. PR: vehicle-server#59.

LR20-4 adds the defs window key to `/summary` entries: computed window scalars and
`not_implemented` window signals both carry it, non-window signals gain no key, and the key
comes from `vehicle_derived.SIGNALS`. PR: vehicle-server#60.

LR20-5 reaches `engine_zero` in W2 with a forced engine-speed trigger that drops to exactly 0
while open, then checks that close lands on that sample. The same test closes W2 at
`session_end`/`unknown` and W5 at `max_duration`, and asserts every spec-reachable close
reason per window over the 200 seeds. PR: vehicle-server#62. GitHub closed the first PR
(#61) when the head branch was renamed to the task's `ext/opencode-server-window-engine-zero`;
#62 is the live PR.

LR20-6 closes the run: the log records all tasks, commits, checks, PR links and doubts, and the
VS Code workspace was refreshed with `python3 scripts/vscode_workspace.py`.

## Checks
- `uv run pytest -q`: 707 passed, 1 warning (Starlette httpx deprecation), 23.8 s.
- `uv run pytest -q tests/test_demo_session.py`: 1 passed, 4.27 s.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: 97 files already formatted.
- `uv run pytest -q tests/test_golden.py tests/test_golden_b.py`: 21 passed, 5.01 s (also in
  the full suite on every branch).
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN (README,
  scripts/make_demo_session.py, tests/test_demo_session.py; README,
  src/vehicle_server/ride_summary.py, tests/test_ride_summary.py).
- LR20-4: `uv run pytest -q`: 708 passed; ruff check and format: pass; zone GREEN.
- LR20-5: `uv run pytest -q`: 711 passed; `tests/test_health_windows_properties.py`:
  25 passed in 0.94 s; golden tests: 21 passed in 5.01 s; ruff check and format: pass; zone
  GREEN.
- No xfail was needed: the per-window close-reason coverage assertion passes for W1-W5.

## PRs
- Demo session: https://github.com/vehicle-platform/vehicle-server/pull/59
- Summary `window` key: https://github.com/vehicle-platform/vehicle-server/pull/60
- Engine-zero property coverage: https://github.com/vehicle-platform/vehicle-server/pull/62

## Commits
- LR20-0: `bc52ad9` (log opened).
- LR20-1: `bb346e8` (rescued demo generator); LR20-2/3: `d708c2e` (demo session).
- LR20-4: `7a0dc39` (summary window key); LR20-5: `9f91936` (property coverage).
- Log updates: `937e9cc`, `ab2b4a3`, `e6f30ce`, and this final LR20-6 commit.

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
2026-11-06, Claude (Opus). Zones green on all three branches; CI green; architecture-guard no
BLOCKER; vss-schema-guardian: no CAN ID / VSS / scale literal, two small literals (below).

- **vehicle-server#60 (window key on `/summary`):** merge as is. Additive, key from defs, every
  status, tests against `vehicle_derived.SIGNALS`.
- **vehicle-server#59 → #63 (merge #63 instead; it contains #59):** MAJOR, the script used a
  `sys.path` insert + four `# noqa: E402` (AGENTS §3: no new noqa) to import `tests.make_fixtures`;
  moved to `tests/make_demo_session.py` (`uv run python -m tests.make_demo_session`), relative
  imports. MAJOR, signals.csv rows were a second hand-built copy of the 13 columns: now
  `make_fixtures.vsig_row_cells` (new `table_len` argument). Minor: `ble_schema_version` from
  `defs_ble.CURRENT_VERSION`, close reasons from `health_windows` constants, parquet files checked
  for position columns too, README stop count matched to the generator. 707 tests.
- **vehicle-server#62 → #64 (merge #64 instead):** the `engine_zero` coverage came only from
  seed-keyed hand-written series that **replaced** the random series of seeds 0-3 for W2/W5. Root
  cause: W2's `max_duration_ms` is 3 s while random trigger segments were >= 2 s with steps up to
  5 s. Now the engine-start trigger uses short segments half the time and the random seeds reach
  `engine_zero` on their own (own test); the directed cases run in addition to the 200 seeds. 26
  tests, ~7.6 s.
- *For Claude* (W3 vs W2): DeepSeek is right, only `engine_start` windows close with
  `engine_zero`; the task text was wrong and is corrected. Handling it via a W2 crank stall was the
  right call (rule 1 respected).
