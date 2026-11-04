# DeepSeek long run 15 — 2026-11-05 (vehicle-server: the D-103 derived signals)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

**Start only after vehicle-server#51 (defs pin v0.23.0) is merged** (`git -C vehicle-server log
origin/main --oneline | grep -i "v0.23.0"`); without it the constants below do not exist.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR15-0 (first!) and LR15-7 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-15-log` | green |
| LR15-1..LR15-6 | vehicle-server | `ext/opencode-server-d103` | green (yellow: `*gps*`, `*position*`, `*mdf4*`, `pyproject.toml`; red: `*ota*`, `external/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`: do not touch them) |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

vehicle-defs v0.23.0 (D-103) gave 33 derived signals the thresholds they were missing: 45
provisional constants in `vehicle/cl250_constants.yaml`, wired into each signal as `const.*`
inputs, with the rule written in the signal's `description` ("Rule (D-103 ...)"). vehicle-server's
`src/vehicle_server/derived/` is the Python reference of the derived signals (rt-core later ports
from it). This run implements them there, so every recorded session computes them and the
analyzer shows them. The values are provisional and will change: **the code must read every
threshold from its declared `const.*` input**, so a later defs release changes the results without
a code change.

No decision is needed from the user. If something here contradicts a decision (vehicle-defs
`docs/DECISIONS.md`: D-070, D-076, D-087, D-095, D-099, D-103) or vehicle-server `CLAUDE.md`, the
decision text wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-server/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area).
- `git -C vehicle-server checkout main && git -C vehicle-server pull && git -C vehicle-server
  submodule update --init`, then `git -C vehicle-server checkout -b ext/opencode-server-d103`.
  In the workspace: `git checkout main && git pull && git checkout -b ext/opencode-long-run-15-log`.
  Right after creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root (zones, branches, trailer, log format, the check table §4).
  Before each push run `python3 scripts/check_zones.py vehicle-server --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-server `CLAUDE.md` ("Derived signals") and `README.md` (derived section).
- The sources of truth, at the pinned submodule `vehicle-server/external/vehicle-defs` (v0.23.0):
  `derived/cl250_derived.yaml` (each signal: `inputs`, `period_ms`, `window_ms`, `event`,
  `stale_after_ms`, `range`, `resolution`, and the **"Rule (D-103 ...)" sentence in
  `description`**), `vehicle/cl250_constants.yaml` (the 45 constants with `source:
  "D-103 recommendation ..."`), `docs/DECISIONS.md` D-103 (items 1-5) and D-070, D-087.
  The generated Python you import: `vehicle_defs.vehicle_derived` and
  `vehicle_defs.vehicle_constants`.
- vehicle-server code: `src/vehicle_server/derived/engine.py` (grid, staleness, range → null,
  statuses), `formulas.py` (the `@_point` / `@_series` / `@_event` registries, `Env`/`at.const()`,
  `stop_event` as the event example, `gear_estimate` for gear ratios from constants),
  `summary.py` (class-B `SUMMARIES`, `NOT_IMPLEMENTED_REASONS`, `SummaryEnv`), `inputs.py` (feeds;
  GPS speed/heading only), `golden.py` (`select_signals`: which class-A signals go into the rt-core
  vectors), and their tests in `tests/` (find the derived tests with `ls tests | grep -i derived`).

### Hard rules for this run

1. **No threshold literal.** Every threshold, band, window or reference value comes from a
   declared `const.*` input through the existing constant accessor. Allowed literals: unit
   conversions (3.6, 60, 1000), 0, 1, 100 for percent, and the clamp bounds of a score. A test per
   signal family patches one constant (monkeypatch the value the accessor returns) and shows the
   output follow it.
2. **Implement the rule as written.** The "Rule (D-103 ...)" sentence is the specification. Where
   it is ambiguous, take the simplest literal reading, write it in the function's docstring and in
   the log's *Unsure about*. Never invent an extra condition, threshold or input; never add an
   input to defs (red).
3. **The engine's contract stays.** A stale input → null (never a held value), a result outside
   `range` → null + `out_of_range`, no clamping, events only at event times, class B one value per
   session (one session = one ride, D-087). Read only declared inputs (`SummaryEnv` raises on an
   undeclared one: that is intended).
4. **No position (D-076).** GPS speed, speed accuracy and fix type only, through the existing
   feeds; fix types by their defs enum name, a 2D fix does not count (D-099). Never latitude,
   longitude or height.
5. **No real data in git (D-033).** Synthetic test sessions only, built with the existing fixture
   helpers.
6. **No new dependency** (`pyproject.toml` is yellow). numpy is already there if the existing code
   uses it; check before using anything.

## LR15-0 — Log first

Before any code: copy `external-ai/log/TEMPLATE.md` to
`external-ai/log/2026-11-05-opencode-long-run-15.md` on `ext/opencode-long-run-15-log`,
`review: pending`, fill the header and the task list, commit and push. Update it after every later
task (commit + push each time).

## LR15-1 — Class A: states and flags

`clutch_state`, `clutch_slip_ratio`, `neutral_coasting_state`, `engine_braking_phase`,
`over_rev`, `lugging`, `cold_engine_abuse`. Enum outputs use the values in the description
(e.g. `clutch_state` 0 engaged / 1 disengaged / 2 slipping); flags are 0/1. Tests: each state and
each flag edge on a synthetic series, a stale input → null, the constant-patch test.

## LR15-2 — Class A: windows and residuals

`idle_rpm_std`, `idle_rpm_drift`, `charging_plateau_voltage`, `fuel_level_filtered`,
`road_roughness`, `heat_soak_delta`, `idle_map_residual`, `wheel_slip`,
`volumetric_efficiency`, `intake_flow_residual`, `data_quality_mask`. Windowed signals use their
`window_ms`. `road_roughness`: a band-pass between the two band constants over the IMU vertical
acceleration (pick a simple, documented filter available in the existing dependencies; say which
in the docstring and the log). `volumetric_efficiency` and `intake_flow_residual` have no
threshold (speed-density with the defs displacement; name the gas constant you use and its
source in the docstring). `data_quality_mask`: read the description; if the bit layout is not
fully defined in defs, leave it `not_implemented` with a reason and write it in *For Claude*.

## LR15-3 — Class A: events

`shift_event`, `launch_event`, `braking_event`, `pitch_event`, `refuel_event`, `cranking_dip`,
`battery_rest_voltage`. Follow `stop_event`: rows at the event time, the value as the
description says, a gap above the input's `stale_after_ms` ends a running detection, an event still
open at the end of the data yields nothing. Tests: one clean event each, a near-miss below each
threshold, a gap in the middle, two events in one session.

## LR15-4 — Class B

1. The D-103 summaries: `ride_warmup_time`, `ride_thermal_cycle_count`,
   `ride_fan_on_temperature`, `throttle_torque_lag`, `ride_final_drive_ratio` (per gear, like the
   other `per_gear` summaries), `speedometer_error`, `effective_tyre_radius`,
   `ride_aggressiveness_score`, `ride_cornering_aggressiveness`, and the three definition rules
   `ride_can_error_count`, `ride_unanswered_did_count`, `ride_tester_nrc78_count`.
2. The summaries that were waiting for a class-A input you implemented in LR15-1..3 (their reason
   in `NOT_IMPLEMENTED_REASONS` is "input not implemented: derived.<x>"): implement each whose
   input now exists; leave `coast_down_cda` and `coast_down_rolling_resistance` as
   `not_implemented` unless their description fully defines the method (it needs a coast-down
   speed band that D-103 did not give: write that in *For Claude*).
3. Remove each implemented name from `NOT_IMPLEMENTED_REASONS`; keep the D-079 window reasons
   (the window state machine is not part of this run).
4. Tests per summary: a synthetic ride with a known answer, a ride without the condition → null
   (never 0 unless the signal is a count), the constant-patch test.

## LR15-5 — Golden vectors

`golden.py` selects every class-A signal in `FORMULAS` that is `ready_rt_core` and has no
`sensor.*` input, so several new signals enter the rt-core vectors. Run
`uv run vehicle-server golden --out <a temp dir>` and commit the updated
`tests/golden/MANIFEST.sha256` if the drift test requires it. **Do not copy anything into
vehicle-rt-core** (Claude refreshes its vectors at the rt-core bump). List in the log which
signals entered the vectors.

## LR15-6 — Docs, checks, PR

1. `README.md` (derived section): the newly implemented signals, a pointer to D-103 and to the
   constants file, and that the thresholds are provisional.
2. `CLAUDE.md` is red: write in *For Claude* the line Claude should change in "Derived signals".
3. Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the zone check, and
   open **one** PR from `ext/opencode-server-d103` to `main`; do not merge it.

## LR15-7 — Close the log

Finish `external-ai/log/2026-11-05-opencode-long-run-15.md`: every task, commit, check result
(test counts), the zone result, the PR link, every doubt (*Unsure about*: each ambiguous rule and
the reading you chose, each filter/method choice) and every request (*For Claude*). Keep
`review: pending`. Push the branch; no PR needed.
