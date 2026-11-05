# DeepSeek long run 18 — 2026-11-05 (D-079 window instances: server report block + analyzer card)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR18-0 (first!) and LR18-7 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-18-log` | green |
| LR18-1 ... LR18-3 | vehicle-server | `ext/opencode-server-window-instances` | green (yellow: any path with `gps`, `position`, `mdf4` in it, `pyproject.toml`, `uv.lock`; red: `*ota*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`: do not touch) |
| LR18-4 ... LR18-6 | vehicle-analyzer | `ext/opencode-analyzer-health-windows` | green (yellow: `src/defs/*`, `package.json`, `package-lock.json`; red: `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`: do not touch) |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

Long run 17 (server#53, reviewed in server#54) added the D-079 health-window state machine to the
vehicle-server reference: `src/vehicle_server/derived/health_windows.py` finds the window
instances, `health_window_summaries.py` turns the first qualifying one into 17 class-B scalars.
The rules are **provisional** (Claude's reading of D-079, README "D-079 health windows"). On the
first real rides (G1) the user must be able to **see where each window opened and closed** to
check those rules, but today only the scalars are stored; the instances are thrown away. This run
stores the instances in the report and shows them in vehicle-analyzer view E. Nothing is
re-computed in the analyzer.

No decision is needed from the user. If something here contradicts a decision (D-033, D-070,
D-076, D-079, D-081, D-085, D-087) or a repo `CLAUDE.md`, the decision text wins: write the
conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-server/`, `vehicle-analyzer/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area).
- For each repo: `git -C <repo> checkout main && git -C <repo> pull && git -C <repo> submodule
  update --init`, then `git -C <repo> checkout -b <branch from the table>`. In the workspace:
  `git checkout main && git pull && git checkout -b ext/opencode-long-run-18-log`. Right after
  creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root (zones, branches, trailer, log format, the check table §4).
  Before each push run `python3 scripts/check_zones.py <repo> --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-defs `docs/DECISIONS.md` D-079 (one entry) only. Do not read the large docs.
- vehicle-server: `CLAUDE.md`, README section "D-079 health windows (provisional)",
  `derived/health_windows.py` (`WindowResult`, `WindowInstance`, the `CLOSE_*` reasons),
  `derived/summary.py` (`SummaryEvaluation`, `evaluate`, `_window_results`), the code that builds
  the `derived_summary` report block (follow `derived.store_all`, called from `ingest.py` and
  `rederive_session`), `series.py` (`t0_of` and how the `/series` route loads a session's
  series), `report.py` around the `derived_summary` text rendering, and the tests
  `test_health_windows_ingest.py`, `test_health_window_summaries.py`.
- vehicle-analyzer: `CLAUDE.md`, `docs/ROADMAP.md`, `src/defs/model.ts` (`HealthWindowDef`,
  `DerivedSignalDef.window`; **read only, do not edit**), `src/components/RideSummary.tsx` and the
  code that loads `GET /sessions/{id}/report` and `/summary` for view E, `src/services/coverage.ts`
  (how a report block is parsed defensively), `ui-tests/ride-summary.spec.ts` (how the server is
  mocked in Playwright).

### Hard rules for this run

1. **The server stores what the state machine already found; the analyzer renders what the
   server stored.** No window rule, threshold or duration is re-implemented or changed. Window
   keys, descriptions, conditions and durations in the analyzer come from the bundled defs
   (`defs.windows`), signal names / units from the response and `defs.derivedSignals`.
2. **Golden vectors and the class-B values unchanged.** `uv run pytest tests/test_golden.py
   tests/test_golden_b.py` passes and every existing value in `derived_summary.parquet` and in
   the `derived_summary` block stays byte-identical; only a new `health_windows` key is added.
3. **No new route, no new dependency, no change to `/summary`, `/rides` or `/series` code.** The
   block reaches the analyzer through the existing `GET /sessions/{id}/report`.
4. **Never a position, never real data.** Window inputs have no GPS; tests use synthetic series
   only (D-033).
5. **Analyzer: listen-only and defs-only rules unchanged.** No edit under `src/defs/`, no new npm
   package. A missing block (older server or a session not re-derived) is a plain message, never
   an error.

## LR18-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-05-opencode-long-run-18.md` on
`ext/opencode-long-run-18-log`, `review: pending`, fill the header and the task list, commit and
push before any code. Update it after every later task.

## LR18-1 — Server: keep the window results

1. `SummaryEvaluation` gains the precomputed window results of `evaluate` (a mapping window key ->
   `WindowResult`), filled from the existing `_window_results` call; nothing else in `evaluate`
   changes.
2. Test (extend `tests/test_health_window_summaries.py` or a new `tests/test_health_window_block.py`):
   on the existing synthetic ride the returned results hold the instances the scalars were taken
   from (the first qualifying W3 instance matches the one `window_warm_idle_rpm_spread` used).

## LR18-2 — Server: `health_windows` in the `derived_summary` report block

1. The code that builds the `derived_summary` block adds one key (all times integers, ms):

   ```json
   "health_windows": {
     "rule": "provisional: Claude's reading of D-079 (vehicle-server README)",
     "t0_device_ms": 1234567,
     "windows": {
       "W3_WARM_IDLE": {
         "qualifying_count": 1,
         "instances": [
           {"start_ms": 3000, "end_ms": 30000, "duration_ms": 27000,
            "close_reason": "condition", "qualifies": true, "first_qualifying": true}
         ]
       }
     }
   }
   ```

   - `t0_device_ms` is **the same t0 as `GET /sessions/{id}/series`** for that session: reuse
     `series.t0_of` with the loader the `/series` route uses; do not copy the rule. `start_ms` /
     `end_ms` = instance open / close minus that t0.
   - One entry per evaluated window, keys in `vehicle_derived.WINDOWS` order; every instance (also
     the non-qualifying ones), in time order; `close_reason` is the `CLOSE_*` string as is;
     exactly the instance equal to `first_qualifying` has `first_qualifying: true`.
   - When the summary evaluation fails (`derived_summary.error`) the key is absent.
2. Both ingest and `vehicle-server derive <id>` write it (they share the block builder; check).
3. `report.py` text format (`GET /sessions/{id}/report?format=text`): one line per window under the
   derived-summary part, e.g. `W3_WARM_IDLE: 2 instances, 1 qualifying (first 3.0-30.0 s)`.
4. Tests: extend `tests/test_health_windows_ingest.py`: the block exists after ingest and after
   `derive`, `t0_device_ms` equals the `/series` response `t0_device_ms` of the same session, the
   W1/W3/W5 instances match the synthetic ride, the text format line; and a check that the other
   `derived_summary` keys are unchanged (rule 2).

## LR18-3 — Server: README, checks, PR

1. README: in "D-079 health windows (provisional)" one short paragraph on the `health_windows`
   block (fields, t0 = `/series` t0, every instance kept). Do **not** edit `CLAUDE.md` (red); put
   the one-line update you would make into *For Claude*.
2. `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the golden tests of rule
   2, the zone check; `uv.lock` unchanged. Open **one** PR from
   `ext/opencode-server-window-instances` to `main`; do not merge it.

## LR18-4 — Analyzer: parse the block

1. New `src/services/healthWindows.ts`: a pure parser of `report.derived_summary.health_windows`
   (in the defensive style of `coverage.ts`): returns `{ rule, t0DeviceMs, windows: [...] }` or a
   reason string (`"not in report"` when the key or the `derived_summary` block is missing,
   `"malformed: <what>"` otherwise). An instance with `end_ms < start_ms`, a non-integer time or an
   unknown field type is rejected with the reason, never guessed. Window keys not in the bundled
   `defs.windows` are kept and marked `unknownInDefs: true` (defs mismatch), not dropped.
2. Vitest unit tests: valid block, missing block, malformed instance, unknown window key, order kept.

## LR18-5 — Analyzer: Health windows card in view E

1. A **Health windows** card in Recorded sessions (E), below the ride summary card, for the
   selected session (from the report view E already loads; no new request if the report is
   already fetched):
   - header with the `rule` text as a "provisional" badge;
   - a timeline strip (plain SVG, no new package): one row per window of `defs.windows`, the
     session span on the x axis (0 to the session's last sample on the same t0, from data E
     already has; if it has none, the last instance end), each instance a band, qualifying bands
     filled, others outlined, the first qualifying one marked; hovering a band shows start, end,
     duration and close reason;
   - per window (in defs order): key, defs `description`, `opensOn`, min / max duration, the
     conditions and `stable` bands rendered verbatim from defs (`did.COOLANT_TEMP gt 80`), the
     instance table (start s, end s, duration s, close reason, qualifies), and the window's
     computed signals from the session's `/summary` response (signals whose
     `defs.derivedSignals[].window` is that key; value, unit, flag as the response gives them);
   - a window in defs with no entry in the block: "not evaluated"; `unknownInDefs` windows in a
     separate "not in the bundled defs" list; the block missing: "No window instances in this
     report (older server, or run `vehicle-server derive <id>`)."
2. Component tests (the existing component test setup): rendering of all three states, band
   count = instance count, first-qualifying marking, the "not evaluated" row.

## LR18-6 — Analyzer: Playwright, ROADMAP, checks, PR

1. Extend `ui-tests/ride-summary.spec.ts` (or a new `ui-tests/health-windows.spec.ts` in the same
   mocking style): a mocked report with the block shows the card and its bands; only the app and
   the configured server are requested.
2. `docs/ROADMAP.md`: row **A15** "Health windows (D-079 instances)" with what was built, needs
   vehicle-server LR18, status done (long run 18) + the PR number.
3. `npm test`, `npm run build`, the Playwright suite as in `AGENTS.md` §4, the zone check
   (`src/defs/*` untouched, no `package.json` change). Open **one** PR from
   `ext/opencode-analyzer-health-windows` to `main`; do not merge it. In the PR body: "needs
   vehicle-server PR <n> (the report block); merge the server PR first".

## LR18-7 — Close the log

Finish the log: every task, commit, check result (test counts), the zone results, both PR links,
every doubt (*Unsure about*) and every request (*For Claude*: at least the server `CLAUDE.md`
line and any rule-2 surprise). Keep `review: pending`. Push the branch; no PR needed.
