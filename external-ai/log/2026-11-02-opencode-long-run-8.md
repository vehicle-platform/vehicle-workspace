---
date: 2026-11-02
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-8-summary-gating-axis-precision
repos: [vehicle-server, vehicle-rt-core, vehicle-analyzer, vehicle-mobile, vehicle-defs, vehicle-workspace]
branches: [vehicle-server:ext/opencode-summary-input-gating, vehicle-rt-core:ext/opencode-golden-b-regen, vehicle-analyzer:ext/opencode-ride-axis-precision, vehicle-mobile:ext/opencode-ride-axis-precision, vehicle-defs:ext/opencode-ride-did-layout-review, vehicle-workspace:ext/opencode-long-run-8-log]
prs: []
zone: yellow
review: pending
---

# long-run-8: E-26 input gating, E-27 axis precision, C3 part 2b layout review

## Goal
Make every implemented class-B summary honour its declared inputs (E-26 (1), user decision:
yes), fix the ride-summary bin-edge precision in analyzer and mobile (E-27), and review the
proposed ride-summary DID layout against the current code (docs only).

## Changes
- `vehicle-server/tests/test_summary_inputs.py`: added the declared-input audit (LR8-1).
- `vehicle-server/src/vehicle_server/derived/summary.py`, `gps_fix.py`, `gps_track.py`,
  `tests/test_derived_summary.py`, `tests/test_summary_inputs.py`,
  `tests/test_track_crosscheck.py`, `README.md`: gated `ride_distance_gps` on the shared
  `/track` fix rule, removed the known-offender xfail, and documented it (LR8-2/LR8-3).
- `vehicle-rt-core/tests/host/vectors/`: regenerated the 11 derived golden headers from defs
  `v0.19.1` (LR8-3).
- `vehicle-analyzer/src/components/RideSummary.tsx`,
  `src/services/rideSummaryLayout.ts`, `tests/rideSummaryLayout.test.ts`: bin-edge precision
  from the axis range (LR8-4).
- `vehicle-mobile/lib/ui/rides/ride_format.dart`,
  `lib/ui/rides/ride_summary_screen.dart`, `test/ride_format_test.dart`: the same axis-range
  rule and test cases (LR8-5).
- `vehicle-defs/docs/ideas/ride-summary-did-layout.md`: appended the compatibility-review
  section; proposal text above it is unchanged (LR8-6).
- `vehicle-workspace/ISSUES.md`: E-26 (1) and E-27 status cells updated.

## Result

### LR8-1 — declared-input audit (vehicle-server)
- Branch `ext/opencode-summary-input-gating`; commit `aa0d57d`
  `test(server): flag class-B summaries that ignore a declared input (E-26)`.
- Added `tests/test_summary_inputs.py` (95 lines), using an instrumented `SummaryEnv` over a
  synthetic session that provides every declared input.
- Full offender list: exactly **`ride_distance_gps`**. It declares `sensor.gps_fix_type` but
  read only `sensor.gps_ground_speed`; no other implemented class-B summary was an offender.
  It was marked `xfail(strict=True)` with the E-26 reference so LR8-2 had to flip it.
- No red-zone edit; `tests/test_summary_inputs.py` is GREEN.

### LR8-2 — gate every offender (vehicle-server)
- Branch `ext/opencode-summary-input-gating`; commit `ca94b9a`
  `fix(server): gate class-B ride summaries on every declared input (E-26)`.
- `ride_distance_gps` now integrates `sensor.gps_ground_speed` only while the latest fix-type
  sample is usable and fresh by the same rule as `/track`, shared through
  `src/vehicle_server/gps_fix.py` (`USABLE_FIX_NAMES`, `_usable_fix_values()`); `gps_track.py`
  imports it and its existing tests stayed green. A no-fix gap contributes zero distance; a
  ride with no usable fix returns the existing missing-inputs outcome, not `0.0`.
- Added the four requested cases: 10 s mid-ride fix loss, stale fix-type stream, no usable fix
  and full fix; removed the LR8-1 xfail. Cross-check values updated to distance `0.0067083`,
  track `0.00559665`, difference `-0.00111165` (the held-speed freshness tail vs `/track`
  trapezoids is explained in the test comments).
- `ride_odometer_mismatch` remains `not_ready` pending the 0xA6 odometer; its new test is an
  explicit stand-in dependency contract (see **Unsure about** and **For Claude**).
- Checks: `uv run pytest` -> `455 passed`; `uv run ruff check .` -> pass;
  `uv run ruff format --check .` -> pass. Zone check: **YELLOW** for `gps_fix.py` and
  `gps_track.py` (`*gps*` position paths, D-076), GREEN for the other changed files.

