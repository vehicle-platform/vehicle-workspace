---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-17-d079-health-windows
repos: [vehicle-workspace, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-17-log, vehicle-server:ext/opencode-server-health-windows]
prs: [vehicle-server#53]
zone: green
review: done 2026-11-05 (merge server#53 then server#54; Claude fixed the stale-gap duration, the guessed trigger and the window-key literals)
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
- `vehicle-server/src/vehicle_server/derived/health_window_summaries.py`: 17 ready window
  summaries (W1 five values, W2/W3/W4/W5 counts and W3/W5 values); two cruise residuals keep
  specific `definition:` reasons.
- `vehicle-server/src/vehicle_server/derived/summary.py`: `SummaryEnv.window()` and a single
  window precompute in `evaluate`; computed window signals leave `NOT_IMPLEMENTED_REASONS`.
- `vehicle-server/src/vehicle_server/derived/golden_b.py`: explicit `SKIP_HEALTH_WINDOW`.
- `vehicle-server/tests/test_health_window_summaries.py`: all 17 values on a synthetic ride
  (including an exact exponential tau), `no_window`, `out_of_range`, cold-soak patch and the
  window-signal classification.
- `vehicle-server/tests/test_summary_inputs.py` / `test_golden_b.py`: window-input audit and
  never-selected assertion.
- `vehicle-server/tests/test_health_windows_ingest.py`: a synthetic session (10 DIDs, 0-91 s)
  through the real ingest; asserts W1/W3/W5 scalars in `report.json`, `/sessions/{id}/summary`
  and `/rides`, then reruns `vehicle-server derive <id>` through the CLI.
- `vehicle-server/README.md`: provisional D-079 rules, the 17 computed and the remaining
  window signals, the golden exclusion and the updated class-B count (57 of 75).

## Result
Done. Task list:

- [x] LR17-0 — log first
- [x] LR17-1 — pure state machine `derived/health_windows.py` + unit tests
- [x] LR17-2 — window signals in `derived/health_window_summaries.py`, golden skip, tests
- [x] LR17-3 — synthetic ingest plus report/API/CLI end-to-end test
- [x] LR17-4 — README "D-079 health windows" subsection
- [x] LR17-5 — full checks, zone check, open one server PR (not merged)
- [x] LR17-6 — close the log

Server PR: https://github.com/vehicle-platform/vehicle-server/pull/53 (open, CI pass, left
unmerged).

Commits:
- `vehicle-server`: `f65954c` state machine, `376a289` window summaries, `0d3db62` end-to-end
  test, `c14bd31` README.
- `vehicle-workspace`: `a5665aa` LR17-0, `43c51c7` LR17-1, `dcdf9ea` LR17-2, `9634c90` LR17-3,
  `b7248a7` LR17-4, `2aff7f8` LR17-5, this closing commit for LR17-6.

## Checks
- `uv run pytest tests/test_health_windows.py -q`: pass (11 tests).
- `uv run pytest tests/test_health_window_summaries.py -q`: pass (5 tests).
- `uv run pytest tests/test_health_windows_ingest.py -q`: pass (1 test).
- `uv run pytest tests/test_golden.py tests/test_golden_b.py -q`: pass (21 tests).
- `uv run pytest -q`: pass (681 tests, 1 third-party deprecation warning).
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: pass (94 files).
- `uv run vehicle-server golden --out <tmp> --manifest <tmp>/MANIFEST.sha256`: manifest is
  byte-identical to `tests/golden/MANIFEST.sha256` (defs v0.24.0); all 29 `window:` signals are
  skipped with `SKIP_HEALTH_WINDOW`.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: green (all changed files).
- `uv.lock` unchanged.
- PR CI (`gh pr checks 53`): pass (33 s, run 42032178412).

## Unsure about
- The task file was requested from `main`, but it is not on `origin/main`; it exists only on
  `claude/lr17-task` (`5fd4083`) and in `.claude/worktrees/lr17-task/`. I read it from the
  worktree and did not edit it.
- The full pre-start reading (section 0) was completed before code.
- The README said "19 of the 46 class-B signals", but the pinned defs now has 75 class-B
  signals and 57 implemented (19 base + D-103 + 17 D-079). I wrote the current 57/75; if the
  task meant only the pre-D-103 base, that line needs rewording.
- The end-to-end test goes through the real catalog encoding, so the integer DIDs quantize:
  STFT mean is 5.078125 (raw 133/136, factor 25/32) and tau is 298.88 s, not 300. The pure
  summary test asserts the exact 300 s; the e2e test allows 1 %.
- `summary._window_input` now treats a DID absent from a caller-supplied restricted
  `did_limits` as an empty input instead of raising; `_feeds_of` still records `ERROR` for such
  a summary. Normal `evaluate` calls pass the full limits, so this only affects the restricted
  test path.

## For Claude
- Task-file location conflict: `external-ai/tasks/2026-11-05-deepseek-long-run-17.md` is absent
  from `main`; the run uses the `claude/lr17-task` copy.
- The two W4 cruise residuals stay `not_implemented`:
  - `window_cruise_final_drive_residual`: its declared inputs have no `const.gear_ratio_<n>`,
    so the measured final drive cannot be separated from the gearbox ratio (compare
    `ride_final_drive_ratio`, which declares them).
  - `window_cruise_ve_residual`: defs has no expected-VE model at that gear and speed.
- Proposed `CLAUDE.md` line (red, not edited): in the D-070 item 2 paragraph, replace
  "`data_quality_mask`, `ride_tester_nrc78_count`, the coast-down pair and the D-079 windows
  stay `not_implemented` with a reason" with "`data_quality_mask`, `ride_tester_nrc78_count`,
  the coast-down pair and the two D-079 cruise residuals stay `not_implemented` with a reason;
  17 D-079 window signals are computed in `health_windows.py`/`health_window_summaries.py`
  and golden B excludes them until rt-core implements the windows".
- Optional hardening: make `summary._feeds_of` use `did_limits.get(key)` like `_window_input`
  so a restricted caller reports missing inputs instead of an `ERROR` entry. No production
  caller is affected today.

## Claude review
- Zones: all paths green (vehicle-server, this log). No unlogged `AI-Agent:` commits or `ext/` PRs;
  no earlier Claude review of this run.
- architecture-guard: no BLOCKER. Scope, purity of `health_windows.py`, `@_summary` registration,
  golden skip, no route/dependency/lock change all fine; formulas (n-1 std, time-midpoint drift,
  least-squares tau) correct. vss-schema-guardian: DID / const names follow the
  `d103_summaries.py` pattern and are declared inputs; window keys were hand-written; defs pin
  unchanged. Golden manifest reproduced byte for byte by Claude.
- vehicle-server#53: merge as is, then **#54** (Claude, `da2eca4` + `702772d`):
  - **Fix:** the state machine evaluated only at sample times, so a stale input was noticed at the
    next sample of another input and the gap counted toward `min_duration_ms` (a 1 s-sampled
    engine speed with a shorter stale limit still gave a qualifying 2 s key-on window; the
    out-of-range test only passed that way). The timeline now adds each sample's stale instant;
    a `max_duration_ms` close ends at open + max; `max_duration_ms` read as optional.
  - The `engine_start` / `engine_stop` trigger is the D-069 engine-speed DID, checked against
    defs at import, instead of a guess from conditions / signal inputs (a failed guess raised and
    aborted every class-B summary).
  - `SummaryEnv.window()` takes the key from the signal's defs `window` entry (no `"W1_KEY_ON"`
    literals); the cruise-residual reasons moved into `NOT_IMPLEMENTED_REASONS`, the obsolete
    `_WINDOW_REASON` block and the import-time mutation removed.
  - `CLAUDE.md` (red): the D-070 item 2 sentence now names the 17 computed window signals and the
    golden skip (DeepSeek's proposed line, reworded).
  - Local: pytest 683, ruff check/format clean, golden manifest identical.
- For Claude requests: task-file location → workspace#175 (merge it; the run used that copy).
  Cruise residuals → ISSUES E-30 item (4) rewritten as a defs question. The optional
  `_feeds_of` / `_window_input` restricted-`did_limits` hardening left as is (test-only path).
- Unsure-about answers: 57/75 class-B count is right; the e2e 1 % tau tolerance from DID
  quantisation is fine.
