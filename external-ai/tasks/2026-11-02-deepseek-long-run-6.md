# DeepSeek long run 6 — 2026-11-02 (class-B ride summaries: server read API + analyzer views)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

Two repos (Python + TypeScript), both **green** zones. Read section 0 completely before writing
code.

## 0. Before you start (read, do not skip)

### Why this run

vehicle-server already computes the D-070 class-B per-ride summaries (one session = one ride):
`derived/summary.py` → `derived_summary.parquet` + the `derived_summary` block of `report.json`.
Nobody can see them: the report block only carries per-signal status and scalar values, the binned
summaries (time-at-temperature histograms, operating-point time) are only in the parquet file, and
the analyzer shows none of it. This run exposes them read-only and draws them. It adds **no new
summary, no new formula and no new signal**.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py <repo> --base origin/main`. **Red = stop**, write the request
  into the log.
- `vehicle-server/CLAUDE.md` (Read API, Storage, Derived signals) and `vehicle-server/README.md`
  (the class-B / ride summary section and the `/series`, `/stats`, `/track` rows). Code:
  `src/vehicle_server/api.py` (auth dependency, how `/stats` and `/track` load a session and map
  errors to 404/422), `derived/summary.py` (`SummaryRow`, `_summarize_one`, `evaluate`, statuses
  `COMPUTED` / `NOT_READY` / `NOT_IMPLEMENTED` / `MISSING_INPUTS` / `ERROR`, `bin_edges`,
  `cell_axes`), `derived/__init__.py` (`store_all`: how `derived_summary.parquet` and the report
  block are written), `index.py` (session list, `has_derived`), `position.py` (the position-name
  rule). Tests: `tests/test_stats.py`, `tests/test_track_api.py`, `tests/test_derived_summary.py`, `tests/conftest.py`,
  `tests/make_fixtures.py`, `tests/derived_helpers.py`.
- Defs (read only): `external/vehicle-defs/derived/cl250_derived.yaml`, the class-B entries
  (`class: B`, `unit`, `range`, `bins`, `inputs`, `ready_phase0`, `pending_inputs`).
- `vehicle-analyzer/CLAUDE.md`, `docs/ROADMAP.md`, `src/services/sessionClient.ts`
  (`buildRequest`, `describeHttpError`), `src/services/trackClient.ts` (strict response parsing
  style to copy), `src/components/SessionPanel.tsx` (recorded sessions, key `E`, "report summary"),
  `src/components/ComparePanel.tsx` (key `A`, CSV export on `V`), `src/App.tsx`, `src/ui/keys.ts`
  (`GLOBAL_KEYS`), `tests/components/`, `ui-tests/views.spec.ts`, `ui-tests/track.spec.ts`.
- `vehicle-defs/docs/DECISIONS.md` **D-070** (derived signals), **D-087** (ride = one stop epoch on
  rt-core, one session on the server; own `stale_after_ms`), **D-033** (public repos), **D-081** /
  **D-085** (analyzer scope).
- `ISSUES.md` row **E-26 (1)**: `ride_distance_gps` ignores `gps_fix_type`. That needs a user
  decision; **do not change it** in this run. Show the value as the server computes it.

### Hard rules for the whole run

- **Read-only.** No route writes, recomputes or deletes anything. Recomputing stays the
  `vehicle-server derive` CLI.
- **Names, units, ranges and bin edges from the server/defs, never literals** (invariant 2). The
  analyzer never hard-codes a summary name, unit, bin edge or display order; it renders what the
  response says (order = the response order, which is defs order).
- **No position.** The summaries contain none; keep it that way (no field named like a position,
  see `position.py`).
- **No new dependency** in either repo (server: pyarrow + standard library; analyzer: SVG or
  `<canvas>`, no chart library). `package.json` / `pyproject.toml` stay unchanged.
- **Do not touch** `derived/summary.py` formulas, the golden vectors, `tests/golden/`, the defs
  submodule pin, `.github/`, any `CLAUDE.md`, `STATUS.md`, `ISSUES.md`, `DECISIONS.md`.
- All test data is **synthetic** (D-033), built with the existing fixture helpers.

Branches (one PR per repo, each opened against `main`):

| Part | Repo | Branch | Tasks |
|---|---|---|---|
| A | vehicle-server | `ext/opencode-server-ride-summary` | RS-1 .. RS-3 |
| B | vehicle-analyzer | `ext/opencode-analyzer-ride-summary` | RS-4 .. RS-8 |
| Log | vehicle-workspace | `ext/opencode-long-run-6-log` | the session log |

One session log for the whole run: `external-ai/log/2026-11-02-opencode-long-run-6.md` (copy
`TEMPLATE.md`; `review: pending`; a result row per task with code `file:line`, test names, status).
Create and push the log branch **first**, with the Result table rows marked `todo`, and update it
as tasks finish.

## Part A — vehicle-server

### RS-1 `GET /sessions/{id}/summary`

A new authenticated route (same auth dependency as `/stats`), served from the stored files only:

```json
{
  "session_id": "...",
  "ride_definition": "<from the report block>",
  "defs_version": "<from the report>",
  "signals": [
    {"name": "ride_distance", "status": "computed", "unit": "km", "range": [0, 1000],
     "kind": "scalar", "value": 12.3, "flag": null},
    {"name": "ride_coolant_time_at_temp", "status": "computed", "unit": "s", "range": [..],
     "kind": "binned",
     "axes": [{"input": "<axis input name>", "unit": "<axis unit>", "edges": [[lo, hi], ...]}],
     "cells": [{"index": 0, "axes": [0], "value": 41.0, "flag": null}, ...],
     "total_s": 900.0, "outside_s": 3.0},
    {"name": "...", "status": "not_ready", "reason": "pending_inputs", "pending_inputs": ["..."]},
    {"name": "...", "status": "missing_inputs", "missing": ["..."]}
  ]
}
```

- `signals` = every class-B signal of the report's `derived_summary` coverage, **in that order**
  (defs order); the non-computed ones keep their status and reason fields as stored.
- Scalars: value/flag from the report block (or the parquet row; they must agree, test it).
- Binned: the cells from `derived_summary.parquet` (`cell`, `edges`, `value`, `flag`); the axis
  description (`input`, `unit`, bin layout) from the pinned defs `bins` of that signal, through the
  existing `bin_edges` / `cell_axes` helpers, never recomputed by hand. If the stored edges and the
  defs edges disagree (the session was decoded with another defs version), return the stored edges
  and add `"defs_mismatch": true` to that signal; test it.
- `unit` and `range` come from the defs entry.
- Errors: unknown session 404 (same message style as `/stats`); a session without a
  `derived_summary` block or whose block is `{"error": ...}` → 404 with
  `session has no ride summary` / the stored error text in `detail`; never 500.
- Pure building logic in a new module `src/vehicle_server/ride_summary.py` (no FastAPI import), the
  route in `api.py` only parses and maps errors.

Tests `tests/test_ride_summary.py`: synthetic session with scalars + one binned summary +
not_ready + missing_inputs entries; order equals coverage order; scalar agreement report/parquet;
binned cells and axes; defs mismatch; no summary → 404; error block → 404 with the text; auth
required.

### RS-2 `GET /rides` (cross-session trend table)

Authenticated. Query: `from` / `to` (optional ISO 8601 date or timestamp, inclusive, UTC; same
parsing rules as the session list if one exists, otherwise document yours), `names` (optional,
comma-separated class-B **scalar** names; default all scalars). Response:

```json
{"columns": [{"name": "ride_distance", "unit": "km"}, ...],
 "rows": [{"session_id": "...", "created_utc": "...", "values": {"ride_distance": 12.3, ...},
           "flags": {"ride_distance": null, ...}}]}
