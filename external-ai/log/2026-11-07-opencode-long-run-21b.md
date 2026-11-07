---
date: 2026-11-07
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-21b
repos: [vehicle-workspace, vehicle-rt-core, vehicle-server]
branches: [vehicle-workspace:ext/opencode-long-run-21b-log, vehicle-rt-core:ext/opencode-rtcore-derived-d103]
prs: [vehicle-rt-core#66]
zone: yellow
review: pending
---

# Long run 21b — vehicle-rt-core D-103 class-A signals (rerun)

## Goal
Rerun `external-ai/tasks/2026-11-06-deepseek-long-run-21.md` after rt-core#65: implement the 21
new D-103 class-A derived signals in vehicle-rt-core and resync the golden vectors from
vehicle-defs v0.24.0.

Task list:
- LR21-0: this log on `ext/opencode-long-run-21b-log`.
- LR21-1: baseline build/tests/cppcheck/size and the class-A inventory.
- LR21-2: point and state signals with unit tests.
- LR21-3: window statistics and events with unit tests.
- LR21-4: resync the golden vectors and fix mismatches.
- LR21-5: full CI, size delta, zone check, one PR.
- LR21-6: close this log and refresh the VS Code workspace.

## Changes
### vehicle-workspace, branch `ext/opencode-long-run-21b-log`
- `external-ai/log/2026-11-07-opencode-long-run-21b.md`: this log (LR21-0; updated at LR21-6).
- `STATUS.md` was already modified before this run; I did not touch or commit it.

### vehicle-rt-core, branch `ext/opencode-rtcore-derived-d103`
- `b375e01 test(derived): resync the golden vectors from vehicle-defs v0.24.0`
  (14 files, +39,114/-64): all five class-A vector headers plus the new
  `derived_start_idle_refuel.h`, and the matching `_b` headers. Vectors only, so the generated
  headers land alone. Committed before the implementation commit, despite the task ordering
  (LR21-4 after LR21-2/3), because generated headers must not share a commit with hand-written
  code.
- `777cfcc feat(derived): implement the D-103 class-A signals`
  (11 files, +1,620/-40): core, types, README, CMake, existing tests, new
  `tests/host/test_derived_d103.c`.
- `9de3f24 docs(derived): record the D-103 memory cost`.
- `cffd22c docs(derived): describe the new class-B vector`.
- PR: https://github.com/vehicle-platform/vehicle-rt-core/pull/66 (`needs-claude-review`);
  body lists the computed set, the 15 NOT_COMPUTED summaries with their reason, the per-object
  size delta and the v0.24.0 vector provenance.

What was implemented:
- 21 new class-A signals: the 15 point/window/state signals and the six events
  `shift_event`, `launch_event`, `braking_event`, `refuel_event`, `cranking_dip`,
  `battery_rest_voltage`.
- New D-103 state in `derived_core_t`; RPM, battery, fuel and acceleration ring histories;
  engine flags, residual formulas, idle statistics/drift, charging plateau and fuel-filtered
  average; shift/launch/braking/refuel/cranking/rest event rules; ride reset of the new state.
- New flags `DERIVED_FLAG_NOT_MOVING=11`, `DERIVED_FLAG_NO_GEAR=12`,
  `DERIVED_FLAG_NOT_APPLICABLE=13`; vector flag enum extended through `NO_FAN_STEP`.
- All vehicle facts and thresholds come from `vehicle_cl250_constants.h` / the gen table; no
  hand-written CAN ID, DID, scale or signal name.
- `derived_core.h`: history caps (`DERIVED_WIN_RPM_HIST_CAP 548`, battery 15, fuel 8,
  acceleration 277), 60 s RPM / 30 s acceleration static asserts, D-103 constants.
- Reset handling clears `d103` and all nine rings in `reset_class_a`.

### vehicle-server
- Read-only use only: vectors regenerated with
  `uv run vehicle-server golden --out ../vehicle-rt-core/tests/host/vectors` at `main`
  `30ef5a8`; no vehicle-server change.

## LR21-1 baseline
- Precondition: `vehicle-rt-core/external/vehicle-defs` v0.24.0; rt-core `main` at `f6d96a1`;
  clean except the pre-existing workspace `STATUS.md` edit.
- Host tests before the change: **53/53 passed** in 23.36 s.
- MISRA/cppcheck workaround: Python 3.15 breaks the cppcheck addons
  (`Symbol not found: _XML_SetAllocTrackerActivationThreshold`); used
  `mkdir -p /tmp/lr21-cppcheck-bin && ln -sf /opt/homebrew/bin/python3.11 /tmp/lr21-cppcheck-bin/python3`
  and prepended `/tmp/lr21-cppcheck-bin` to PATH.
- MISRA canary passed (10.8, 15.5, 15.6, 17.7, 8.7; `CANARY_OK`); baseline MISRA RC 0 with
  `--suppressions-list=misra/suppressions.txt --suppress=missingIncludeSystem
  '--suppress=*:*external/*' -i src/hal/host -i src/app/host -I src
  -I external/vehicle-defs/gen/c/rt_core`.
- Baseline M7 release objects: `derived_core.c.obj` text 5,470; `derived_ride.c.obj` 1,172;
  `derived_gear.c.obj` 144; `derived_inputs.c.obj` 316 text / 1,493 BSS; host
  `sizeof(derived_core_t)` 12,592 B.
- Removed untracked MISRA canary artifacts `misra/canary.c.dump` and
  `misra/canary.c.ctu-info`.

### LR21-1 inventory (21 class-A signals not computed before this run)
| Signal | Kind | Inputs | Reference |
|---|---|---|---|
| clutch_state | point/state | RPM, measured ratio, throttle, gear ratios, tolerance, load min | d103_states.py:32 |
| clutch_slip_ratio | point | gear estimate, measured ratio, gear ratios | d103_states.py:60 |
| neutral_coasting_state | point/state | speed, RPM, gear estimate, throttle, closed throttle | d103_states.py:71 |
| engine_braking_phase | point/state | speed, throttle, RPM, fuel rate, moving/closed/idle max/fuel max | d103_states.py:92 |
| over_rev | point | RPM, over-rev RPM min | d103_states.py:108 |
| lugging | point | gear estimate, RPM, load, lugging RPM/load consts | d103_states.py:114 |
| cold_engine_abuse | point | coolant, RPM, load, operating/cold-abuse consts | d103_states.py:128 |
| idle_rpm_std | window | RPM, coolant, speed, idle band consts | d103_windows.py:81 |
| idle_rpm_drift | window | RPM, coolant, speed, idle band consts | d103_windows.py:105 |
| charging_plateau_voltage | window | battery voltage, RPM, plateau RPM min | d103_windows.py:139 |
| fuel_level_filtered | window | fuel level, vehicle acceleration, accel max | d103_windows.py:157 |
| heat_soak_delta | point | intake air temp, ambient air temp, speed, speed max | d103_windows.py:236 |
| idle_map_residual | point | intake MAP, throttle, RPM, expected/closed/idle consts | d103_windows.py:248 |
| volumetric_efficiency | point | MAF, MAP, intake air temp, RPM, displacement | d103_windows.py:303 |
| intake_flow_residual | point | MAF, MAP, intake air temp, RPM, displacement, VE reference | d103_windows.py:310 |
| shift_event | event | RPM, speed, step/window/speed-change consts | d103_events.py:28 |
| launch_event | event | speed, measured ratio, moving/end/tolerance/gear-1 consts | d103_events.py:67 |
| braking_event | event | vehicle acceleration, decel/duration consts | d103_events.py:108 |
| refuel_event | event | speed, fuel level, moving/step/tank consts | d103_events.py:170 |
| cranking_dip | event | RPM, battery voltage, idle RPM min | d103_events.py:226 |
| battery_rest_voltage | event | RPM, battery voltage, engine-start rule | d103_events.py:264 |

All are DID-only or computed-derived inputs (no sensor/GPS); the out-of-scope sensor signals
`wheel_slip`, `pitch_event` and `road_roughness` stay uncomputed.

## LR21-2 / LR21-3 result
- Golden replay matches the reference: 46,191 rows, 0 mismatches, 0 boundary skips;
  199,655 steps, mean 6,137 ns/step, max 145,000 ns/step, at most 46 evaluations/step,
  61 signals computed.
- `test_derived_core`: 23/23 tests, expected class-A count 49, gen fingerprint `0x4184CA10`,
  new scenario replay. Static RAM: `derived_core_t` 20,336 B (sample buffers 5,432,
  signal tables 5,640).
- `test_derived`: 5/5 tests; computed count `49u + 12u` = 61.
- New `test_derived_d103`: 7/7 tests with hand-computed cases:
  clutch/gear states, engine flags and residuals, battery/fuel windows, idle windows,
  the six events, ride reset, and stale/invalid flags. It covers reset for charging,
  cranking, battery rest, launch, braking, refuel, shift, idle std and fuel filtered.
- Fixed unit-test assumptions against the reference: clutch slipping uses a 2.4 ratio,
  charging needs RPM > 3000, VE/MAF uses 7.276743 g/s, the fuel filter needs two
  acceleration-fresh samples, stale dependants report INVALID_INPUT, and the cranking
  out-of-range case needs a battery sample.

## LR21-4 result
- Vectors are from defs v0.24.0: `derived_vectors.h` sha256 prefix `fb6d136f7812`,
  `derived_start_idle_refuel.h` prefix `37498b850369`; 49 class-A signals; new scenario
  3,025 inputs / 21,539 outputs.
- `test_derived_vectors`: 5/5; max flag bound `DERIVED_VECTOR_FLAG_NO_FAN_STEP`; new
  `test_start_idle_refuel_is_well_formed`.
- `test_derived_ride`: now explicitly asserts the 15 new D-103 class-B summaries are
  NOT_COMPUTED with `DERIVED_NC_NO_FORMULA` (`D103_CLASS_B_NOT_COMPUTED[]`), skips exactly
  those rows/record fields, and expects 27 golden / 12 computed / 15 not computed. This is
  an asserted out-of-scope boundary, not a silent skip.
- Vectors README updated: five class-A scenarios, 49 signals, v0.24.0, 3.5 MB, class-B
  27/12/15, and the new `derived_start_idle_refuel_b.h` is not replayed in this class-A run.
- `src/features/derived/README.md` updated for 49 signals, the new flags/windows/events,
  tests and memory.

## LR21-5 checks
- `ctest --preset host-tests`: **54/54 passed** (final run 42.51 s).
- `host-tsan`: **11/11 passed** (13.80 s).
- `host-coverage`: **54/54 passed** (36.67 s); gcovr **98.4% lines, 100.0% functions,
  92.9% branches** (floors 95/80).
- `target-m7-debug` and `target-m7-release`: both build.
- M7 release delta per object: `derived_core.c.obj` text **5,470 -> 10,636** (+5,166 B),
  data 0, BSS 0; `derived_ride.c.obj` text 1,172 (unchanged); `derived_gear.c.obj` text 144
  (unchanged); `derived_inputs.c.obj` text 316 / BSS 1,493 (unchanged); `derived.c.obj`
  BSS **12,388 -> 20,136** (+7,748 B); host `sizeof(derived_core_t)` **20,336 B**.
- cppcheck warning/performance/portability: RC 0.
- cppcheck style + MISRA C:2012: RC 0 after removing unused `RING_COUNT` and fixing
  MISRA 2.5/10.8/15.7 findings (nested `else` instead of `else if` chains, named duration
  variables).
- Zone check on all changed paths: **all YELLOW, no RED** (MCU firmware rule); PR marked
  `needs-claude-review`.
- No new dependencies, no firmware suppression, no disabled tests, no release or pin change.

## Unsure about
- `derived_core.c` is 2,215 lines, slightly above the task guide of ~2,000. I did not split it
  in this run: the D-103 code shares the core's private `ctx_t`, DID lookup, `store()` and
  history helpers, so a split needs an internal header and wider refactor than this run.
  The task's "or a new derived_*.c if it would grow past ~2000" is therefore not fully met;
  see For Claude.
- The 15 D-103 class-B summaries are deliberately left NOT_COMPUTED. They are class B
  (ride summaries), while this run implements class A; keeping the explicit asserted list
  makes the boundary reviewable, but a reviewer may still treat it as test weakening.
- `ride_idle_rpm_drift` reset is not explicitly unit-tested (the reset test covers idle std
  and the other stateful windows/events). Out-of-range cases are unreachable for enum/bool
  flags and for the 500 ms shift/launch event values.
- The vectors-only commit precedes the implementation commit, against the task's LR21-2/3
  before LR21-4 order, for generated-header isolation. The final branch is green.
- The generated `derived_start_idle_refuel_b.h` is not added to the class-B replay in this
  run; its 15 new summaries are NOT_COMPUTED. It is documented in the vectors README.
- Pre-existing untracked `vehicle-server/` in the workspace and modified `STATUS.md` were
  left untouched.

## For Claude
- Review PR #66; decide whether `derived_core.c` must be split into `derived_d103.c` now or
  whether the shared private state justifies keeping it at 2,215 lines.
- Confirm the class-B NOT_COMPUTED handling and the explicit skip list are acceptable for
  this class-A run, or request the D-103 class-B summaries as a follow-up.
- Review the stale-flag semantics: dependants of an invalid derived input report
  INVALID_INPUT, not STALE_INPUT; the new tests pin that.
- Do not merge; the user merges. No releases, tags or submodule pins changed.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