### LR8-3 — regenerate class-B golden vectors (rt-core) and docs (server)
- Branch `ext/opencode-golden-b-regen`; commit `acddc09`
  `chore(rt-core): regenerate derived golden vectors from defs v0.19.1`.
- Regenerated all 11 headers in `tests/host/vectors/`. Every diff is only the first-line defs
  version banner `v0.19.0` -> `v0.19.1`; every `content-sha256` remained identical and the
  server `tests/golden/MANIFEST.sha256` is unchanged. The payloads are byte-identical; the
  files are not literally byte-identical because of the banner. This matches the expected
  "no value change": `golden_b.py` selects only signals without a GPS input and rt-core does
  not compute `ride_distance_gps`.
- Server docs commit `ae7e6d6`
  `docs(server): class-B summaries honour declared inputs; GNSS fix rule shared with /track`
  updates `README.md` only.
- Checks: golden generation completed; `uv run pytest tests/test_golden_b.py
  tests/test_golden.py tests/test_summary_inputs.py -q` -> `39 passed`; rt-core
  `cmake --preset host-tests`, `cmake --build --preset host-tests`, `ctest --preset
  host-tests` -> `45 passed`. Zone: rt-core headers **YELLOW** (generated firmware inputs);
  the server README commit is GREEN, but the server branch's worst zone remains YELLOW from
  LR8-2.

### LR8-4 — analyzer bin-edge precision (vehicle-analyzer)
- Branch `ext/opencode-ride-axis-precision`; commit `ee05147`
  `fix(analyzer): format ride-summary bin edges with the axis precision (E-27)`.
- Added `precisionForAxis` in `rideSummaryLayout.ts`; `RideSummary.tsx` edge and heat-grid
  labels now use the precision of the axis input range (`first edge min .. last edge max`),
  not the signal value range. Values and cell classifications are unchanged.
- Tests cover `0..12000 -> 0`, a sub-unit range -> 4, a single bin -> 3, a negative range -> 1
  and an empty range -> 3.
- Checks: `npm ci`, `npm test`, `npm run build` -> pass. Zone: **GREEN**.

### LR8-5 — mobile bin-edge precision (vehicle-mobile)
- Branch `ext/opencode-ride-axis-precision`; commit `68c40f6`
  `fix(mobile): format ride-summary bin edges with the axis precision (E-27)`.
- Added `rideAxisRange` in `ride_format.dart`; `ride_summary_screen.dart` `_edgeText` call
  sites now pass the axis ranges, so bin edges use the same rule as the analyzer. Added the
  equivalent unit tests to `test/ride_format_test.dart`.
- Checks: `flutter analyze` -> pass; `flutter test` -> pass. `pubspec.lock` was reverted after
  the Flutter run; `pubspec.yaml` is unchanged. Zone: **GREEN**.

### LR8-6 — ride-summary DID layout compatibility review (vehicle-defs)
- Branch `ext/opencode-ride-did-layout-review`; commit `17b2c60`
  `docs(ideas): compatibility review of the ride-summary DID layout (C3 part 2b)`.
- Appended `## Compatibility review (DeepSeek, 2026-11-02)` to
  `docs/ideas/ride-summary-did-layout.md`; the proposal above it is unchanged. The section has
  one table row per check with evidence and result, plus the verdict.
- Recomputed sizes (4 B header included): `RIDE_USAGE 18`, `RIDE_FUELING 12`,
  `RIDE_OPERATING_POINTS` not served, `RIDE_THERMAL 14`, `RIDE_ELECTRICAL 8`,
  `RIDE_ENGINE_STRESS 22`, `RIDE_DRIVETRAIN 12`, `RIDE_CALIBRATION 14`,
  `RIDE_RIDER_STYLE 8`, `RIDE_ECU_HEALTH 21`, windows `16/14/20/14/12`. Largest record 22 B;
  all proposal sizes match; no raw maximum exceeds 4 B; no raw maximum is all-ones or an exact
  `.5` tie. 70 scalar fields: 12 computed by rt-core, 58 NOT_AVAILABLE.
- The five v1 leftovers are exactly `operating_point_time`, `fuel_trim_map`,
  `ride_coolant_time_at_temp`, `ride_oil_time_at_temp` and `ride_final_drive_ratio`;
  `RIDE_OPERATING_POINTS` is not served in v1 (proposal point 5). No other record becomes
  empty.