```

- One row per session that has a computed `derived_summary` block, sorted by `created_utc`
  ascending; sessions without one are skipped (count them in `"skipped": n`).
- A name that is not a class-B scalar in defs → 422 listing the unknown names (binned summaries
  are refused here with their own message: they belong to RS-1).
- A value that is not `computed` for that session is `null` with its status in `flags`.
- Read the report blocks, not every parquet file (it must stay cheap for 100+ sessions). Test with
  ≥ 3 synthetic sessions, including one without summaries and one with a not_ready value.

### RS-3 Server docs

`README.md`: the `/summary` and `/rides` rows in the read API table, response examples, the error
cases, and one sentence that `ride_distance_gps` currently integrates GNSS speed without a fix-type
gate (ISSUES E-26 (1)). If `CLAUDE.md` should mention the routes, write the wording into the log's
*For Claude* (do not edit it).

Checks for Part A (all must pass before each push): `cd vehicle-server`,
`uv sync --locked`, `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .` (the
same steps as `.github/workflows/`).

## Part B — vehicle-analyzer

Work against a mock that returns the RS-1 / RS-2 contracts above if Part A is not finished.

### RS-4 Clients (`src/services/rideSummaryClient.ts`)

- `fetchRideSummary(cfg, sessionId)` and `fetchRides(cfg, {from, to, names})` reusing
  `buildRequest` / `describeHttpError`.
- `parseRideSummary(json)` / `parseRides(json)` validate strictly like `parseTrackResponse`
  (known `status` and `kind` values, `cells[i].axes.length === axes.length`, edges are `[lo, hi]`
  with `lo < hi`, finite numbers or `null`) and throw a readable error otherwise.
- 404 `session has no ride summary` maps to a "no ride summary" state, not an error.

Tests: `tests/rideSummaryClient.test.ts` (valid, every malformed case, the 404 mapping).

### RS-5 Ride summary card in Recorded sessions (`E`)

In `SessionPanel.tsx`, next to the existing "report summary", a "ride summary" section for the
selected session (new component `src/components/RideSummary.tsx`):
- states: no server, loading, no ride summary, error, loaded;
- scalars: a table `name | value | unit | flag`, values formatted with a precision derived from the
  response's `range` (no per-name formatting);
- binned: one small SVG bar chart per signal (one axis) or a heat grid (two axes), axis labels from
  `axes[].input` + `unit` + the edges, `total_s` and `outside_s` under it; `defs_mismatch` shows a
  visible warning;
- the non-computed signals in a collapsed "not available (n)" list with status and reason;
- no fetch per keystroke or per render: fetch once per selected session, cancel on change.

Tests: component tests in `tests/components/` for each state, a binned 1-axis and a 2-axis
signal, the collapsed list and the mismatch warning; pure layout helpers (bar scaling, precision
from range) in `src/services/rideSummaryLayout.ts` with unit tests.

### RS-6 Compare (`A`): summary table A vs B

In `ComparePanel.tsx`, a "ride summaries" table under the overlay: scalar rows present in both
sessions, `A | B | B − A | unit`; a row where either side is not computed shows its status instead
of a number; the CSV export (`V`) gets a second block or an option for this table, with the same
`#` comment line style. Reuse RS-4/RS-5 helpers. Tests.

