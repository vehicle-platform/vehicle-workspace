# DeepSeek long run 14 — 2026-11-05 (analyzer: Signal coverage view)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR14-0 (first!) and LR14-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-14-log` | green |
| LR14-1..LR14-5 | vehicle-analyzer | `ext/opencode-analyzer-coverage` | green; **yellow allowed only for `src/defs/model.ts`** (parsing more of the bundled defs, see LR14-1; the PR then says `needs-claude-review`); red: `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`; yellow `package.json`: do not touch |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

vehicle-defs defines about 300 discrete values for the CL250 platform: 40 polled ECU DIDs
(5 verified on the bike, 35 not yet), 47 OBD catalog candidates and 10 identification DIDs, 18
non-DID sensors (IMU, GPS, CAN health, tester statistics), and 155 derived signals (class A 66,
B 75, C 12, D 2). Some are computed today by vehicle-server and rt-core, many wait for a sensor,
a threshold decision or the bike. Nobody can see that picture in one place. This run adds a
**Signal coverage** view to vehicle-analyzer: every defs value in one table, what it waits for,
and, for a selected recorded session, whether that session has data for it. At gate G1 (first
bike connection) the user will watch this table to see which values "light up". It is also a
figure for the thesis.

**Every number in this view comes from the bundled defs or from the server's report.** The
counts above are context for you, never constants in the code: a test must prove the counts
follow the defs.

No decision is needed from the user. If something here contradicts a decision (vehicle-defs
`docs/DECISIONS.md`: D-033, D-066, D-068, D-070, D-078, D-081, D-085, D-087) or vehicle-analyzer
`CLAUDE.md`, the decision text wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-analyzer/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area; reading a file there is fine).
- `git -C vehicle-analyzer checkout main && git -C vehicle-analyzer pull`, then
  `git -C vehicle-analyzer checkout -b ext/opencode-analyzer-coverage`. In the workspace:
  `git checkout main && git pull && git checkout -b ext/opencode-long-run-14-log`. Right after
  creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format, the check table
  (§4). Before each push run `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`
  from the workspace root. **Red = stop and revert that path**; yellow is allowed only for
  `src/defs/model.ts`, anything else yellow = revert and write the request into the log.
- vehicle-analyzer `CLAUDE.md` (scope D-081, layer split D-085: no LLM, no fault matching, no
  plain-language diagnosis) and `docs/ROADMAP.md`.
- The defs sources **as bundled by the analyzer** (`src/defs/index.ts` imports them from the pinned
  submodule `external/vehicle-defs`, currently v0.20.0; do not change the pin):
  `uds/vehicle_cl250.yaml` (`dids`: `verified`, `poll_period_ms`, `obd_pid`, unit, range),
  `uds/obd_catalog.yaml` (`polled`, `groups`, `candidates`, `identification`),
  `derived/cl250_derived.yaml` (`sensors`: the `phase0` and `rt_core` sources, `null` = not
  available there; `signals`: `class`, `unit`, `inputs`, `pending_inputs`, `window`, `record`;
  `windows`; `ride_summary_records` if present at the pin). Read the header comments of each file
  for the meaning of the keys.
- vehicle-analyzer code: `src/defs/model.ts` (what `buildDefs` already parses: `catalog`,
  `catalogByDid`, `windows`, ...), `src/App.tsx` (views and their keys; the used keys are
  A C D E F G H L N O S T U X), `src/components/SessionPanel.tsx` and `src/services/sessionClient.ts`
  (the selected session, `getReport`, server URL and token handling), `src/services/exportService.ts`
  (CSV export), `src/components/RideHistoryPanel.tsx` (a recent table view to copy the style from).
- vehicle-server (read only, the contract of the per-session columns):
  `src/vehicle_server/report.py` (`range_checks` per DID with `valid_percent`, the vehicle-signal
  summary per DID, `imu`, `gps` summary flags, `can_health`, `tester_stats`) and
  `src/vehicle_server/derived/engine.py` + `derived/summary.py` (the `derived` and
  `derived_summary` blocks: per signal `status` in `ok | not_implemented | not_ready |
  missing_inputs | ...` with `reason`, `pending_inputs`, `missing`). Use the key names you find
  there; if a key you need does not exist, the cell says "not in report", never a guess.

### Hard rules for this run

1. **Defs-only catalog (invariant 2).** Every row comes from the bundled defs. No hand-written
   signal list, name, unit, DID or count anywhere in `src/` (tests may name a few defs names to
   assert they appear).
2. **Read-only.** The view reads the bundled defs and, optionally, `GET /sessions/{id}/report`
   through the existing session client. No new server route, no request to any other host, no
   CAN transmission, nothing over the USB adapter.
3. **No interpretation (D-085).** The "waiting for" column quotes defs (`pending_inputs` text,
   `verified: false`, candidate status) or the server (`reason`) verbatim or with a fixed short
   label per defs key; no diagnosis, no "probably", no score.
4. **No position (D-076).** Do not show GPS position fields; GPS sensors appear only as
   rows with presence (the server never sends a position in the report anyway).
5. **No new dependency** (`package.json` is yellow).
6. **No real data in git (D-033).** Test fixtures are synthetic.

## LR14-0 — Log first