- Results: checks 1, 2, 5, 6, 7, 9 **OK**; check 3 **OPEN** (no generic per-field
  NOT_AVAILABLE codegen/writer feature); check 4 **MISMATCH** (rt-core does not keep the
  last-closed epoch counter, and the uint16 counter wraps/resets); check 8 **OPEN** (server has
  no raw/NA encoder and the Python/C rounding tie rule is undecided). Verdict: not yet
  "no blocker"; Claude must resolve 3, 4 and 8.
- Checks: docs-only, no codegen/generated files changed; `git diff --check` -> pass; zone
  check -> **GREEN** (`docs/ideas/*`). The review script was run from `vehicle-defs` with
  `uv run --with pyyaml python <script>`.

```python
import math
import sys

import yaml

ROOT = "/Users/alihanesentas/Desktop/vehicle-platform/vehicle-defs"
with open(f"{ROOT}/derived/cl250_derived.yaml") as f:
    doc = yaml.safe_load(f)
with open(f"{ROOT}/uds/dids.yaml") as f:
    uds = yaml.safe_load(f)

records = doc["ride_summary_records"]
signals = doc["signals"]

explicit_dids = {d["did"]: d["name"] for d in uds["nodes"]["RT_CORE"]["dids"]}
ride_dids = {r["did"]: k for k, r in records.items()}
print("DID collisions:", set(explicit_dids) & set(ride_dids))
print("Ride DIDs outside 0xFD40-0xFD5F:", [k for k, r in records.items() if not 0xFD40 <= r["did"] <= 0xFD5F])

multi = []
by_record = {}
for name, s in signals.items():
    if s["class"] != "B" or "record" not in s:
        continue
    rec = s["record"]
    by_record.setdefault(rec, []).append(name)
    if s.get("bins") or s.get("per_gear"):
        multi.append((name, rec, "bins" if s.get("bins") else "per_gear"))

print("\nMulti-element (v1 leftover):")
for m in multi:
    print(" ", m)
print("Leftovers not listed by proposal:",
      sorted({n for n, _, _ in multi} - {"operating_point_time", "fuel_trim_map",
             "ride_coolant_time_at_temp", "ride_oil_time_at_temp", "ride_final_drive_ratio"}))

computed = {
    "ride_distance", "ride_time", "ride_idle_time", "ride_stop_count",
    "ride_fuel_used", "ride_fuel_consumption", "ride_ltft_mean", "ride_stft_std",
    "ride_coolant_rate_max", "ride_start_coolant_temp", "ride_start_intake_temp",
    "ride_end_coolant_temp",
}

print("\nrecord scalar_count bytes computed na widths")
total_rows = []
for rname, r in records.items():
    fields = [n for n in by_record.get(rname, [])
              if not signals[n].get("bins") and not signals[n].get("per_gear")]
    widths = []
    ncomp = 0
    for n in fields:
        s = signals[n]
        raw_max = round((s["range"][1] - s["range"][0]) / s["resolution"])
        if raw_max < 0:
            raise SystemExit(f"negative raw max {n}")
        width = 1 if raw_max < 0xFF else 2 if raw_max < 0xFFFF else 4 if raw_max < 0xFFFFFFFF else None
        if width is None:
            print("DOES NOT FIT 4 B:", n, raw_max)
        widths.append(width)
        if n in computed:
            ncomp += 1
    size = 4 + sum(widths) if fields else None
    total_rows.append((rname, r["did"], len(fields), size, ncomp, len(fields) - ncomp, widths))
    print(f"{rname:26} 0x{r['did']:04X} {len(fields):2} {str(size):>4} {ncomp:2} {len(fields)-ncomp:2} {widths}")

print("\nempty scalar records:",
      [r for r in records if not [n for n in by_record.get(r, [])
       if not signals[n].get("bins") and not signals[n].get("per_gear")]])
print("total computed scalar fields:", sum(x[4] for x in total_rows))
print("max record bytes:", max(x[3] for x in total_rows if x[3] is not None))

print("\nall-ones collisions (valid raw max == reserved value):")
for rname, _, _, _, _, _, widths in total_rows:
    fields = [n for n in by_record.get(rname, [])
              if not signals[n].get("bins") and not signals[n].get("per_gear")]
    for n, w in zip(fields, widths):
        s = signals[n]
        raw_max = round((s["range"][1] - s["range"][0]) / s["resolution"])
        if w and raw_max == (1 << (8 * w)) - 1:
            print(" ", rname, n, raw_max, w)
```

