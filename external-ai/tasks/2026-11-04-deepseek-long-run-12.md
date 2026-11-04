# DeepSeek long run 12 — 2026-11-04 (bring-up gate check: B0 / V0 / V1 verdict from a session)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR12-1..LR12-4 | vehicle-server | `ext/opencode-server-bringup` | green (yellow: `*gps*`, `*position*`, `*mdf4*`, `pyproject.toml`; red: `*ota*`, `external/*`, `.github/*`: do not touch them) |
| LR12-5 | vehicle-analyzer | `ext/opencode-analyzer-bringup` | green (red: `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`; yellow: `src/defs/*`, `package.json`: do not touch them) |
| LR12-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-12-log` | green |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

The first sessions on the real Honda CL250 are close (gate G1 in `STATUS.md`). The bring-up
sequence in vehicle-defs `docs/hardware-integration.md` §6 has gates **B0** (desk), **V0** (bike,
ignition on, engine off) and **V1** (engine idling, closed area), each with a "Pass when" column,
and §7.2 says what to read in `tester_stats`. Today the user has to read `report.json` by hand
and compare it with that table. This run makes vehicle-server answer the question directly:
"does this session pass gate V0?", with one line per criterion, and shows the same answer in
vehicle-analyzer's recorded-session view. It only reads stored data: no new ingest field from
the phone, no transmission of any kind.

No decision is needed from the user. If something here contradicts a decision (vehicle-defs
`docs/DECISIONS.md`: D-033, D-045, D-053, D-058, D-076) or a repo's `CLAUDE.md`, the decision text
wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-server/` and `vehicle-analyzer/` (not under
  `.claude/worktrees/`, that is Claude's area).
- For each repo: `git -C <repo> checkout main && git -C <repo> pull`, then
  `git -C <repo> checkout -b <branch from the table>`. Right after creating each branch, and again
  at the end, run from the workspace root: `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format, the check table
  (§4). Before each push run `python3 scripts/check_zones.py <repo> --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-server `CLAUDE.md` and `README.md`; vehicle-analyzer `CLAUDE.md` and `docs/ROADMAP.md`.
- The criteria, **the only source for this run**: vehicle-defs `docs/hardware-integration.md`
  §6 (table rows B0, V0, V1), §7 (the measurement table) and §7.2 (tester statistics). Read only
  those sections. Do not edit vehicle-defs (it is red, its docs are yellow).
- vehicle-server code: `src/vehicle_server/report.py` (how `can_health`, `tester_stats`, `imu`,
  `range_checks`, `status` are built), `src/vehicle_server/cli.py` (subcommands),
  `src/vehicle_server/api.py` (auth and the `/sessions/{id}/...` routes), `index.py`,
  `parquet.py`, and in the defs submodule `external/vehicle-defs/gen/python/vehicle_defs/`
  `vehicle_cl250.py` (`CLIENT_STEP_MAX_MS`, `ASSUMED_ROUND_TRIP_MS`, the polled DIDs) and
  `ble.py` (the CAN health flags, e.g. `ecuPresent`). Tests: `tests/conftest.py`,
  `tests/make_fixtures.py`, `tests/test_report.py`, `tests/test_cli.py`, `tests/test_api.py`.
- vehicle-analyzer code: the Recorded sessions view (key **E**: list, report summary, ride summary
  card) and the client it uses for `GET /sessions/{id}/report` and `/summary`.

### Hard rules for this run

1. **Read-only.** The check reads `report.json`, the index and the decoded Parquet of a stored
   session. It never re-ingests, never rewrites `report.json` of an existing session (exception:
   LR12-1 adds one field to *new* reports, see there) and never talks to a device.
2. **No invented numbers (invariant 2).** Every threshold comes from `vehicle_defs` (for example
   `CLIENT_STEP_MAX_MS`, `ASSUMED_ROUND_TRIP_MS`, the polled DID list, enum names of the bus
   state) or is quoted from `hardware-integration.md` §6 with the section in a comment (the only
   such numbers are "≥ 5 min" for V1 and "IMU gap count 0" for B0). Where the doc gives no number
   (V1 "RPM changes with a throttle blip", B0 "at rest"), the check is **manual**: it shows the
   measured values and says what the user must look at; it never decides with a threshold you
   chose.
3. **No position, ever (D-076).** The check does not read `gps.parquet` and does not touch any
   file whose name contains `gps` or `position` (yellow). GPS bring-up (§7.3) is out of scope.
4. **No real data in git (D-033).** Test sessions are synthetic, built with the existing fixture
   helpers. Never commit a session from `VEHICLE_DATA_DIR` or the user's desk.
5. **No new dependency** in either repo.

## LR12-1 — Report: ECU presence

`hardware-integration.md` §6 V0 needs "ECU present", but the `can_health` block of `report.json`
does not aggregate the `ecuPresent` flag today (check this first; if it already does, skip to
LR12-2 and say so in the log).

1. In `report.py`, add to the `can_health` block, next to `latched_foreign_tester` /
   `latched_bus_off`: `ecu_present_rows` (rows with the flag set), `ecu_absent_rows` (v3 CAN health
   rows with the flag clear) and `ecu_present_last` (the flag of the last row, or `null`). Use the
   flag name from the defs BLE schema exactly as `report.py` reads the other flags.
2. Add it to the text summary line of `can_health` (`?format=text` / `vehicle-server report`).
3. Old reports without these keys must keep working everywhere (the check of LR12-2 treats a
   missing key as **unknown**, never as a pass).
4. Tests in `tests/test_report.py`: present on all rows, absent on all rows, present then absent,
   no CAN health rows (v2 telemetry → keys absent or `null`, document which).

## LR12-2 — The check (pure module)

New `src/vehicle_server/bringup.py`, pure functions only (input: the report dict and, where
needed, small arrays read by the caller; no I/O inside the check functions).

1. `check_gate(gate: str, report: dict, extra: BringupInputs) -> BringupResult` for
   `gate` in `B0`, `V0`, `V1` (case-insensitive input, upper-case in the output; anything else →
   `ValueError`).
2. Each criterion is one `Check`: `id` (stable snake_case), `status` in
   `pass | fail | warn | manual | unknown`, `measured` (JSON-serialisable), `expected` (plain
   text), `source` (the doc section or the defs constant name, e.g.
   `"hardware-integration.md §6 V0"`, `"vehicle_cl250.CLIENT_STEP_MAX_MS"`), `note` (one plain
   sentence).
3. The criteria (map each to the report fields you found; if a field does not exist, the check is
   `unknown` with the reason, never `pass`):
   - **B0:** report `status` is `ok` (`warn` → `warn`, `fail` → `fail`); IMU gap count 0
     (the report's IMU loss/gap fields; no IMU in the session → `unknown`); "at rest" → `manual`
     with the IMU gap numbers shown.
   - **V0:** ECU present (LR12-1: `pass` when every CAN health row has it, `fail` when any row is
     absent, `unknown` for an old report); all polled DIDs valid (the polled DID list from
     `vehicle_defs`, **not** a hand-written list or the number 5: each needs at least one valid
     sample in `range_checks` and no out-of-range sample; show `valid_percent` per DID); no latch
     flags (`latched_foreign_tester` and `latched_bus_off` false); no bus-off
     (`max_bus_off_count` == 0, and no bus-off state in `bus_states_seen` by its defs enum name).
   - **V1:** the V0 CAN-health checks again (latch, bus-off, ECU present) for the whole session;
     session length ≥ 5 min (§6 "CAN health clean for ≥ 5 min"; take the duration from what the
     report or the telemetry Parquet already gives, explain which in a comment); RPM changes with a
     throttle blip → `manual`, `measured` = min / p50 / max of the engine-speed DID over the session
     (name it by its defs name; read it through the existing `/stats` code path if one fits rather
     than a new reader).
   - **V0 and V1, §7.2 tester statistics (status `warn` at most, never `fail`):**
     `step_gap_over_count` > 0 → `warn` ("the D-053 10 ms step assumption does not hold for conn
     in this session"; the 10 comes from `CLIENT_STEP_MAX_MS`); any DID with `rtt` `max_ms` >
     `ASSUMED_ROUND_TRIP_MS` → `warn` with the DIDs listed; no v4 tester data → `unknown`.
4. `BringupResult`: `session_id`, `gate`, `verdict` = `fail` if any check is `fail`, else
   `incomplete` if any is `unknown`, else `pass`; plus `needs_you` (the `manual` checks) and
   `warnings` (the `warn` checks), and `checks` in a fixed order. A `manual` check never changes
   the verdict; the output says the verdict is "pass, pending N manual check(s)" in the text form.
5. `format_text(result) -> str`: one line per check (`PASS`/`FAIL`/`WARN`/`MANUAL`/`UNKNOWN`,
   id, measured, expected), then the verdict line.
6. Tests `tests/test_bringup.py`: for each gate a clean session → `pass`; each criterion failing
   alone → `fail` (or `warn` for §7.2) with the right id; an old report without the LR12-1 keys →
   `incomplete`; no IMU / no v4 / no CAN health data → `unknown` with a reason; a manual check
   never changes the verdict; unknown gate → `ValueError`; the polled DID list really comes from
   defs (a test that patches the defs list and sees the check follow it).

## LR12-3 — CLI and API

1. CLI: `vehicle-server bringup <session_id> --gate B0|V0|V1 [--json]` → the text form by
   default, the JSON form with `--json`; exit code 0 for `pass`, 1 for `fail`, 2 for
   `incomplete`, and the usual error exit for an unknown session. Tests in `tests/test_cli.py`.
2. API: `GET /sessions/{id}/bringup?gate=V0` with the same bearer-token auth as `/report`;
   `404` unknown session, `422` missing or unknown gate, `200` with the JSON result otherwise.
   It must not be reachable without the token. Tests in `tests/test_api.py` (auth, 404, 422, 200
   for each gate on a synthetic session).
3. The JSON shape is the same in the CLI and the API (one serialiser).

## LR12-4 — Server docs

1. `README.md`: a short *Bring-up gate check* section: what B0/V0/V1 are (one line each, pointing
   to `vehicle-defs/docs/hardware-integration.md` §6), the CLI and API, the exit codes, the
   statuses, and that `manual` checks are the user's to judge.
2. `CLAUDE.md` is red: do not edit it. Write in *For Claude* the one line Claude should add to its
   "v0 as built" list.
3. Do not edit `hardware-integration.md` (vehicle-defs). Write in *For Claude* where §6 / §7.2
   should mention the command.

Then run the server checks of `AGENTS.md` §4 (`uv run pytest`, `uv run ruff check .`,
`uv run ruff format --check .`), the zone check, and open **one** PR from
`ext/opencode-server-bringup` to `main`; do not merge it.

## LR12-5 — Analyzer: show the verdict in Recorded sessions (key E)

1. In the Recorded sessions view, next to the report summary of the selected session, add a
   **Bring-up check** card with a gate selector (B0 / V0 / V1, default V0) that calls
   `GET /sessions/{id}/bringup?gate=…` with the same server URL and token fields as the other
   session requests (token in the `Authorization` header only, never in a URL).
2. Render what the server returns, without re-computing anything: the verdict (pass / fail /
   incomplete, plus "N manual check(s) pending"), then one row per check (status, id, measured,
   expected, source). Colours follow the existing status colours of the analyzer; do not add a new
   palette.
3. A server without the endpoint (404 on the route, an older server) shows "this server has no
   bring-up check (needs vehicle-server with LR12)" instead of an error toast; a 422 shows the
   server's message.
4. Tests: a component test for pass, fail, incomplete with manual checks, the 404-old-server case
   and that the token goes in the header. If the Playwright smoke tests cover view E with a mocked
   server, add the bring-up route to that mock and one assertion; only the app and the configured
   server may be requested.
5. `docs/ROADMAP.md`: add the item (next free id) and mark it done with the PR link.
6. Run the analyzer checks of `AGENTS.md` §4 (at least `npm test`, `npm run build`; Playwright if
   you changed a view it covers), the zone check, and open **one** PR from
   `ext/opencode-analyzer-bringup` to `main` that says it needs the server PR; do not merge it.

## LR12-6 — Log

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-04-opencode-long-run-12.md` on
branch `ext/opencode-long-run-12-log` in the workspace, `review: pending`, with every task,
commit, check result, both zone results, every doubt (*Unsure about*: especially every report
field you mapped to a criterion and every criterion you marked `unknown`/`manual`) and every
request (*For Claude*). Push the branch; no PR needed.
