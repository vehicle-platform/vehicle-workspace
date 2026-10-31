---
date: 2026-10-31
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-4-attribution
repos: [vehicle-ml, vehicle-workspace]
branches: [vehicle-ml:ext/opencode-ml-attribution, vehicle-workspace:ext/opencode-long-run-4-log]
prs: []
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

## Result
| Task | Code | Tests | Status |
|---|---|---|---|
| ML-23 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`pca_training_means`, `pca_alarm_modality`, `_fit_baseline`) | `tests/test_evaluate.py::test_pca_ratio_removes_the_feature_count_advantage`, `::test_pca_attribution_skips_zero_and_non_finite_training_means`, `::test_pca_training_means_read_only_the_training_sessions` | done `77c3514` |
| ML-24 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`_fit_baseline`, `_baseline_unscored`, `_fault_results`), `tests/physics_synthetic.py` (`has_imu`) | `tests/test_evaluate.py::test_sessions_without_imu_are_unscored_but_physics_scores`, `tests/test_physics_synthetic.py::test_session_without_imu_writes_no_imu_file`, `tests/test_baseline.py::test_fit_ignores_a_window_with_a_missing_feature` | done `c5a6286` |
| ML-25 | todo | todo | todo |
| ML-26 | todo | todo | todo |

## Checks
- Pending.

## Unsure about
- Pending.

## For Claude
- ML-24 "before" observation: `evaluate` did not crash on a mixed dir, but an IMU-less
  fault session was counted as `missed` for both baselines and the report had no coverage
  field; physics still scored it. The new behaviour records it as `not_evaluated` for the
  baselines.
- ML-24 ambiguity: a fault session with only some windows unscored is counted as
  `missed` when its scored windows do not alarm; only an all-unscored session is
  `not_evaluated`. Say if you want partial coverage reported separately.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
