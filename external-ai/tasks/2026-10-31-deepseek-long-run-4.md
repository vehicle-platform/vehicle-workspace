# DeepSeek long run 4 — 2026-10-31 (vehicle-ml attribution normalisation + sessions without IMU)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out (run 3
ended with nothing committed). If a task is blocked, write why in the log's *For Claude* section
and go on to the next one.

## 0. Before you start (read, do not skip)

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Check every
  changed path with `python3 scripts/check_zones.py vehicle-ml --base origin/main` before each
  push. **Red = stop**, write the request into the log.
- `vehicle-ml/CLAUDE.md` methodology rules 1-5 (non-negotiable). This run is about **rule 3**
  (which modality catches which fault, reported separately) and **rule 4** (no generalisation
  claim; what was not tested is "unknown").
- `vehicle-ml/README.md`, sections on the data layer and "Stage 1 (D-083)".
- `src/vehicle_ml/evaluate.py` (`_top_modality`, `pca_alarm_modality`, `z_alarm_modality`,
  `evaluate`), `src/vehicle_ml/baseline.py` (`BaselineModel`, `pca_residuals`, `abs_z`),
  `src/vehicle_ml/data/sources.py` (`MODALITIES`, `feature_metadata`, `imu_columns`),
  `src/vehicle_ml/data/dataset.py` (`build_dataset`, time base per session), `tests/physics_synthetic.py`.
- Last run's log `external-ai/log/2026-10-31-opencode-long-run-3.md` (*Unsure about* and *Claude
  review*): the two known limits you fix here are written there.
- `PLATFORM-RULES.md` invariant 2: names, units and vehicle constants come from
  `vehicle_ml.defs`, never hand-written. Never commit real ride data, GPS or keys (D-033); all test
  data is synthetic.

Branches (one PR, opened against `main`):

| Part | Repo | Branch | Tasks |
|---|---|---|---|
| A | vehicle-ml | `ext/opencode-ml-attribution` | ML-23 .. ML-26 |
| Log | vehicle-workspace | `ext/opencode-long-run-4-log` | the session log |

One session log for the whole run: `external-ai/log/2026-10-31-opencode-long-run-4.md` (copy
`TEMPLATE.md`; `review: pending`; a result row per task with code `file:line`, test names, status).
Create and push the log branch **first**, with the Result table rows marked `todo`, and update it
as tasks finish.

## Part A — vehicle-ml

Same hard rules as runs 2-3: session split, roles not names in library code, numpy/pandas/pyarrow
only (no new dependency), no safety use, no result numbers presented as findings.

### ML-23 PCA attribution normalised per modality
Problem: `pca_alarm_modality` sums squared residuals per modality, so the modality with more
features (IMU: six axes × stats and FFT bands) wins structurally even on healthy windows.
Change: attribute a PCA alarm to the modality with the largest **residual ratio**: the window's
summed squared residual of that modality divided by that modality's **mean summed squared
residual on the healthy training windows** (computed once in `evaluate` from the same windows the
baseline was fitted on, never from val/test). A modality whose training mean is 0 or non-finite is
skipped; if every modality is skipped the window gets `""`. Keep the tie rule (alphabetically
first). Keep the old raw-sum function available only if a test or the report still needs it;
otherwise replace it. robust-z attribution stays as it is (|z| is already scale-free), but say so
in its docstring.
Store the per-modality training means in `evaluation.json` (they are part of the method).
Tests: a hand-built case where IMU has 10 features with small residuals and CAN has 2 features
with one large residual attributes to `can` with the ratio rule (and would have gone to `imu` by
the raw sum); the training means come only from training rows (a test that poisons val/test
rows with huge residuals and checks the means are unchanged); all-skipped → `""`.

### ML-24 Sessions without IMU
Problem: `build_dataset` picks a time base per session; a session without IMU gets a telemetry
base and no IMU features, and `evaluate` has no defined behaviour for such windows.
First write a test that builds a synthetic data dir where some sessions have no IMU file (extend
`tests/physics_synthetic.py` with an option, sensor names from defs as today) and records what
happens now. Then make the behaviour explicit:
- Baseline models (PCA, robust-z) are fitted only on windows that have every baseline feature;
  a window missing any baseline feature gets **no baseline score** (NaN) and is reported as
  "not scored (missing modality)" — never as a detection, a miss or a false alarm.
- Physics models (CAN only) still score those windows.
- `evaluation.json` / `evaluation.md` list, per split, the sessions and windows not scored by the
  baselines and which modality was missing; the per-fault table counts a fault session whose
  windows were all unscored as "not evaluated" for that model, not as missed.
- The dataset card (`dataset.md`) already lists per-session modality availability; check it shows
  these sessions correctly.
Tests: mixed data dir end to end (no crash, unscored windows counted, physics still scores them);
an IMU-less fault session is "not evaluated" for the baselines and evaluated for physics; fitting
never uses a window with a missing feature.

### ML-25 Attribution stability across seeds
`--seeds` (run 3) writes per-seed results and mean/min/max per metric. Add, per model × fault
kind, the fraction of seeds whose first-alarm modality equals `expected_modality`, and the list
of first-alarm modalities per seed, to the aggregate in `evaluation.json` and a table in the
aggregate markdown. A seed where the fault was not detected counts as "no alarm", not as a
mismatch.
Tests: `--seeds 0,1` on a small synthetic dir produces the new aggregate fields with consistent
counts; a hand-built two-seed aggregate gives the expected fraction.

### ML-26 README
README "Stage 1" section: the ratio rule for PCA attribution and why (feature-count bias), the
"not scored (missing modality)" rule, the stability table. No result numbers presented as findings.

Checks for Part A (all must pass before each push): `cd vehicle-ml && uv run pytest -q`,
`uv run ruff check .`, `uv run ruff format --check .`.

## Finish

- Open the vehicle-ml PR (body: task list, checks, `needs-claude-review` if any path is yellow) and
  the workspace PR for the log. Fill the log: Result table, Checks, Unsure about, For Claude.
- Do not merge anything. Do not edit `STATUS.md`, `ISSUES.md`, `DECISIONS.md`, any `CLAUDE.md`.
- Put into *For Claude*: every place where the rules above were ambiguous and the choice you made,
  what the ML-24 "before" test showed, and any dependency you wanted (with licence).
