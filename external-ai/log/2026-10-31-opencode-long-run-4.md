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

## Result
| Task | Code | Tests | Status |
|---|---|---|---|
| ML-23 | `vehicle-ml/src/vehicle_ml/evaluate.py` (`pca_training_means`, `pca_alarm_modality`, `_fit_baseline`) | `tests/test_evaluate.py::test_pca_ratio_removes_the_feature_count_advantage`, `::test_pca_attribution_skips_zero_and_non_finite_training_means`, `::test_pca_training_means_read_only_the_training_sessions` | done `77c3514` |
| ML-24 | todo | todo | todo |
| ML-25 | todo | todo | todo |
| ML-26 | todo | todo | todo |

## Checks
- Pending.

## Unsure about
- Pending.

## For Claude
- Pending.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