Before any code: copy `external-ai/log/TEMPLATE.md` to
`external-ai/log/2026-11-05-opencode-long-run-14.md` on `ext/opencode-long-run-14-log`,
`review: pending`, fill the header and the task list, commit and push. Update it after every
later task (commit + push each time), so the log is never behind the code.

## LR14-1 — Coverage model (pure)

1. If `buildDefs` does not yet expose them, extend `src/defs/model.ts` (yellow, allowed) to parse
   the derived `sensors` (name, unit, description, `phase0`, `rt_core`) and `signals` (name,
   class, unit, description, inputs, `pending_inputs`, `window`, `record`) and the identification DIDs, with the
   same strict style as the existing parsers (a missing required key throws). Do not change any
   existing field or behaviour; existing tests must pass unchanged.
2. New pure module `src/services/coverage.ts`: `buildCoverage(defs) -> CoverageRow[]` with one row
   per value, `group` in `polled_did | catalog_candidate | identification | sensor | derived`,
   plus `name`, `id` (DID hex where there is one), `class` (derived only), `unit`, `description`,
   and a `defsStatus` object:
   - polled DID: `verified` (bool), `pollPeriodMs`;
   - candidate / identification: catalog only (`polled: false`);
   - sensor: its `phase0` and `rt_core` source text (`null` shown as "none");
   - derived: `pendingInputs` (list), `inputs`, `window`/`record` if present.
   **Do not compute `ready_phase0` / `ready_rt_core`:** they are not YAML keys; vehicle-defs
   codegen derives them (`tools/codegen/.../derived.py` `ready()`), and a second copy of that rule
   in TypeScript would drift. The analyzer shows the raw YAML facts only.
3. `waitingFor(row) -> string[]` (pure, fixed labels, defs only): polled DID not verified →
   "verification on the bike (G1, D-068)"; candidate → "catalog only, not polled (D-066)";
   identification → "catalog only"; derived with `pendingInputs` → each item verbatim; sensor with
   `phase0: null` → "no Phase 0 source (defs)". Nothing else (whether a derived signal is
   computed shows in the session column, from the server).
4. `applySession(rows, report) -> rows` (pure): adds a `session` cell per row from a report JSON:
   polled DID → `valid_percent` (or "no samples"); sensor → present / absent from the report's
   summary blocks (name the report key you used per sensor in a comment; unknown → "not in
   report"); derived class A → the `derived` block entry (`status`, `reason`); class B → the
   `derived_summary` entry. A missing block or entry → "not in report", never "ok".
5. `summarize(rows) -> counts per group and per status` for the header chips.
6. Tests `src/services/coverage.test.ts`: the number of rows per group equals the length of the
   matching defs list (computed from the parsed defs in the test, not typed); a few known names
   appear in the right group; `waitingFor` labels for each case; `applySession` with a synthetic
   report: ok, not_implemented with reason, not_ready, missing block → "not in report"; an
   unknown status string from the server is kept verbatim.

## LR14-2 — The view

1. New `src/components/CoveragePanel.tsx`, opened with the key **I** (check it is free) and listed
   in the header/help like the other views ("Signal coverage").
2. Top: the pinned defs ref (`DEFS.ref`), the selected session id (or "no session selected"), and
   one chip per group with its count and the main split (e.g. polled DIDs: verified / not
   verified; derived: per class, and per session status when a session is loaded).
3. Table: group, name, id, class, unit, defs status, waiting for, session. Sort by any column;
   filter by group, class, "waiting for" category and session status; a text search on name and
   description. Long text wraps; the table scrolls inside the panel, the page does not.
4. A **Load session** control uses the session already selected in Recorded sessions (key E) if
   there is one, else a session id field; it calls the existing `getReport` with the configured
   server URL and token (header only). Errors use the existing session-client messages.
5. Export the visible rows as CSV through the existing export service (same CSV conventions as the
   other exports).
6. Colours: the analyzer's existing status colours only; status is readable without colour.

## LR14-3 — Tests for the view

1. Component test: renders all groups from the bundled defs; filters and search narrow the rows;
   loading a mocked report fills the session column; a server error shows the client's message;
   CSV export contains the visible rows only.
2. If the Playwright smoke tests cover the header views, add the key **I** view with a mocked
   report route and one assertion; only the app and the configured server may be requested.

## LR14-4 — Docs

1. `docs/ROADMAP.md`: add the item (next free id, A13) and mark it done with the PR link.
2. README (if it lists the views and keys): add the view.
3. `CLAUDE.md` is red: write in *For Claude* the one line Claude should add.

## LR14-5 — Checks and PR

Run the analyzer checks of `AGENTS.md` §4 (at least `npm test`, `npm run build`, the lint/type
check the table lists, Playwright if you changed a covered view), the zone check, and open **one**
PR from `ext/opencode-analyzer-coverage` to `main`. Its body says `needs-claude-review` if
`src/defs/model.ts` changed. Do not merge it.

## LR14-6 — Close the log

Finish `external-ai/log/2026-11-05-opencode-long-run-14.md`: every task, commit, check result
(test counts), the zone result, the PR link, every doubt (*Unsure about*: especially each report
key you mapped to a sensor or a derived block, and any defs key whose meaning you were unsure of)
and every request (*For Claude*). Keep `review: pending`. Push the branch; no PR needed.
