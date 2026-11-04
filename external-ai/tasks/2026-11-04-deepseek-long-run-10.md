# DeepSeek long run 10 — 2026-11-04 (vehicle-ml D-083 stage 2 on synthetic data)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR10-1..LR10-6 | vehicle-ml | `ext/opencode-ml-stage2` | green (`pyproject.toml` yellow: do not touch it) |
| LR10-7 | vehicle-workspace `external-ai/log/` | (your log) | green |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### What this run is

D-083 (vehicle-defs `docs/DECISIONS.md`, on main; read the whole entry and D-079, D-088)
stages the anomaly work. Stage 1 (classical physics estimators + a baseline **without physics**,
synthetic evaluation) is done on vehicle-ml main. This run builds the **stage-2 machinery** and
runs it on **synthetic data only**:

1. a session split that **holds out an operating-point band** (unseen temperatures, unseen
   loads; D-083 item 3 stage 2 "generalisation to unseen temperatures and loads");
2. a **physics-weighted hybrid score** (D-083 item 2: the physics enters as a weighted term, the
   weight is a tuned hyper-parameter, and the score **always** contains the physics residual);
3. a **generalisation report** that compares physics, `baseline_pca`, `baseline_z` and the hybrid
   in-distribution vs on the held-out band.

No real ride exists yet and no HIL fault injection exists yet. Every number this run produces is
a property of the synthetic generator, **never** a thesis result (vehicle-ml rule 4). The
existing `SYNTHETIC_NOTE` must appear in every new report.

