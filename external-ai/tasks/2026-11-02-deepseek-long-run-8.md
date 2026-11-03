# DeepSeek long run 8 — 2026-11-02 (E-26 summary input gating, E-27 axis precision, C3 part 2b layout review)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

Repos and zones in this run:

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR8-1..LR8-3 | vehicle-server | `ext/opencode-summary-input-gating` | green |
| LR8-3 | vehicle-rt-core `tests/host/vectors/` only | `ext/opencode-golden-b-regen` (only if a header changes) | yellow |
| LR8-4 | vehicle-analyzer | `ext/opencode-ride-axis-precision` | green |
| LR8-5 | vehicle-mobile | `ext/opencode-ride-axis-precision` | green (`pubspec.yaml` must stay unchanged) |
| LR8-6 | vehicle-defs `docs/ideas/ride-summary-did-layout.md` only | `ext/opencode-ride-did-layout-review` | green |
| LR8-7 | vehicle-workspace `external-ai/log/` | (your log) | green |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### User decisions for this run (2026-11-02)

- **E-26 (1): yes, recorded as D-095** (vehicle-defs#115, merged; `git -C vehicle-defs pull` first). A class-B ride summary must honour **every input it declares** in
  `derived/cl250_derived.yaml` (`inputs:`). An input that is declared but never read is a bug in
  the reference, not a free choice.
- Everything else in ISSUES E-20/E-23/E-24/E-25 and every Q-xxx is **out of scope** for this run.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py <repo> --base origin/main` from the workspace root.
  **Red = stop**, write the request into the log.
- `ISSUES.md` rows **E-26** and **E-27** (workspace root).
- vehicle-server: `CLAUDE.md`, README sections "Golden vectors for rt-core (D-070 item 2)" and
  "Class-B (per-ride) golden vectors (C3 part 2a)". Code: `src/vehicle_server/derived/summary.py`
  (all `@_summary` functions, `SummaryEnv`, `_integral`), `derived/inputs.py`
  (`_sensor_series`: GPS speed/heading are filtered by `gnss_fix_ok` only),
  `src/vehicle_server/gps_track.py` (`USABLE_FIX_NAMES`, `_usable_fix_values()`: fix types by
  **defs enum name**, plus a freshness rule for the latest fix-type sample),
  `derived/golden_b.py` and `tests/golden/MANIFEST.sha256`. Tests: `tests/test_summary*.py`,
  `tests/test_golden_b.py`, `tests/test_gps_track.py`.
- vehicle-defs (read only): `derived/cl250_derived.yaml` (class-B entries: `inputs`, `range`,
  `resolution`, `record`), `docs/DECISIONS.md` D-055, D-067, D-070, D-075, D-087, D-088, D-093
  (only those entries), `uds/dids.yaml` entries 0xFD02 and 0xFD03, and the codegen that emits the
  rt-core `platform_uds` record tables (find it with grep for `FD03` under `codegen/` or
  `tools/`).
- vehicle-rt-core (read only except LR8-3): `src/features/derived/` (which class-B signals are
  computed, the previous-ride record), `src/services/tester_epoch*` (stop-epoch counter type),
  the platform UDS server buffer / ISO-TP limits under `src/features/uds/` (read only, red),
  `tests/host/test_derived_ride.c`, `tests/host/vectors/`.

### Hard limits of this run

- **No signal facts by hand** (invariant 2): fix-type names, ranges, resolutions and DIDs come from
  `vehicle_defs` at run time, never as literals in the reference. The only literal allowed is
  reusing `gps_track.USABLE_FIX_NAMES` (import it, do not copy it).
- Never read, store or emit a **GPS position** (D-060, D-076). Speed, heading and fix type only.
- No edit in vehicle-defs outside `docs/ideas/`, no defs pin bump, no version bump, no tag, no
  `manifest.yaml`, no `.github/`, no `CLAUDE.md`, no `gen/`.
- rt-core: only files under `tests/host/vectors/` may change, and only through the generator
  (`uv run vehicle-server golden --out ...`), never by hand.

## LR8-1 — Audit: declared but unread inputs of every class-B summary

1. Write a test in vehicle-server (`tests/test_summary_inputs.py`) that, for every class-B signal
   the reference implements (`status` not `not_implemented`), checks that each declared input of
   the defs entry is read by the summary. Use an instrumented `SummaryEnv` (or a spy on its
   `samples`/series accessors) and run each summary on a small synthetic session that has every
   input. The test lists the offenders by name.
2. Expected offender today: `ride_distance_gps` (declares `sensor.gps_fix_type`, reads only
   `sensor.gps_ground_speed`). There may be more; find them, do not guess.
3. Mark the known offenders `xfail(strict=True)` with the E-26 reference in this commit, so LR8-2
   flips them. Record the full offender list in your log.

Commit: `test(server): flag class-B summaries that ignore a declared input (E-26)`.

## LR8-2 — Fix: gate every offender on its declared inputs

1. `ride_distance_gps`: integrate `sensor.gps_ground_speed` only over samples where the latest
   fix-type sample is **usable and fresh by the same rule as `/track`**. Reuse
   `gps_track._usable_fix_values()` / `USABLE_FIX_NAMES` and the defs `stale_after_ms` of the fix
   type (D-087); if the helpers are private, move them into a small shared module
   (`src/vehicle_server/gps_fix.py`) and make `gps_track.py` import it, behaviour unchanged
   (its tests must stay green untouched). A gap with no usable fix contributes **zero distance**,
   never an interpolated one. A ride with no usable fix at all → the summary's existing
   "missing inputs" outcome, not 0.0.
2. Fix any other offender from LR8-1 the same way: the declared input must change the result in a
   way its defs `description` supports. If the description does not say how the input is used,
   **do not invent a rule**: leave it `xfail`, and write the signal and the question under
   *For Claude*.
3. Tests (each a separate case): a ride where fix drops to `noFix` for 10 s mid-ride (distance
   shorter by exactly that stretch); a stale fix-type stream (speed samples after the fix type
   stops updating are not counted); a ride with no usable fix (missing inputs); a ride with full
   fix (result equal to the old one within `resolution / 2`). `ride_odometer_mismatch` consumes
   the GNSS distance: add a test that it follows the new value.
4. Remove the `xfail` marks LR8-1 added for the fixed signals.

Commit: `fix(server): gate class-B ride summaries on every declared input (E-26)`.

## LR8-3 — Regenerate the class-B golden vectors for rt-core

1. Run `uv run vehicle-server golden --out <workspace>/vehicle-rt-core/tests/host/vectors` and
   `uv run pytest tests/test_golden_b.py tests/test_golden.py`.
2. Expected: **no header changes**. `golden_b.py` selects only signals without a GPS input
   (it asserts this), and rt-core does not compute `ride_distance_gps`. Confirm it with
   `git -C vehicle-rt-core status --porcelain tests/host/vectors` and record the result in the log
   ("regenerated, byte-identical" plus the MANIFEST check).
3. Only if a header **does** change (an LR8-2 fix touched a signal rt-core computes): update
   `tests/golden/MANIFEST.sha256` in the server branch, commit the regenerated headers on the
   rt-core branch `ext/opencode-golden-b-regen`, run the rt-core host tests
   (`cmake --preset host-tests && cmake --build --preset host-tests && ctest --preset host-tests`),
   and if a rt-core test fails, **do not change rt-core C code**: write the failing test and the
   signal under *For Claude* (Claude aligns `features/derived` and runs the review).
4. Update the vehicle-server README class-B section and `CLAUDE.md`-free docs only: one sentence
   that class-B summaries honour every declared input and that the GNSS distance uses the `/track`
   fix rule. Close nothing in `ISSUES.md`; add "(1) done in <branch>" to E-26's status cell only.

Commit (server): `docs(server): class-B summaries honour declared inputs; GNSS fix rule shared with /track`.

## LR8-4 — E-27 in vehicle-analyzer: axis edge precision from the axis

1. `src/services/rideSummaryLayout.ts`: add a pure helper that returns the precision of a binned
   axis from **its own range** (first edge min .. last edge max) with the existing
   `precisionForRange` rule. `src/components/RideSummary.tsx` `edgeText` uses it instead of the
   signal's value range. Values and cells stay formatted as today.
2. Unit tests in the existing `rideSummaryLayout` test file: rpm axis (0..12000) gets 0 decimals
   while the signal range is seconds with 1-2 decimals; an axis with sub-unit edges keeps its
   decimals; a single-bin axis; negative edges.
3. Update the Playwright ride-summary spec only if a visible label changes in its fixture.
4. Checks: `npm ci && npm test && npm run build`.

Commit: `fix(analyzer): format ride-summary bin edges with the axis precision (E-27)`.

## LR8-5 — E-27 in vehicle-mobile: the same rule

1. `lib/ui/rides/ride_summary_screen.dart` `_edgeText(edge, range)`: pass the **axis** range
   (first edge min .. last edge max) instead of `signal.range` at both call sites (~314, ~335).
   Put the axis-range helper next to the existing precision helper so it is unit-testable, with
   the **same rule and the same test cases** as LR8-4, so the analyzer and the phone print the
   same labels for the same ride.
2. Checks: `flutter pub get && flutter analyze && flutter test` (do not commit a `pubspec.lock`
   rewrite).
3. In `ISSUES.md` add "fixed in <analyzer branch>, <mobile branch>" to E-27's status cell; do not
   close the row.

Commit: `fix(mobile): format ride-summary bin edges with the axis precision (E-27)`.

## LR8-6 — Review the C3 part 2b ride-summary DID layout against the code (docs only)

Do **not** implement the layout and do not touch `uds/dids.yaml`, codegen or rt-core: that is a
red-zone `/signal-change` for Claude after the user approves. Your job is a compatibility check of
`vehicle-defs/docs/ideas/ride-summary-did-layout.md` against what exists today. Add a section
`## Compatibility review (DeepSeek, 2026-11-02)` at the end of that file with one table row per
check: *check · evidence (file:line) · result OK / MISMATCH / OPEN · note*.

Checks:

1. **DID range:** the proposal uses 0xFD40-0xFD4E; D-070 item 4 reserves 0xFD40-0xFD5F; the YAML
   `record` names and their DIDs. No collision with any DID in `uds/dids.yaml` or the candidate
   catalog.
2. **Sizes table:** recompute every record's field widths from the current YAML with the
   proposal's rule (raw max = `round((range.max − range.min) / resolution)`, width = smallest of
   1/2/4 B whose all-ones value is **strictly above** raw max) with a throwaway script (not
   committed; paste the script in the log). List every row of the table that differs, and any
   signal whose raw max does not fit in 4 B.
