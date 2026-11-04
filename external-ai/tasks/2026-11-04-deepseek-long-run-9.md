# DeepSeek long run 9 — 2026-11-04 (vehicle-mcp ride-summary tools, D-102)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR9-1..LR9-5 | vehicle-mcp | `ext/opencode-mcp-ride-summary` | yellow (whole repo: Claude reviews before the user merges) |
| LR9-6 | vehicle-workspace `external-ai/log/` | (your log) | green |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### User decision for this run (2026-11-04)

- **D-102** (vehicle-defs `docs/DECISIONS.md`, merged; run `git -C vehicle-defs pull` first and
  read the D-102 entry and D-092). Two changes are approved, nothing else:
  1. a new tool `get_ride_summary(session_id)` (tool 8);
  2. `query_ride_history(start_date, end_date)` keeps its signature and every current output
     field, and adds per listed session the class-B scalars from vehicle-server `GET /rides`.
- **Any other new tool, parameter or cross-ride aggregate is out of scope** (vehicle-mcp
  `CLAUDE.md`: adding a tool requires the user's approval). If you think one is needed, write it
  into *For Claude* and do not build it.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clone `vehicle-mcp/` (not under `.claude/worktrees/`, that is Claude's area).
- Right after `git checkout -b ext/opencode-mcp-ride-summary`, and again at the end, run from the
  workspace root: `python3 scripts/vscode_workspace.py` (if the script exists). It refreshes the
  VS Code folder list so the branch shows up with the 🐋 mark.
- Commit with the normal git config; the user's git config tags authors on `ext/opencode-*`
  branches automatically. Do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py vehicle-mcp --base origin/main` from the workspace root.
  **Red = stop**, write the request into the log.
- vehicle-mcp: `CLAUDE.md` (tool list, rules 1-6), `README.md` (tool table),
  `src/vehicle_mcp/source.py` (`HistorySource`, `SourceError`, `StatsRouteUnavailable`),
  `client.py` (`VehicleServerClient`, how `stats()` detects a server without `/stats` and raises
  `StatsRouteUnavailable`; `_session_path`; the token never leaks), `tools.py` (`VehicleTools`,
  `_call`, `_parse_bound`, `is_position_name`, `query_ride_history`, the `/stats` fallback in
  `compute_signal_stats`), `server.py` (tool registration, `INSTRUCTIONS`), `tests/support.py`
  (`FakeVehicleServer`), `tests/test_tools.py`, `tests/test_source.py`, `tests/test_server.py`.
- vehicle-server (read only, the contract you consume): `CLAUDE.md` "Read API",
  `src/vehicle_server/api.py` routes `GET /sessions/{id}/summary` and `GET /rides` (query
  parameters, status codes), `src/vehicle_server/ride_summary.py` (`build_ride_summary`,
  `load_ride_summary`, `NoRideSummary`, `build_rides`, `parse_utc_bound`, `created_in_range`,
  `select_scalar_names`, `BadRideQuery`), and its tests `tests/test_ride_summary.py` /
  `tests/test_api.py` for real response shapes (the two 404s differ only by `detail`:
  `unknown session: <id>` vs the `NoRideSummary` text). Copy shapes into your fakes from these tests,
  do not invent fields.

### Hard limits of this run

- **Read-only:** GET only (an existing test proves the HTTP source issues GET only; extend it to
  the new routes).
- **Invariant 7 (the LLM does no math):** the tool returns the server's stored values as they
  are. No recomputing, rebinning, unit conversion, rounding, ranking, totals or means of the
  summary values. The only existing aggregate stays `mean_loss_percent` in `query_ride_history`.
- **Invariant 2 / rule 4:** signal names, units and bin edges come from the server response,
  never as literals in `src/`. Test fixtures may use synthetic names.
- **Position (D-076, rule 3):** apply `is_position_name` to every name a new path returns, the
  same way the existing tools do; a position-looking name is dropped and counted, never shown.
- No new runtime dependency, no `pyproject.toml` version bump, no tag, no `CLAUDE.md`, no
  `.github/`, no edit in any other repo. Synthetic data only (D-033).

## LR9-1 — Source: two read-only methods

1. `HistorySource`: add `ride_summary(session_id) -> Any` (the `GET /sessions/{id}/summary`
   shape) and `rides(*, start: str | None, end: str | None, signals: list[str] | None) -> Any`
   (the `GET /rides` shape). Docstrings name the shape like the existing methods.
2. `source.py`: add `RidesRouteUnavailable(SourceError)` next to `StatsRouteUnavailable`.
3. `VehicleServerClient`: implement both with `_get`; map the server's "no summary stored" 404
   to a `SourceError` subclass or message the tool can tell apart from "unknown session" (read
   the server code to see how the two 404s differ; if they cannot be told apart, say so in the
   log). Detect a server without `/rides` the same way `stats()` detects a missing `/stats` and
   raise `RidesRouteUnavailable`.
4. Tests in `tests/test_source.py`: paths, query parameters, GET only, both 404 cases, the
   missing-route case, the token never appears in an error text.

## LR9-2 — Tool: `get_ride_summary(session_id)`

1. `VehicleTools.get_ride_summary`: return the server's summary for one session with its
   scalars (name, value, unit, status, flag) and binned signals (axes, cells) as served. Keep
   `defs_mismatch` and add a short `warnings` entry when it is true ("stored bin edges differ
   from the current defs; values are as stored"). No summary stored → `ToolError` naming the
   reason. Position-looking names: dropped and counted as in the other tools.
2. Docstring (the LLM reads it): what a class-B ride summary is (one session = one ride), that
   values are computed by vehicle-server from vehicle-defs definitions, that null values carry a
   status/flag reason, and that the tool never computes anything.
3. Register it in `server.py`; mention it in `INSTRUCTIONS` if that text lists the tools.
4. Tests in `tests/test_tools.py`: a computed summary, a null value with its status, a binned
   signal, `defs_mismatch`, no summary stored, unknown session, a position-looking name.

## LR9-3 — Tool: `query_ride_history` gets the ride scalars

1. After the current logic, call `rides(start=..., end=...)` with the **same bounds the user
   gave** and join rows by `session_id`. Each listed session gains a `ride` object (`values`,
   `flags` and the `columns` units from the response); a dated session the server skipped (no
   stored summary) gets `ride: null` with a reason; undated sessions stay as today. Add the
   server's `skipped` count to the output.
2. `RidesRouteUnavailable` → the output is exactly today's output plus a top-level
   `ride_scalars: "unavailable"` reason (mirror the `/stats` fallback wording). Any other source
   error on `/rides` → the same fallback with the error text, never a failed tool call, since the
   session part is still valid.
3. Check that vehicle-mcp `_parse_bound` and vehicle-server `parse_utc_bound` give the same range
   for a date-only bound, a timestamp without offset and one with an offset. Add a test with all
   three. If they differ, do **not** change the server; write it into *For Claude*.
4. Every current `query_ride_history` test must pass unchanged; add tests for the join, a
   skipped session, an undated session, the missing route and a `/rides` error.

## LR9-4 — Docs inside the repo

1. `README.md`: the tool table gets `get_ride_summary` and the extended `query_ride_history`
   output, the dependency list gets `/sessions/{id}/summary` and `/rides`, with the minimum
   vehicle-server version that has them (find it from the server git history: server#46).
2. Do not edit `CLAUDE.md` (red); Claude already updated its tool list for D-102.

## LR9-5 — Checks

1. `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` all green.
2. A smoke run: `VEHICLE_API_TOKEN=x uv run python -c "from vehicle_mcp.server import build_server; ..."`
   (or the existing server test) proves 8 tools are registered.
3. `python3 scripts/check_zones.py vehicle-mcp --base origin/main` from the workspace root:
   expect yellow only.

## LR9-6 — Log and wrap-up

1. Your log `external-ai/log/2026-11-04-opencode-long-run-9.md` (copy of `TEMPLATE.md`,
   `review: pending`): per task the branch, files, checks with their result, the zone check
   result, the LR9-1 404 finding and the LR9-3 bound comparison.
2. *For Claude*: anything you wanted to add but D-102 does not allow, every open doubt.
3. Push the branch. Open **one** PR `vehicle-platform/vehicle-mcp` from
   `ext/opencode-mcp-ride-summary` to `main` with the body starting `needs-claude-review` (yellow
   zone) and do not merge it.
4. Run `python3 scripts/vscode_workspace.py` once more from the workspace root.