No decision is needed from the user for this run: it stays inside D-083 and vehicle-ml's rules.
If you find that something here contradicts D-083 or vehicle-ml `CLAUDE.md`, the decision text
wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clone `vehicle-ml/` (not under `.claude/worktrees/`, that is Claude's area).
- First `git -C vehicle-ml checkout main && git -C vehicle-ml pull`, then
  `git checkout -b ext/opencode-ml-stage2`. Right after that, and again at the end, run from the
  workspace root: `python3 scripts/vscode_workspace.py` (it refreshes the VS Code folder list).
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py vehicle-ml --base origin/main` from the workspace root.
  **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-ml `CLAUDE.md` (methodology rules 1-5; rule 1 session-based split, rule 3 modality per
  fault, rule 4 no generalisation claim) and `README.md` (sections *Stage 1*, *Attribution*,
  *Sessions without IMU*, *Several split seeds*, and the "deliberately not modelled" list).
- vehicle-ml code: `src/vehicle_ml/split.py` (`assign_split`, `split_sessions`, `group_kfold`,
  `assert_no_leakage`), `src/vehicle_ml/evaluate.py` (`MODEL_NAMES`, `SYNTHETIC_NOTE`,
  `_physics_scores`, `_threshold`, `_false_alarms`, `_fault_results`, `_fit_baseline`,
  `evaluate`, `evaluate_seeds`, `aggregate_metrics`, `_markdown`), `src/vehicle_ml/baseline.py`
  (`BaselineModel.scores`), `src/vehicle_ml/physics/config.py` (`RoleMap`, `load_roles`),
  `configs/physics_cl250.toml`, `src/vehicle_ml/cli.py`, and the tests
  `tests/physics_synthetic.py` (`PhysicsSessionSpec.ambient_c`, `.load`, `FAULT_KINDS`),
  `tests/test_evaluate.py`, `tests/test_split.py`.

### Hard limits of this run

- **Synthetic data only** (D-033): never read, commit or describe a real ride, a VIN or a GPS
  position. Test data is generated in `tmp_path`.
- **No new dependency** (numpy, pandas, pyarrow only; no torch, scikit-learn, scipy). No neural
  network, no isolation forest, no autoencoder: those need a dependency decision (README). Do not
  edit `pyproject.toml` or `uv.lock`.
- **Invariant 2:** library code names roles, never defs signal names. Any new role goes into
  `configs/physics_cl250.toml` and is validated by `load_roles` like the existing ones; never a
  signal literal in `src/`.
- **Rule 1:** every split is by session. A session is in exactly one part; extend
  `assert_no_leakage` coverage to every new split.
- **Invariant 3 / D-083 item 4:** nothing outputs to a node; no threshold here is a safety value.
- **Do not change stage-1 behaviour:** `vehicle-ml evaluate` without the new options must write
  the same `evaluation.json` as today (an existing-output regression test proves it, LR10-5).
- Do not weaken checks (no skipped tests, no `# noqa`, no lowered thresholds in existing tests).
  No version bump, no tag, no `CLAUDE.md`, no `.github/`, no edit in any other repo.

## LR10-1 — Operating point per session (data-derived)

1. Add an optional `[operating_point]` table to `configs/physics_cl250.toml` mapping two axes to
   **existing** roles: `temperature = "coolant_temp"` and `load = "engine_speed"`. Validate it in
   `physics/config.py` (unknown axis or role not in `[roles]` = a clear `ValueError`; the table
   is optional, a config without it still loads).
2. New module `src/vehicle_ml/operating_point.py`: `session_operating_points(...)` returns, per
   session, the **median** of each configured role over the session's valid samples, plus the
   sample count. A session without valid samples for an axis gets `None` for it and is reported,
   never guessed. The value comes from the recorded data only, never from `faults.json` or the
   synthetic spec.
3. Docstring and README state plainly that these are **proxies** (median coolant temperature for
   ambient temperature, median engine speed for load) and why (no ambient-temperature signal in
   the role map).
4. Tests: medians on a synthetic set with known `ambient_c`/`load` are monotonic in the spec
   values; missing role data gives `None`; config validation errors.

## LR10-2 — Held-out operating-point split

1. `split.py`: `split_by_band(points, axis, band, *, seed, fractions)` (or a name in the style of
   the file) puts every session whose operating point on `axis` lies inside the closed `band`
   into a `test_holdout` part, and splits the remaining sessions into train/val/test exactly like
   `split_sessions` with the same seed. A session with `None` on that axis is excluded and listed.
2. `assert_no_leakage` must hold across all four parts; train and val must contain **no** session
   inside the band.
3. Refuse (clear `ValueError`) a band that leaves train or val without healthy sessions, or a
   holdout part with no session.
4. Tests: determinism per seed, no leakage, band edges inclusive, the refusal cases.

## LR10-3 — Physics-weighted hybrid score (D-083 item 2)

1. New module `src/vehicle_ml/hybrid.py`. Per window:
   `hybrid = w * physics_score + (1 - w) * baseline_score`, where `physics_score` is the existing
   stage-1 physics score and `baseline_score` the existing `baseline_pca` score, **both already on
   the robust train-healthy scale used by `_physics_scores` / the baseline** (if the two are not on
   one scale, normalise each by its train-healthy median/MAD first and document it).
2. `w` comes from a fixed grid `(0.25, 0.5, 0.75, 1.0)`. **`w = 0` is never allowed** (the score
   always includes the physics residual itself); a test proves the grid and the constructor refuse
   `w <= 0`.
3. Tuning on the **validation** split only: threshold each candidate at the target false-alarm
   rate on validation healthy sessions (reuse `_threshold`), then pick the `w` that detects the
   most validation fault sessions; ties go to the smaller mean detection delay, then the larger
   `w`. If validation has no fault session, use `w = 0.5` and mark it `not tuned` in the report.
   The test split is never used for tuning (test this).
4. A window the physics model did not score (gap, not identifiable) is unscored for the hybrid too:
   never fall back to the baseline alone (that would drop the physics term). Count such windows.
5. Rule 3: the hybrid alarm's modality is the physics group's modality when the physics term
   is the larger weighted contribution, else the baseline's attribution; report which term
   dominated per alarm.
6. Add `hybrid` to the models the evaluator reports **only when the new option is used** (LR10-4);
   the default `MODEL_NAMES` output stays unchanged.

## LR10-4 — Generalisation evaluation

1. `evaluate(...)` gains keyword options `holdout_axis: str | None = None`,
   `holdout_band: tuple[float, float] | None = None`, `hybrid: bool = False`; the CLI gains
   `--holdout temperature:LOW:HIGH` (or `load:LOW:HIGH`) and `--hybrid`. Without them the output
   is today's output.
2. With a holdout, report for every model the same metrics as today (false alarms per hour,
   detection delay, missed faults, modality per fault kind) **twice**: on the in-distribution
   `test` part and on `test_holdout`, plus the operating-point band, the axis proxy role, the
   excluded sessions and `SYNTHETIC_NOTE`. Deltas between the two are differences of reported
   numbers only; no new statistic.
3. Thresholds are always fitted on validation healthy sessions (in-distribution); never refit on
   the holdout.
4. `--seeds` works with `--holdout` (the holdout part is the same for every seed; only the
   remaining split changes) through `evaluate_seeds` / `aggregate_metrics`.
5. `evaluation.md` gets a short *Generalisation (synthetic)* section; `evaluation.json` keeps its
   current keys and adds a `generalisation` object.

## LR10-5 — Synthetic scenario and tests

1. A test helper (in `tests/physics_synthetic.py` style) that builds a dataset spanning
   `ambient_c` 0-40 °C and `load` 0.3-1.2, healthy and faulty sessions of every `FAULT_KINDS`
   entry, enough sessions that train, val, test and the holdout each have healthy sessions and
   at least one fault of each CAN kind (`EXPECTED_MODALITY == "can"`).
2. Tests: end to end `evaluate(..., holdout_axis="temperature", holdout_band=(30.0, 45.0),
   hybrid=True)` writes both reports with the new sections; the default `evaluate(...)` output is
   **byte-identical** (after removing timestamps, if any) to the output of the current main code on
   the same data (write the expected JSON from main first, commit it as a fixture or compute it in
   the test from a frozen copy; explain your choice in the log); CLI parsing of `--holdout`.
3. **Do not tune the generator to make a model win.** If you add an "expected direction" check
   (for example: the physics cooling score keeps its false-alarm rate on the hot holdout better
   than `baseline_pca`), record the observed numbers in the log; if the direction does not hold,
   leave it failing out of the suite (do not assert it) and describe it under *For Claude*.

## LR10-6 — Docs inside the repo

1. `README.md`: a *Stage 2 (D-083, synthetic)* section: the operating-point proxies, the holdout
   split, the hybrid score and its `w` grid and tuning rule, the never-zero physics weight, the
   CLI example, and the statement that stage 2 on real rides and HIL fault injection is still to
   come (needs data and the HIL bench). Update the status line at the top.
2. Do not edit `CLAUDE.md` (red).

## LR10-7 — Checks, log and wrap-up

1. From `vehicle-ml/`: `uv sync`, `uv run pytest`, `uv run ruff check .`,
   `uv run ruff format --check .` all green. Paste the pass counts into the log.
2. `python3 scripts/check_zones.py vehicle-ml --base origin/main` from the workspace root:
   expect green only.
3. Your log `external-ai/log/2026-11-04-opencode-long-run-10.md` (copy of `TEMPLATE.md`,
   `review: pending`) on a workspace branch `ext/opencode-long-run-10-log`: per task the files,
   checks with their results, the zone result, the observed synthetic numbers of LR10-5 (2) and
   (3), the regression-fixture choice, every doubt.
4. Push both branches. Open **one** PR `vehicle-platform/vehicle-ml` from `ext/opencode-ml-stage2`
   to `main` (body: summary, checks, zone result, log file name) and do not merge it.
5. Run `python3 scripts/vscode_workspace.py` once more from the workspace root.
