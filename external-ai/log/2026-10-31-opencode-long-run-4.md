---
date: 2026-10-31
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-4-attribution
repos: [vehicle-ml, vehicle-workspace]
branches: [vehicle-ml:ext/opencode-ml-attribution, vehicle-workspace:ext/opencode-long-run-4-log]
prs: [vehicle-ml#14, vehicle-workspace#133]
zone: green
review: pending
---

# DeepSeek long run 4 — attribution normalisation and sessions without IMU

## Goal
Fix the two limits recorded after long run 3: normalise PCA attribution per modality and
define the behaviour for sessions without IMU, then report attribution stability across split
seeds and document it.

## Changes
- `vehicle-ml/src/vehicle_ml/evaluate.py`: PCA alarms now use the per-modality residual ratio (window sum / healthy-training mean) instead of the raw sum; the training means are computed from complete healthy train windows and stored in `evaluation.json`; the baseline scaler is fitted on complete train windows only. `vehicle-ml/tests/test_evaluate.py` covers the ratio case, skipped means, and train-only means.
- `vehicle-ml/tests/physics_synthetic.py`: added `PhysicsSessionSpec.has_imu`; an IMU-less session writes no `imu.parquet` and the index records `has_imu=0`. `vehicle-ml/src/vehicle_ml/evaluate.py`: baseline fit and scaler use complete train windows only; unscored windows are listed per split in `baseline_unscored` and the report; baseline scores are NaN for those windows; fault entries distinguish `not_evaluated` from `missed`; false-alarm hours count scored windows only. Tests cover the mixed data dir, the IMU-less fault session, the dataset card, and a baseline fit with a missing feature.
- `vehicle-ml/src/vehicle_ml/evaluate.py`: `aggregate_attribution` stores, per model × fault kind, the seeds with that fault kind, the first-alarm modality per seed (`no alarm`, `not evaluated` or `mixed` where needed), the match count and fraction; the aggregate markdown has an attribution-stability table. `_seed_metrics` now excludes `not_evaluated` sessions from the detection denominator and reports `not_evaluated_rate`. Tests cover the two-seed aggregate, the all-unscored seed, and the CLI path.
- `vehicle-ml/README.md`: Stage 1 now documents the PCA ratio rule and its feature-count rationale, the "not scored (missing modality)" baseline rule, the dataset-card availability check, and the attribution-stability table. No result numbers are presented as findings.

## Result
| Task | Code | Tests | Status |
|---|---|---|---|
| ML-23 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`pca_training_means`, `pca_alarm_modality`, `_fit_baseline`) | `tests/test_evaluate.py::test_pca_ratio_removes_the_feature_count_advantage`, `::test_pca_attribution_skips_zero_and_non_finite_training_means`, `::test_pca_training_means_read_only_the_training_sessions` | done `77c3514` |
| ML-24 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`_fit_baseline`, `_baseline_unscored`, `_fault_results`), `tests/physics_synthetic.py` (`has_imu`) | `tests/test_evaluate.py::test_sessions_without_imu_are_unscored_but_physics_scores`, `tests/test_physics_synthetic.py::test_session_without_imu_writes_no_imu_file`, `tests/test_baseline.py::test_fit_ignores_a_window_with_a_missing_feature` | done `c5a6286` |
| ML-25 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`aggregate_attribution`, `_seed_first_alarm_modality`, `_seed_metrics`) | `tests/test_evaluate.py::test_aggregate_attribution_treats_no_alarm_as_not_a_match`, `::test_aggregate_attribution_reports_all_unscored_seeds`, `::test_seeds_write_per_seed_entries_and_an_aggregate` | done `d1457b1` |
| ML-26 | `vehicle-ml/README.md` | docs only; full `pytest`/`ruff` checks below | done `bc4984d` |

## Checks
- `cd vehicle-ml && uv run pytest -q`: pass (152 passed).
- `cd vehicle-ml && uv run ruff check .`: pass.
- `cd vehicle-ml && uv run ruff format --check .`: pass.
- `python3 scripts/check_zones.py vehicle-ml --base origin/main`: green (`README.md`, `src/vehicle_ml/evaluate.py`, `tests/physics_synthetic.py`, `tests/test_baseline.py`, `tests/test_evaluate.py`, `tests/test_physics_synthetic.py`).
- `python3 scripts/check_zones.py . --path external-ai/log/2026-10-31-opencode-long-run-4.md`: green.

## Unsure about
- All evidence is synthetic; no real ride, GPS or personal data was used, and no result is
  a generalisation claim (rule 4).
- `PhysicsSessionSpec.has_imu` is a test-fixture option only; production data still comes
  from `vehicle-server` and the session index.
- I used the training mean of the **summed** squared residual per modality, matching the
  wording in ML-23; the per-feature mean would change the ratio.
- No new dependency was needed (numpy/pandas/pyarrow only).

## For Claude
- ML-23 ambiguity: I compute each modality's training mean over the complete healthy
  train windows only, using the summed squared residual per window (the same quantity the
  ratio divides). I replaced the raw-sum PCA attribution rather than keeping a second
  public function; no test or report needs the old one.
- ML-24 "before" observation: `evaluate` did not crash on a mixed dir, but an IMU-less
  fault session was counted as `missed` for both baselines and the report had no coverage
  field; physics still scored it. The new behaviour records it as `not_evaluated` for the
  baselines.
- ML-24 ambiguity: a fault session with only some windows unscored is counted as
  `missed` when its scored windows do not alarm; only an all-unscored session is
  `not_evaluated`. Say if you want partial coverage reported separately.
- ML-25 ambiguity: a fault kind can have several test sessions in one seed. I collapse
  their first-alarm modalities to one seed value; if they disagree the seed is `mixed`,
  which is not a match. The fraction denominator is all seeds that had the fault kind in
  their test split, including `no alarm` and `not evaluated` seeds.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
