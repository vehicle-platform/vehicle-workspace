---
date: 2026-11-04
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-9
repos: [vehicle-mcp, vehicle-workspace]
branches: [vehicle-mcp:ext/opencode-mcp-ride-summary, vehicle-workspace:ext/opencode-long-run-9-log]
prs: [vehicle-mcp#16]
zone: yellow
review: pending
---

# DeepSeek long run 9 — vehicle-mcp ride-summary tools (D-102)

## Goal
Implement D-102 in vehicle-mcp: `get_ride_summary(session_id)` and class-B ride
scalars in `query_ride_history`, read-only and without recomputing any value.

## Changes

### LR9-1 — source methods (67e6e3a)
- `vehicle-mcp/src/vehicle_mcp/source.py`: added `HistorySource.ride_summary()`
  and `.rides()`, plus `RidesRouteUnavailable(SourceError)` and
  `NoRideSummary(SourceError)`.
- `vehicle-mcp/src/vehicle_mcp/client.py`: added GET
  `/sessions/{id}/summary` and GET `/rides` (`from`, `to`, `names`). The two
  404s differ by detail: `unknown session: <id>` is a server error, other
  non-default detail text is `NoRideSummary`. A default `Not Found` 404 on
  `/rides` is `RidesRouteUnavailable`, matching `stats()`. The token is scrubbed
  from all mapped error text.
- `vehicle-mcp/tests/support.py`: fake `/summary` and `/rides` payloads,
  `supports_rides`, `rides_error`, `summaries`, `rides_payload`.
- `vehicle-mcp/tests/test_source.py`: route paths, query parameters, GET-only,
  both 404 cases, missing `/rides`, and token-free error tests.

### LR9-2 — get_ride_summary (2a6b521)
- `vehicle-mcp/src/vehicle_mcp/tools.py`: added `get_ride_summary`; returns the
  server's scalars and binned axes/cells unchanged, passes `defs_mismatch`
  through and adds a warning, drops position-looking names into
  `dropped_position_names`, and reports no stored summary separately.
- `vehicle-mcp/src/vehicle_mcp/server.py`: registered tool 8.
  `INSTRUCTIONS` does not list individual tools, so it was left unchanged.
- `vehicle-mcp/tests/test_tools.py`: computed scalar, null status, binned
  cells, `defs_mismatch`, no summary, unknown session, position name.
- `vehicle-mcp/tests/test_server.py`: eight registered tools and an MCP smoke
  call for `get_ride_summary`.

### LR9-3 — ride scalars in history (eb8a7a8)
- `vehicle-mcp/src/vehicle_mcp/tools.py`: `_with_ride_scalars` calls `/rides`
  with the user's original `start_date`/`end_date`, joins rows by
  `session_id`, adds `ride` (`values`, `flags`, `columns`), `ride: null` with a
  reason, `skipped`, and the `ride_scalars: "unavailable"` fallback for a
  missing `/rides` or any source error. Undated sessions keep today's shape.
- `vehicle-mcp/tests/test_tools.py`: join, skipped session, undated session,
  missing route, `/rides` error, and UTC-bound expectations.
- `vehicle-mcp/tests/test_source.py`: the join also works through a non-HTTP
  `HistorySource`.
- Extra fix (213537c): `/rides` position-looking columns, values and flags are
  dropped and counted too, not only names in `/summary`. This was not an
  explicit LR9 test but follows D-076's "every name a new path returns".

Bound comparison: a one-off run with
`uv run --project vehicle-server --with-editable ./vehicle-mcp` compared
`vehicle_mcp.tools._parse_bound` with `vehicle_server.ride_summary.parse_utc_bound`
for a date-only bound, a timestamp without offset and a timestamp with
`+02:00`. All three matched; the test asserts the same UTC values.

### LR9-4 — README (ca0c0f6)
- `vehicle-mcp/README.md`: added `get_ride_summary`, the extended
  `query_ride_history` output, the `/summary` and `/rides` dependencies, the
  stored-value rule, the fallback and position filtering.
- Server history check: server#46 merged 2026-11-02 (`53641e2`), but no release
  tag contains it; `v0.6.0` and older predate it. README states server#46 as
  the minimum and that no tag has it yet.

### LR9-5 — checks
- Full checks pass; see below. No code change in this task.

### LR9-6 — log and PR
- This log on `vehicle-workspace` branch `ext/opencode-long-run-9-log`; PR
  vehicle-mcp#16 from `ext/opencode-mcp-ride-summary` to `main`, body starts
  `needs-claude-review`; not merged.
- `scripts/vscode_workspace.py` does not exist on workspace `main` (it is only
  on `claude/vscode-visibility`), so it was not run, as the task allows.

## Result
D-102 is implemented in vehicle-mcp: tool 8 and the extended history join,
read-only and value-preserving. Four feature/docs commits plus one position
filtering fix are pushed; PR #16 is open for Claude review.

## Checks
- `uv run pytest -q`: 96 passed.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: 23 files already formatted.
- MCP smoke: `build_server(...).list_tools()` returns 8 tools.
- `python3 scripts/check_zones.py vehicle-mcp --base origin/main`: YELLOW only
  (README, client, server, source, tools, support, test_server, test_source,
  test_tools); no red.
- Bound comparison (LR9-3): date-only, no-offset and offset bounds all equal
  between vehicle-mcp and vehicle-server.

## Unsure about
- The task file says D-102 is merged, but vehicle-defs#127 is still open and
  D-102 is only on `claude/d102-mcp-ride-tools`. The task file itself is only
  on `claude/vscode-visibility` (`fbaff23`), not workspace `main`. I read both
  from those branches and did not edit vehicle-defs.
- A server without `/sessions/{id}/summary` is not given a dedicated
  `SummaryRouteUnavailable` error; its default 404 is reported as a generic
  server error. Only `/rides` has the specified fallback. This matches the
  task text but is a small asymmetry.
- A binned summary entry is dropped whole when any axis input looks like a
  position name. This is the conservative reading of "apply `is_position_name`
  to every name a new path returns"; it could hide a non-position value in an
  unusual future definition.
- No release tag contains server#46, so README cannot name a released minimum.
  If a later server release is cut, that sentence should be updated.

## For Claude
- Please confirm the D-102/defs#127 merge order and whether the README wording
  "server#46, no release tag contains it yet" is the desired minimum.
- The extra 213537c position filtering on `/rides` was added for D-076 even
  though LR9-3 did not list a test for it; please check the drop-whole-entry
  choice for binned axes.
- No additional tool, parameter or cross-ride aggregate was added; none was
  needed for D-102.

## Claude review
