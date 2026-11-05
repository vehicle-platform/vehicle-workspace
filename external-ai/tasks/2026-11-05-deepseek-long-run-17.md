# DeepSeek long run 17 — 2026-11-05 (D-079 health windows in the vehicle-server reference)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR17-0 (first!) and LR17-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-17-log` | green |
| LR17-1 ... LR17-5 | vehicle-server | `ext/opencode-server-health-windows` | green (yellow: any path with `gps`, `position`, `mdf4` in it, `pyproject.toml`, `uv.lock`; red: `*ota*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`: do not touch) |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

D-079 (vehicle-defs `docs/DECISIONS.md`) defines five health-snapshot windows W1-W5: the same
measurement under the same operating condition on every ride, so rides can be compared. The
windows and their thresholds are in defs (`derived/cl250_derived.yaml` → `windows:` block, exposed
as `vehicle_defs.vehicle_derived.WINDOWS`; the window signals carry `window: <key>`). The server
reference (D-070 item 2) does not compute them yet: `src/vehicle_server/derived/summary.py` marks
every ready window signal `not_implemented` with `_WINDOW_REASON` ("window state machine not
implemented"; ISSUES E-30 item 4). This run builds that state machine and the window signals
whose inputs exist today, on the stored session data. 19 window signals are ready (no
`pending_inputs`); the others (pump current, 1 kHz crank sample, vibration) stay as they are.

No decision is needed from the user. If something here contradicts a decision (D-033, D-069
item 3, D-070, D-075, D-079, D-087, D-103) or `vehicle-server/CLAUDE.md`, the decision text wins:
write the conflict into *For Claude* and skip that part. **Section 2 below is Claude's reading of
D-079 for the reference; implement it exactly and list it in the README as provisional.** Where
it is still not enough to compute a signal, do not invent a rule: leave that signal
`not_implemented` with a specific reason and write it into *For Claude*.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clone `vehicle-server/` and the workspace root (not under `.claude/worktrees/`,
  that is Claude's area).
- `git -C vehicle-server checkout main && git -C vehicle-server pull && git -C vehicle-server
  submodule update --init`, then `git -C vehicle-server checkout -b
  ext/opencode-server-health-windows`. In the workspace: `git checkout main && git pull && git
  checkout -b ext/opencode-long-run-17-log`. Right after creating each branch, and again at the
  end, run from the workspace root: `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root (zones, branches, trailer, log format, the check table §4).
  Before each push run `python3 scripts/check_zones.py vehicle-server --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-defs `docs/DECISIONS.md` D-079 (one entry, ~20 lines) and D-069 item 3 (engine-start
  detection). Do not read the large docs.
- vehicle-defs `derived/cl250_derived.yaml`: the header comment on `windows:` (lines ~31-52), the
  `windows:` block, the `window_*` signals, and `vehicle/cl250_constants.yaml`
  `window_cold_soak_max_delta_degc`.
- vehicle-server: `CLAUDE.md`, `src/vehicle_server/derived/summary.py` (how a class-B summary is
  registered with `@_summary`, `SummaryEnv`, `Outcome`, `_checked`, the `NOT_IMPLEMENTED_REASONS`
  block, `MissingInputs`), `derived/d103_summaries.py` (flag constants, `_valid`, how a summary
  reads a `const.*` input), `derived/engine.py` (staleness: `stale_after_ms` per input, D-087),
  `derived/golden_b.py` `classify()`, and the tests `test_derived_summary.py`,
  `test_derived_d103_summaries.py`, `test_golden_b.py`, `tests/derived_helpers.py`.
- Note the name clash: `derived/d103_windows.py` is about D-103 sliding windows, **not** D-079.
  Put the new code in `derived/health_windows.py` (state machine) and
  `derived/health_window_summaries.py` (the signals).

### Hard rules for this run

1. **No literal threshold, duration or signal name.** Window conditions, `stable` bands,
   `min_duration_ms`, `max_duration_ms` and `opens_on` come from `vehicle_derived.WINDOWS`; the
   cold-soak delta from its `const.*` input; signal names, units and ranges from
   `vehicle_derived.SIGNALS`. A test proves that patching a `WINDOWS` value changes the result.
2. **Golden vectors unchanged.** rt-core implements the windows later; the window signals must
   **not** enter the golden B selection in this run. Add an explicit skip reason in
   `golden_b.classify()` (e.g. `SKIP_HEALTH_WINDOW`), and `uv run vehicle-server golden --out
   <tmp>` must reproduce `tests/golden/MANIFEST.sha256` byte for byte. If it does not, stop and
   write it into *For Claude*.
3. **Never a held value, never a position.** A stale or invalid input = condition not met (defs
   header). No GPS input is used by any window.
4. **Pure and synthetic.** The state machine is a pure function over time-stamped samples (no I/O,
   no clock). Tests use synthetic series only; no real ride data in git (D-033).
5. **No new dependency, no new route, no change to `/summary` or `/rides` code.** The new scalar
   signals appear there through the existing class-B machinery.

## 1. What exists

`/summary` already returns every class-B scalar from `derived_summary.parquet`; once a window
signal is a computed scalar it shows up in vehicle-analyzer view E and on the phone without client
work. The `report.json` `derived_summary` block, the `vehicle-server derive <id>|--all` command and
the `/rides` scalar table pick it up the same way.

## 2. The reference rules (Claude's reading of D-079; provisional, document in the README)

### 2.1 Timeline and inputs

- One session = one ride (D-075/D-087). Evaluate on the merged, sorted sample times of the
  window's inputs (condition and `stable` inputs). At each time every input has its latest valid
  sample if that sample is not older than the input's `stale_after_ms` (the same rule as the
  engine), else it is **unknown**. A condition with an unknown input is **not met**.
- `derived.<name>` inputs (W4 `derived.gear_estimate`) come from the class-A series the engine
  already computed (`derived.parquet` / the in-memory evaluation the summaries use).

### 2.2 Instances

- **`condition`:** an instance opens at the first time all `conditions` hold and closes at the
  first time one fails, a `stable` spread (max - min of that input since the open) exceeds its
  `max_spread`, or `max_duration_ms` is reached. Duration = close time - open time.
- **`key_on`:** at most one instance per ride: it opens at the first sample of the session only if
  the `conditions` hold there (W1: engine speed valid and 0); otherwise the ride has no key-on
  instance. It closes like `condition`.
- **`engine_start`:** opens when `did.ENGINE_SPEED` goes from a valid 0 to a valid value > 0
  (D-069 item 3; both samples valid and consecutive valid samples of that DID); closes when engine
  speed is a valid 0 again, at `max_duration_ms`, or when it becomes unknown.
- **`engine_stop`:** opens when `did.ENGINE_SPEED` goes from a valid value > 0 to a valid 0; then
  it holds while the `conditions` hold, and closes like `condition`.
- An instance **qualifies** when its duration ≥ `min_duration_ms`. An instance closed by
  `max_duration_ms` qualifies too.
- **Re-arm:** after any close, a new `condition` instance can open only after the conditions were
  not met at least once (no back-to-back instances during one long idle). `engine_start` /
  `engine_stop` re-arm on their next transition. The session end closes an open instance (it
  qualifies if long enough).
- Per window the reference keeps the **first qualifying instance** and the **count** of qualifying
  instances (`<window>_count` signals: 0 when none, a computed value, not null).

### 2.3 Signal values (over the first qualifying instance; valid samples inside it)

| Signal | Value |
|---|---|
| `window_key_on_rest_voltage` | mean of `did.BATTERY_VOLTAGE` |
| `window_key_on_sensor_spread` | per input the mean; value = largest mean - smallest mean of the three temperatures |
| `window_key_on_map_baro_delta` | mean `did.INTAKE_MAP` - mean `did.BAROMETRIC_PRESSURE` |
| `window_key_on_warm_restart` | 1 if abs(mean coolant - mean ambient) > `const.window_cold_soak_max_delta_degc`, else 0 |
| `window_warm_idle_rpm_spread` | max - min of `did.ENGINE_SPEED` |
| `window_warm_idle_rpm_drift` | mean engine speed of the second half (by time) - mean of the first half |
| `window_warm_idle_map_spread` | max - min of `did.INTAKE_MAP` |
| `window_warm_idle_stft_mean` | mean of `did.SHORT_TERM_FUEL_TRIM_B1` |
| `window_warm_idle_stft_std` | sample standard deviation (n - 1) of the same; fewer than 2 samples = null + flag |
| `window_post_stop_coolant_start` / `_end` | first / last valid `did.COOLANT_TEMP` in the instance |
| `window_post_stop_coolant_tau` | Newton cooling: least-squares fit of ln(T - T_amb) over time (T = coolant, T_amb = mean ambient in the instance), tau = -1 / slope in s; null + flag when fewer than 3 points have T - T_amb > 0 or the slope is ≥ 0 |
| `*_count` (W1-W5) | number of qualifying instances |

- A signal whose window had no qualifying instance, or whose own inputs have no valid sample in
  it: `value` null with a flag. Reuse an existing flag name where it fits (`no_data`), add at most
  two new constants (e.g. `no_window`, `too_few_samples`) next to the D-103 ones.
- The result passes through the existing range check (`_checked`): out of range = null +
  `out_of_range`, never clamped.
- **Not computed in this run** (keep `not_implemented`, but with a specific reason instead of
  `_WINDOW_REASON`, and list them in *For Claude*):
  - `window_cruise_final_drive_residual`: its declared inputs have no `const.gear_ratio_<n>`, so
    the measured final drive cannot be separated from the gearbox ratio (compare
    `ride_final_drive_ratio` in `d103_summaries.py`, which declares them) → defs question.
  - `window_cruise_ve_residual`: defs has no "expected VE at that gear and speed" model.
  The W4 state machine and `window_cruise_count` **are** computed.

## LR17-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-05-opencode-long-run-17.md` on
`ext/opencode-long-run-17-log`, `review: pending`, fill the header and the task list, commit and
push before any code. Update it after every later task.

## LR17-1 — State machine (`derived/health_windows.py`)

1. A pure module: input = the window spec from `vehicle_derived.WINDOWS[key]`, per-input sample
   series (time ms, value, valid) and per-input `stale_after_ms`; output = the list of instances
   (open ms, close ms, close reason, qualifies) with the first qualifying one and the count.
   Frozen dataclasses, type hints, docstrings in the style of `summary.py`.
2. Unit tests (`tests/test_health_windows.py`), synthetic: each `opens_on` kind; a condition that
   flickers (re-arm); `stable` spread breaking an instance; `max_duration_ms` close and re-arm;
   a stale input = not met; session end closing an open instance; an instance just below and just
   at `min_duration_ms`; `engine_start` needing two valid consecutive samples; patching a
   `WINDOWS` threshold changes the result (rule 1).

## LR17-2 — Window signals (`derived/health_window_summaries.py`)

1. Register the ready window signals with the existing `@_summary` mechanism (table in 2.3);
   remove them from the `_WINDOW_REASON` set; the two cruise residuals get their specific
   `not_implemented` reasons. Import the module where `d103_summaries` is imported so they
   register.
2. `golden_b.classify()`: the explicit health-window skip reason (rule 2); extend
   `test_golden_b.py` so a window signal is never selected.
3. Tests (`tests/test_health_window_summaries.py`): every computed signal on a synthetic ride
   (known values, including tau on an exact exponential), the no-instance flag, the out-of-range
   path, the cold-soak constant patch, and a check that every `window:` signal of defs is either
   computed here or `not_implemented` with a reason other than `_WINDOW_REASON`.

## LR17-3 — End to end

1. A synthetic session through the real ingest (use the fixture builders in
   `tests/make_fixtures.py` / `tests/derived_helpers.py`, no real data) that reaches W1, W3 and W5:
   `report.json` `derived_summary` and `GET /sessions/{id}/summary` show the window scalars as
   `kind: "scalar"`; `GET /rides` lists them like the other class-B scalars.
2. `vehicle-server derive <id>` recomputes them (existing command, no change expected).

## LR17-4 — Docs

`vehicle-server/README.md`: a short "D-079 health windows" subsection under the derived signals:
the rules of section 2 marked **provisional (Claude's reading of D-079, LR17)**, which signals are
computed, which stay `not_implemented` and why, and that the golden vectors exclude them until
rt-core implements the windows. Do **not** edit `CLAUDE.md` (red); put the one-line CLAUDE.md
update you would make into *For Claude*.

## LR17-5 — Checks and PR

`uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the golden reproduction
of rule 2 (`uv run vehicle-server golden --out <tmp dir>` + compare against
`tests/golden/MANIFEST.sha256`, or the existing test that does it), the zone check, then open
**one** PR from `ext/opencode-server-health-windows` to `main`; do not merge it. `uv.lock` must
not change.

## LR17-6 — Close the log

Finish the log: every task, commit, check result (test counts), the zone result, the PR link,
every doubt (*Unsure about*) and every request (*For Claude*: at least the two cruise residuals
and the CLAUDE.md line). Keep `review: pending`. Push the branch; no PR needed.
