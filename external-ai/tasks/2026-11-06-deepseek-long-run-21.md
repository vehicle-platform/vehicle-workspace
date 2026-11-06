# DeepSeek long run 21 — 2026-11-06 (rt-core C3 part 3: the D-103 class-A signals)

Written by Claude for opencode/DeepSeek. Run the tasks in order without asking between them.
Commit after every task (Conventional Commits, `AI-Agent: opencode/<model>` trailer) and push
after every commit. If a task is blocked, write why in the log's *For Claude* section and go on.
**Never merge a PR.**

**Precondition:** vehicle-rt-core `main` pins vehicle-defs **v0.24.0** (rt-core#65, Claude). Check
with `git -C vehicle-rt-core/external/vehicle-defs describe --tags` after `git pull` +
`git submodule update --init`. If it says v0.23.0, stop: write "rt-core#65 not merged" into the log
and end the run.

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| LR21-0 (first!) and LR21-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-21-log` | green |
| LR21-1 ... LR21-5 | vehicle-rt-core | `ext/opencode-rtcore-derived-d103` | **yellow** (`src/features/derived/*`, `tests/host/*`): the PR body starts with `needs-claude-review`. **Red, never touch:** `external/*`, `gen/*`, `misra/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `cubemx/*`, `*.ld`, `src/features/cornering/*`, `src/features/uds/*`, `src/features/heartbeat/*`, `src/features/vehicle_republish/*`, `src/services/*` (yes, all of `services/` for this run), `src/app/*` |
| (read only) | vehicle-server | none: only run `vehicle-server golden` from its `main` | — |

## 0. Before you start (read, do not skip)

### Why this run

vehicle-server's Python reference computes 21 more class-A derived signals since D-103
(server#52, defs v0.23.0/v0.24.0, provisional thresholds). Its golden vector selection already holds
49 class-A signals, but rt-core's `tests/host/vectors/` are still the v0.23.0 set of 28, so rt-core
cannot resync them until it implements the new ones (ISSUES E-30 (5)). This run implements them in
`src/features/derived/` and resyncs the vectors. The vectors are the oracle: a signal is done when
the replay in `tests/host/test_derived_core.c` matches the reference within the generated tolerance.

No decision is needed from the user. If something here contradicts a decision (D-070, D-087, D-088,
D-103) or `vehicle-rt-core/CLAUDE.md`, the decision text wins: write the conflict into *For Claude*
and skip that part.

### Visibility and git

- Work in the main clones (`vehicle-rt-core/`, the workspace root), not under `.claude/worktrees/`.
- After creating each branch, and at the end, run `python3 scripts/vscode_workspace.py` from the
  workspace root. Normal git config; do not set `user.name` / `user.email`.
- Before every push: `python3 scripts/check_zones.py vehicle-rt-core --base origin/main`. A red path
  → do not push; revert that path and write it into *For Claude*.

### Read (in this order, only what is listed)

1. `AGENTS.md` (workspace root): zones, trailer, log format, check table §4.
2. `vehicle-rt-core/CLAUDE.md` (read only): layering, safety rules, the CI list (layering greps,
   cppcheck + MISRA, coverage floors 95 % lines / 80 % branches).
3. `vehicle-rt-core/src/features/derived/README.md` and `derived_core.h`, then `derived_core.c`
   (how a signal is scheduled on the gen period grid, `kind_of()`, sample-and-hold ages, the stale
   rule, `stop_event` as the one existing event, how a result outside the gen range becomes
   OUT_OF_RANGE, the NOT_COMPUTED reasons).
4. `vehicle-rt-core/tests/host/vectors/README.md` and `tests/host/test_derived_core.c` (the replay,
   the boundary-skip rule and `EXPECTED_SKIPPED`).
5. The generated table: `external/vehicle-defs/gen/c/rt_core/vehicle_cl250_derived.h/.c` and
   `vehicle_cl250_constants.h` (read only).
6. For each signal you implement, its Python reference in `vehicle-server/src/vehicle_server/derived/`
   (`d103_common.py`, `d103_states.py`, `d103_windows.py`, `d103_events.py`, `formulas.py`, `engine.py` for the grid
   and stale semantics). **The reference and the defs description are the specification**; port the
   arithmetic, do not invent a variant.

### Hard rules for this run

1. **Never a threshold literal.** Every D-103 threshold comes from the generated
   `vehicle_cl250_constants.h` macro of its declared `const.*` input (values are provisional and
   will change). Signal indices, DID indices, periods, ranges and `stale_after_ms` come from gen/.
   Unit conversions (3.6, 60, 2π) are fine as named `static const` values.
2. **Static memory only.** No `malloc`, no VLA, no recursion. Every buffer has a size from a gen/
   macro or a named constant with a comment saying why it is enough. Float32 for results; `double`
   only for long accumulators like part 2a, with a comment.
3. **No change outside `src/features/derived/` and `tests/host/`** (plus the README of the feature).
   If the core needs something from `services/` or `app/`, stop that signal and write it into
   *For Claude*.
4. **No new MISRA suppression and no new cppcheck deviation** (`misra/*` is red). Restructure the
   code instead; if impossible, leave the signal NOT_COMPUTED and explain in *For Claude*.
5. **QM separation stays:** nothing new includes `features/derived/` (the CI layering grep).
6. **Do not edit generated vectors by hand.** They come only from
   `cd vehicle-server && uv run vehicle-server golden --out ../vehicle-rt-core/tests/host/vectors`
   on vehicle-server `main` (pins v0.24.0). Do not change vehicle-server.
7. **Never weaken a test.** No tolerance change, no new boundary-skip rule. A signal you cannot make
   match is left NOT_COMPUTED with a reason (rule in LR21-4), never "almost matching".

## LR21-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-06-opencode-long-run-21.md` on
`ext/opencode-long-run-21-log` (from workspace `main`), `review: pending`, header + task list.
Commit and push before any code. Update it after every later task.

## LR21-1 — rt-core: inventory and baseline

1. Build and test `main` as is: `cmake --preset host-tests && cmake --build --preset host-tests &&
   ctest --preset host-tests` (expect 53/53). Run the cppcheck commands of `.github/workflows/ci.yml`
   locally (read the workflow; the MISRA addon needs `python3.11` in `PATH`). Record the results.
2. Baseline size: `cmake --preset target-m7-release && cmake --build --preset target-m7-release`,
   then `arm-none-eabi-size` on the `derived_*.c.obj` objects (find them under
   `build/target-m7-release`). Record text / data / bss per object in the log.
3. From the gen table, list the class-A signals with `rt_core_ready` that rt-core does not compute
   yet (expect 21: clutch_state, clutch_slip_ratio, neutral_coasting_state, shift_event,
   launch_event, braking_event, volumetric_efficiency, intake_flow_residual, idle_map_residual,
   heat_soak_delta, charging_plateau_voltage, cranking_dip, battery_rest_voltage,
   cold_engine_abuse, over_rev, lugging, idle_rpm_std, idle_rpm_drift, engine_braking_phase,
   refuel_event, fuel_level_filtered; trust the gen table over this list). For each: formula kind
   (point / window / state / event), inputs (DID / derived / const), the reference function. Put
   the table into the log. Signals with a sensor input (`wheel_slip`, `pitch_event`,
   `road_roughness`) stay out of this run.
4. Create the branch. No code change in this task.

## LR21-2 — rt-core: point and state signals

Implement, in `derived_core.c` (or a new `derived_d103.c` + `.h` in the same feature if
`derived_core.c` would grow past ~2000 lines; the core stays pure: no HAL, RTOS, services, clock),
the signals of the inventory that are **point or state formulas over DIDs, computed signals and
constants** (e.g. volumetric_efficiency, intake_flow_residual, idle_map_residual, heat_soak_delta,
clutch_slip_ratio, clutch_state, neutral_coasting_state, over_rev, lugging, cold_engine_abuse,
engine_braking_phase, battery_rest_voltage, charging_plateau_voltage, fuel_level_filtered). For each:

- the same stale / range / flag behaviour as the existing part 1 signals (a stale input → invalid
  with the existing flag, never a held value; outside the gen range → OUT_OF_RANGE, never clamped);
- states use the gen enum values, never literals;
- a hand-computed unit test in `tests/host/test_derived_core.c` (or a new
  `tests/host/test_derived_d103.c` registered like the others in `tests/host/CMakeLists.txt`):
  one valid case, one stale input, one out-of-range case per signal.

Do **not** resync the vectors yet. Build, ctest, cppcheck. Commit.

## LR21-3 — rt-core: window statistics and events

Implement the rest: the windowed statistics (idle_rpm_std, idle_rpm_drift, cranking_dip and any
other signal whose reference keeps a time window) with fixed-size ring buffers sized from the gen
period and the window constant (compile-time `_Static_assert` that the buffer covers the largest
window at the fastest period), and the events (shift_event, launch_event, braking_event,
refuel_event) through the existing `KIND_EVENT` path that `stop_event` uses. A new ride (D-075
epoch, README "Fresh state") resets every new window and event state like it resets the part 1
ones. Unit tests as in LR21-2, plus one ride-reset test per stateful signal. Build, ctest, cppcheck.
Commit.

## LR21-4 — rt-core: resync the golden vectors

1. From the workspace root:
   `cd vehicle-server && git checkout main && git pull && git submodule update --init && uv sync &&
   uv run vehicle-server golden --out ../vehicle-rt-core/tests/host/vectors`.
   The banners must name v0.24.0. Commit the regenerated headers **alone** in one commit
   (`test(derived): resync the golden vectors from vehicle-defs v0.24.0`).
2. Run `ctest --preset host-tests`. For every mismatch: compare your C with the reference line by
   line (grid alignment, the first sample after a stale gap, float32 vs double, the half-open window
   edges, the event timestamp rule) and fix the C.
3. If a signal still does not match after that, make it NOT_COMPUTED with a reason string and add it
   to an explicit, asserted list in the replay test (like `EXPECTED_SKIPPED`: the test fails if the
   list and the actual set differ), plus a *For Claude* entry with the first mismatching scenario,
   time and both values. **No tolerance or skip-rule change** (rule 7).
4. Update the vectors README (signal count, defs version) and the feature README (computed set,
   which signals are NOT_COMPUTED and why). Commit.

## LR21-5 — rt-core: checks, size, PR

1. Full local CI: host-tests, `host-tsan`, `host-coverage` (floors 95 % / 80 % on `src/` must still
   hold; record the numbers), both cross builds, cppcheck + MISRA exactly as the workflow. All green.
2. Size: `arm-none-eabi-size` on the `derived_*.c.obj` objects again; record the text / data / bss
   delta per object against LR21-1 in the log and the PR body (D-088: measured costs set the
   budget; Claude decides whether it is accepted).
3. Zone check. Open **one** PR to `main`, body starting with `needs-claude-review`, listing: the
   computed signals, the NOT_COMPUTED ones with reasons, test counts, coverage, the size delta, and
   "the golden vectors are regenerated from vehicle-server main at v0.24.0, not edited". Do not merge.

## LR21-6 — Close the log

Every task, commit, check result (test counts, coverage, cppcheck), the size table, the zone
results, the PR link, every NOT_COMPUTED signal with its first mismatch, every doubt
(*Unsure about*) and every request (*For Claude*). Keep `review: pending`. Run
`python3 scripts/vscode_workspace.py` one last time. Push the branch; no PR needed.