Additional one-off checks: `rg -n "0xFD" uds/obd_catalog.yaml uds/vehicle_cl250.yaml
uds/vehicle_cl250_uds.yaml` -> no matches; a direct half-tie check
`abs((max-min)/resolution - round(...)) == 0.5` -> no matches.

### LR8-7 — log and wrap-up (vehicle-workspace)
- Branch `ext/opencode-long-run-8-log`; this file plus the `ISSUES.md` status edits are the
  only changes. Zone check for `external-ai/log/*`: **GREEN**. No PR opened; branches pushed.

## Checks
- `vehicle-server`: `uv run pytest` -> `455 passed`; `uv run ruff check .` -> pass;
  `uv run ruff format --check .` -> pass; targeted golden/audit rerun -> `39 passed`.
- `vehicle-rt-core`: golden generation -> 11 banner-only header updates, content hashes and
  `MANIFEST.sha256` unchanged; `ctest --preset host-tests` -> `45 passed`.
- `vehicle-analyzer`: `npm ci`, `npm test`, `npm run build` -> pass.
- `vehicle-mobile`: `flutter analyze`, `flutter test` -> pass; `pubspec.lock` reverted.
- `vehicle-defs`: docs-only; `git diff --check` -> pass; no codegen tests needed.
- Zone checks (`python3 scripts/check_zones.py <repo> --base origin/main`):
  - `vehicle-server`: **YELLOW** (`src/vehicle_server/gps_fix.py`,
    `src/vehicle_server/gps_track.py`; other changed files GREEN).
  - `vehicle-rt-core`: **YELLOW** (11 `tests/host/vectors/*.h`).
  - `vehicle-analyzer`: **GREEN**.
  - `vehicle-mobile`: **GREEN**.
  - `vehicle-defs`: **GREEN**.
  - workspace log path: **GREEN**.
- Worst zone: **YELLOW**; no red-zone edit attempted.

## Unsure about
- The task table lists vehicle-server as green, but the actual path rule makes `gps_fix.py` and
  `gps_track.py` YELLOW because they are `*gps*` position paths (D-076). They contain no
  position storage or emission (speed/heading/fix type only), but a PR would need
  `needs-claude-review`.
- `ride_odometer_mismatch` is still `not_ready` pending the 0xA6 odometer. The added test is a
  stand-in that checks it follows the gated GNSS distance; if its future definition consumes
  the GNSS distance differently, the test must be revisited.
- LR8-6 check 4 assumes the header counter should identify a ride across a new ride open. The
  proposal's wording "from `services/tester_epoch`" does not say how the last-closed value is
  retained; current rt-core cannot supply it.
- LR8-6 check 3 names a possible codegen feature (`na: true` -> `*_NA` plus a writer rule); the
  exact name/shape is Claude's choice. The existing `*_MAX` must remain saturation, not NA.
- LR8-6 check 8 has no runnable raw encoder to compare; the Python/C rule is an analysis, not a
  passing test.

## For Claude
- **LR8-6 OPEN/MISMATCH rows** (all in the defs review section, commit `17b2c60`):
  - **Check 3 (OPEN):** add a generic per-field NOT_AVAILABLE codegen/writer feature; the
    current encoder emits `*_MAX` (saturation) and has no NA value. Suggested shape:
    `na: true` -> generated `*_NA`, with the writer using it for missing/out-of-range values.
  - **Check 4 (MISMATCH):** rt-core stores the epoch counter only for the open ride;
    `derived_ride_close()` does not retain it, so header bytes 1-2 cannot be built for the
    last closed ride after a new one opens. Also the uint16 counter wraps/resets on
    `uds_client_open()`, and `0xFFFF` must be exempt from the all-ones = NOT_AVAILABLE rule if
    the header counter uses it.
  - **Check 8 (OPEN):** vehicle-server has no raw/NA encoder for these records and only 16 of
    the 70 scalar fields have reference values; decide the raw quantization and rounding rule
    (`lrintf`/`nearbyint` ties-to-even matches Python `round`; `roundf`/`lroundf` does not).
- **Zone:** the server branch is YELLOW because of `gps_fix.py` / `gps_track.py`; if a PR is
  opened, mark it `needs-claude-review`. No red-zone change is requested.
- **Test dependency:** the `ride_odometer_mismatch` follow-the-GNSS test is a stand-in until the
  0xA6 odometer exists; confirm that is the intended contract when that signal becomes ready.
- No offender was left `xfail`: LR8-1 found only `ride_distance_gps`, and LR8-2 fixed it.
- No signal, UDS, BLE, CAN, codegen, generated or firmware code was changed; LR8-6 is docs-only.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