3. **Record encoding:** is "big-endian unsigned, saturating" really what the codegen emits for
   0xFD02/0xFD03? Does the existing encoder already support a 4-byte field and a per-field
   NOT_AVAILABLE value, or does the proposal need a codegen feature? Name it.
4. **Header:** the stop-epoch counter type in `services/tester_epoch` versus the proposed
   `uint16`; wrap behaviour; what a reader sees after 65 535 rides.
5. **Payload size:** the largest record (+ 0x62 + 2 DID bytes) against the platform UDS server
   response buffer and the ISO-TP limits in rt-core (single frame vs. multi-frame on the platform
   bus); is 22 B served today by any path?
6. **Which ride:** does rt-core#54 keep a "last closed ride" record that this can be copied from,
   and is RIDE_CLOSED derivable from it at boot (no ride closed yet)?
7. **NOT_AVAILABLE:** which of the scalar fields in each record rt-core computes today (should be
   12) and which would read NOT_AVAILABLE; any field whose valid raw value could equal all-ones.
8. **Server side:** can vehicle-server's class-B reference produce the same raw value for each
   field (same rounding: `round` half-even in Python vs. the C rounding in rt-core)? Flag the
   rounding rule as OPEN if they differ.
9. **Histogram leftovers:** the signals left out of v1 (point 5 of the proposal), checked against
   the YAML: is the list complete, and does any record become empty besides
   RIDE_OPERATING_POINTS?

End the section with a short verdict: "no blocker" or the list of MISMATCH/OPEN rows Claude must
resolve before the decision. Do not change the proposal text above your section.

Commit: `docs(ideas): compatibility review of the ride-summary DID layout (C3 part 2b)`.

## LR8-7 — Log and wrap-up

1. Your log `external-ai/log/2026-11-02-opencode-long-run-8.md` (copy of `TEMPLATE.md`,
   `review: pending`): per task the branch, files, checks with their result, the zone check
   result, the LR8-1 offender list, the LR8-3 byte-identical result, the LR8-6 script.
2. *For Claude*: every red-zone need you met, every offender you left `xfail`, every OPEN row of
   LR8-6.
3. Do not open PRs unless the user asks; push the branches.