### RS-7 Ride history view (new key)

A new view "Ride history": pick 1-4 scalar columns from `/rides` (the list comes from the
response `columns`, never hard-coded), an optional date range, and draw one small SVG line/dot
chart per column over the rides (x = ride order or `created_utc`, toggle), gaps for null values,
hover shows session id + value + flag, click opens the session in the Recorded sessions view.
Pick a free key: check `GLOBAL_KEYS` in `src/ui/keys.ts` **and** every panel-local binding; use
`R` if free, otherwise the first free letter, and write the choice into the log. Key bar entry,
help text and layout persistence like the other views.

Tests: component tests (states, column picker from the response, null gaps).

### RS-8 UI smoke + docs

- Playwright: route `/sessions`, `/sessions/{id}/summary` and `/rides` to fixtures; open `E` and
  check the ride summary card, open the new history view; add it to the views smoke test. Keep the
  track spec's rule: every request goes to the app origin or the configured server origin.
- `docs/ROADMAP.md`: add a row (next free `A` number) "Ride summaries (class B)" marked done with
  this run's PR; `README.md`: the card, the Compare table, the history view and its key.

Checks for Part B (all must pass before each push): `cd vehicle-analyzer && npm ci`,
`npm run build`, `npm test`, `npm run test:ui` (after `npx playwright install chromium` once).

## Finish

- Open the vehicle-server PR and the vehicle-analyzer PR (body: task list, checks, screenshots
  optional), then the workspace PR for the log. Fill the log: Result table, Checks, Unsure about,
  For Claude.
- Do not merge anything.
- Put into *For Claude*: every place where the rules above were ambiguous and the choice you made,
  the key you picked for RS-7, the `from`/`to` parsing you used, whether stored and defs bin edges
  ever disagreed in practice, and whether a vehicle-mcp tool for ride summaries looks useful (the
  vehicle-mcp tool list is fixed and **needs the user's approval**: do not add one, only describe
  it).
