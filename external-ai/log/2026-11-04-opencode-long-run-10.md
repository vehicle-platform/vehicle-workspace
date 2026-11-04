---
date: 2026-11-04
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-10
repos: [vehicle-ml, vehicle-workspace]
branches: [vehicle-ml:ext/opencode-ml-stage2, vehicle-workspace:ext/opencode-long-run-10-log]
prs: [https://github.com/vehicle-platform/vehicle-ml/pull/16]
zone: green
review: pending
---

# vehicle-ml D-083 stage 2 on synthetic data

## Goal
Build the D-083 stage-2 machinery in vehicle-ml on synthetic data only: data-derived
operating-point proxies, an operating-point band holdout split, a physics-weighted hybrid
score, a generalisation report, tests and docs. No real ride, HIL or safety claim; no new
dependency and no change to stage-1 default output.

## Changes

### LR10-1 — Operating-point proxies
- `configs/physics_cl250.toml`: optional `[operating_point]` maps `temperature="coolant_temp"`
  and `load="engine_speed"`.
- `src/vehicle_ml/physics/config.py`: `OPERATING_POINT_AXES`, validates the table and every
  axis role against `[roles]`; a config without the table still loads.
- `src/vehicle_ml/operating_point.py`: `OperatingPoint`, `load_role_frame`,
  `session_operating_points`; median finite samples per axis and `None` when absent.
  Values come from recorded data only, never from `faults.json` or the synthetic spec.
- `tests/test_operating_point.py`: medians, monotonic proxy values, missing axis and config
  validation.
- Commit `f38627f` (`feat(ml): add data-derived operating-point proxies`); pushed.
- Check: `uv run pytest tests/test_operating_point.py -q` → 5 passed.
- Zone: GREEN for every touched file.

### LR10-2 — Held-out operating-point split
- `src/vehicle_ml/split.py`: `split_by_band(points, axis, band, *, seed, fractions,
  healthy=None)`; closed band, `test_holdout` part, `excluded` sessions for a `None` proxy,
  and a clear `ValueError` when the holdout is empty or train/val lacks sessions or healthy
  sessions. `SPLIT_PARTS` includes `test_holdout`; `assert_no_leakage` covers all four parts.
- `tests/test_split.py`: determinism, no leakage, inclusive edges, refusals and healthy
  constraints.
- Commit `1eae3d8` (`feat(ml): hold out an operating-point band by session`); pushed.
- Check: `uv run pytest tests/test_split.py -q` → 14 passed.
- Zone: GREEN.
- Later LR10-4 makes the holdout list sorted so `--seeds` reports the same membership in a
  stable order; membership itself was already seed-independent.

### LR10-3 — Physics-weighted hybrid score
- `src/vehicle_ml/hybrid.py`: `HYBRID_WEIGHTS=(0.25, 0.5, 0.75, 1.0)`, `HybridScorer`,
  train-healthy median/MAD normalisation, `w <= 0` refusal, and unscored propagation when
  either the physics or the baseline window is unscored.
- `tests/test_hybrid.py`: grid, constructor refusal, formula, normalisation, unscored
  propagation and smaller/larger weight behaviour.
- Commit `05599c2` (`feat(ml): add the physics-weighted hybrid score`); pushed.
- Check: `uv run pytest tests/test_hybrid.py -q` → 11 passed.
- Zone: GREEN.

### LR10-4 — Generalisation evaluation and CLI
- `src/vehicle_ml/evaluate.py`: `evaluate(..., holdout_axis=None, holdout_band=None,
  hybrid=False)`. Holdout mode replaces the split, loads operating points from recorded
  frames, and reports every model twice (`test` and `test_holdout`) with false alarms per
  hour, detection delay, misses, not-evaluated counts, modalities/groups and deltas.
  Thresholds stay on validation healthy sessions. Hybrid mode tunes only validation fault
  sessions, uses `w=0.5` and `tuned=false` when validation has no fault, reports the grid,
  chosen threshold, unscored window counts and dominant term per alarm.
- `src/vehicle_ml/cli.py`: `--holdout AXIS:LOW:HIGH` and `--hybrid`; malformed/unknown
  holdout produces return code 2.
- `src/vehicle_ml/split.py`: sorted `test_holdout` so `evaluate_seeds` keeps the same
  holdout list for every seed.
- `_seed_metrics` adds `model.holdout.*` aggregates when generalisation is present.
- Commit `516ce15` (`feat(ml): add held-out generalisation evaluation`); pushed.
- Checks: `uv run ruff check`/format on the files passed; `tests/test_stage2.py` →
  7 passed after the LR10-5 tests were added.
- Zone: GREEN.
- Default `evaluate` output: identical to the stage-1 fixture after canonicalising
  platform-dependent float last bits (LR10-5).

### LR10-5 — Synthetic scenario and tests
- `tests/physics_synthetic.py`: `GENERALISATION_PHYSICS_SESSIONS` (42 sessions) and
  `make_generalisation_data_dir`. The scenario spans ambient 0–40 °C and load 0.3–1.2,
  healthy and faulty sessions for every `FAULT_KINDS` entry, and seed-0 split counts
  train 20, val 5, test 5, test_holdout 12. Every part has healthy sessions and at least one
  fault of every CAN kind; the holdout also has `wheel_vibration`.
- `tests/test_stage2.py`: end-to-end CLI `--holdout temperature:30:45 --hybrid`, default
  fixture regression, malformed CLI holdout, holdout stability across `--seeds`, tuning
  ignoring test rows/faults, `w=0.5` not-tuned fallback, and unknown-axis refusal.
- Regression fixture choice: `tests/fixtures/evaluation_stage1_default.json` was written by
  the current `main` code on the default synthetic dataset before the stage-2 changes, then
  committed as the frozen expected JSON. It has no timestamps. The first CI run failed only
  because Linux/BLAS spellings of a few floats differed from macOS in the last bits
  (`75.99032330757854` vs `75.99032330757791`, etc.); the evaluation numbers were equal.
  The test therefore canonicalises floats to 12 significant digits before comparing the
  serialised JSON, while keys, strings, lists and integers stay exact. This is a
  cross-platform necessity, not a loosened metric threshold. If stage-1 output changes
  intentionally, regenerate the fixture in the same PR that changes the output.
- Commit `394d6bc` (`test(ml): add the synthetic generalisation scenario`); pushed. Follow-up
  `ef95008` (`test(ml): compare the stage-1 fixture modulo float last bits`) makes the
  fixture comparison platform-stable; pushed.
- Check: `uv run pytest tests/test_stage2.py -q` → 7 passed in 29.64s before the canonical
  comparison, 7 passed in 28.47s after it.
- Zone: GREEN.

Observed LR10-5 synthetic numbers (final run):
- Split: train 20, val 5, test 5, test_holdout 12; excluded 0; proxy `coolant_temp`;
  axis `temperature`; band `[30.0, 45.0]`.
- Hybrid: `w=0.75`, `tuned=true` (`validation fault sessions`), threshold
  `14.239944`; candidates all detected 3 validation fault sessions with mean delay 0 ms
  except `w=1.0` (6666.67 ms); unscored windows 0 in every part.
- False alarms per hour (test → holdout): physics `0.0 → 128.571` (delta +128.571);
  `baseline_pca` `0.0 → 120.000` (+120.000); `baseline_z` `0.0 → 137.143` (+137.143);
  hybrid `0.0 → 128.571` (+128.571). Test healthy time was 0.0167 h; holdout healthy time
  was 0.1167 h.
- Holdout fault detection: all four models detected 1/1 session of every holdout kind
  (four CAN kinds plus `wheel_vibration`). The physics and hybrid `wheel_vibration`
  "detection" was attributed to the `charging` group; this is probably the cold
  distribution shift, not IMU content, and is not asserted.
- In-distribution test: physics detected 1/1 for all four CAN kinds; `baseline_pca`,
  `baseline_z` and hybrid missed the single `fan_failure` test session (0/1) and detected
  1/1 for the other three. This is a synthetic observation, not a tuning target.

### LR10-6 — README
- `README.md`: status line updated; new `## Stage 2 (D-083, synthetic)` section covers the
  operating-point proxies, holdout split/report, hybrid formula, `(0.25, 0.5, 0.75, 1.0)`
  grid, validation-only tuning, the never-zero physics weight, unscored propagation and
  modality attribution. It includes the `--holdout`/`--hybrid` CLI example and states that
  real-ride and HIL fault-injection stage 2 is still to come.
- Commit `dbff60d` (`docs(ml): describe the synthetic stage-2 evaluation`); pushed.
- Zone: GREEN.

### LR10-7 — Checks and wrap-up
- `uv sync` → 15 packages checked.
- `uv run pytest -q` → 186 passed in 144.08s after the canonical fixture comparison.
- `uv run ruff check .` → all checks passed.
- `uv run ruff format --check .` → 58 files already formatted.
- `python3 scripts/check_zones.py vehicle-ml --base origin/main` → all GREEN.
- Workspace log branch `ext/opencode-long-run-10-log`; log file
  `external-ai/log/2026-11-04-opencode-long-run-10.md`.
- `scripts/vscode_workspace.py` was run from the workspace root; the generated
  `vehicle-platform.code-workspace` is untracked and is not committed.
- One non-merged vehicle-ml PR from `ext/opencode-ml-stage2` to `main`:
  https://github.com/vehicle-platform/vehicle-ml/pull/16. CI check `test` passed in
  2m32s; merge state CLEAN/MERGEABLE; not merged.

## Result
All LR10-1..LR10-6 changes are implemented, tested and pushed on
`vehicle-ml:ext/opencode-ml-stage2`. LR10-7 checks are green and the PR CI check passed.
The default stage-1 output matches the fixture after canonicalising platform-dependent
float last bits. Stage 2 remains synthetic-only: no real ride, HIL or safety claim, no new
dependency, no `pyproject.toml`/lock change. The vehicle-ml PR is not merged.

## Checks
- `uv run pytest tests/test_operating_point.py -q`: 5 passed.
- `uv run pytest tests/test_split.py -q`: 14 passed.
- `uv run pytest tests/test_hybrid.py -q`: 11 passed.
- `uv run pytest tests/test_stage2.py -q`: 7 passed.
- `uv run pytest -q`: 186 passed in 144.08s.
- `uv run ruff check .`: all checks passed.
- `uv run ruff format --check .`: 58 files already formatted.
- `python3 scripts/check_zones.py vehicle-ml --base origin/main`: all GREEN.
- No skipped tests, no `# noqa`, no lowered thresholds.

## Unsure about
- The expected direction check does not hold. On the cold holdout, physics cooling false
  alarms are 128.571/h versus 120.000/h for `baseline_pca`; physics is not better. The
  holdout is only 12 sessions / 0.1167 healthy hours, so these rates are coarse synthetic
  numbers. No direction assertion is in the suite, per the task.
- The physics model "detects" `wheel_vibration` on the cold holdout and attributes it to
  the `charging` group. Since a wheel vibration changes only IMU and every CAN/derived
  column stays healthy, this is most likely a cold-shift false attribution rather than a
  real detection. It is not asserted as a success criterion.
- The hybrid misses the single `fan_failure` test session because the baseline misses it;
  the physics model detects it. The hybrid threshold/weight are validation-selected, so
  this is reported as observed and not tuned away.
- The regression fixture locks the complete stage-1 JSON except float last bits, which are
  canonicalised to 12 significant digits for Linux/macOS stability. Any intentional
  stage-1 output change must regenerate it; the test failure is the intended warning.
- The holdout list is sorted in `split_by_band` to keep reports stable across seeds. This
  does not change membership or the stable train/val/test hash split.

## For Claude
- Please review the failed expected-direction observation above: physics holdout false
  alarms (128.571/h) are worse than `baseline_pca` (120.000/h) on this synthetic cold
  holdout. I did not add a direction assertion and did not tune the generator.
- Please check the cold-holdout `wheel_vibration` attribution: physics/hybrid report a
  detection via `charging`, despite no CAN change; I suspect distribution shift.
- Please check the hybrid `fan_failure` test miss: baseline-only miss dominates the hybrid.
- CI first failed on exact floating-point byte comparison, not on an evaluation result;
  `ef95008` canonicalises only float last bits. Please confirm that this deviation from
  literal byte equality is acceptable.
- No red-zone edits were made; `pyproject.toml`, `CLAUDE.md`, `.github/` and other repos
  were untouched.
- The vehicle-ml PR https://github.com/vehicle-platform/vehicle-ml/pull/16 should stay
  open and unmerged; the workspace log commit is part of LR10-7.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
