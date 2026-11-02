---
date: 2026-11-02
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-6-ride-summary
repos: [vehicle-server, vehicle-analyzer, vehicle-workspace]
branches: [vehicle-server:ext/opencode-server-ride-summary, vehicle-analyzer:ext/opencode-analyzer-ride-summary, vehicle-workspace:ext/opencode-long-run-6-log]
prs: []
zone: green
review: pending
---

# long-run-6 ride summaries

## Goal
Expose the stored D-070 class-B ride summaries through read-only server APIs and render them in the analyzer: `GET /sessions/{id}/summary`, `GET /rides`, a ride-summary card in Recorded sessions, a Compare A-vs-B table, and a ride-history view. No new summaries, formulas or signals.

## Changes
- `vehicle-server/src/vehicle_server/ride_summary.py`: added the pure read-side builder for the stored `derived_summary` report block and `derived_summary.parquet` (RS-1), the class-B scalar selector and UTC date parsing, and the `/rides` table builder (RS-2). No formula, signal or write path changed.
- `vehicle-server/src/vehicle_server/api.py`: added authenticated `GET /sessions/{id}/summary` (RS-1) and `GET /rides` (RS-2), mapping missing/error summaries to 404 and invalid `/rides` names to 422.
- `vehicle-server/tests/test_ride_summary.py`: 19 tests for both routes, including defs order, scalar/parquet agreement, one- and two-axis cells, stored-edge mismatch, skipped sessions, null/status values and date bounds.
- `vehicle-server/README.md`: read-API rows, examples, error cases, UTC date rules and the E-26 (1) fix-type note (RS-3).

## Result

| Task | Status | Evidence |
|---|---|---|
| RS-1 `GET /sessions/{id}/summary` | done | `vehicle-server/src/vehicle_server/ride_summary.py:180` (`build_ride_summary`) and `:206` (`load_ride_summary`); route `src/vehicle_server/api.py:238`; tests `tests/test_ride_summary.py:141-343` (19 total, 10 summary cases) |
| RS-2 `GET /rides` | done | `vehicle-server/src/vehicle_server/ride_summary.py:236` (`select_scalar_names`), `:265` (`parse_utc_bound`), `:302` (`build_rides`); route `src/vehicle_server/api.py:248`; tests `tests/test_ride_summary.py:345-448` |
| RS-3 Server docs | done | `vehicle-server/README.md` `/summary` and `/rides` table rows, examples and E-26 (1) sentence |
| RS-4 Analyzer clients | todo | |
| RS-5 Ride summary card (`E`) | todo | |
| RS-6 Compare summary table (`A`) | todo | |
| RS-7 Ride history view | todo | |
| RS-8 UI smoke + docs | todo | |

## Checks
- `cd vehicle-server && uv run pytest -q`: pass, `432 passed, 1 warning` (2026-11-02).
- `cd vehicle-server && uv run ruff check .`: pass.
- `cd vehicle-server && uv run ruff format --check .`: pass, `73 files already formatted`.
- `python3 scripts/check_zones.py vehicle-server --base origin/main --path src/vehicle_server/ride_summary.py`: GREEN.
- `python3 scripts/check_zones.py vehicle-server --base origin/main --path src/vehicle_server/api.py`: GREEN.
- `python3 scripts/check_zones.py vehicle-server --base origin/main --path tests/test_ride_summary.py`: GREEN.
- `python3 scripts/check_zones.py vehicle-server --base origin/main --path README.md`: GREEN.

## Unsure about
- `/rides` `from`/`to` parsing is ours (there was no existing session-list date parser): date-only means the whole UTC day, timestamps without an offset are UTC, offsets are converted. An inverted range is not an error; it returns no rows after the normal filter.
- `/rides` treats a present, non-error `derived_summary` block as a computable row even when one or more values are not computed; those values are null and their status is in `flags`. A report missing the signal gives `flags: "missing"`.
- `/summary` returns the stored `bin0`/`bin1` edges and sets `defs_mismatch` when they differ from the pinned defs. If a stored binned signal has no parquet file/rows, it is a 404 (`session has no ride summary`) rather than a 500.
- Scalar values/flags are returned from the report block; a test ingests `v4_session` and asserts they agree with the parquet scalar rows.
- `/summary` emits signals in global defs order, not the record-grouped order of the report's `records` object.

## For Claude
- `vehicle-server/CLAUDE.md` still lists only the older read routes; please add `/summary` and `/rides` there if the wording is useful (red/synced file, not edited).
- E-26 (1) is deliberately untouched: `ride_distance_gps` integrates GNSS speed without a fix-type gate. `/summary` shows the stored value as computed; README notes the open decision.
- Confirm the `/rides` date-bound choice (date-only whole UTC day; offsetless timestamps UTC; inverted range empty) and whether `skipped` should count only missing/error blocks, as implemented.
- `/summary` sets `defs_mismatch` only from stored cell edges; the parquet schema has two fixed edge pairs (`bin0`, `bin1`), so a future defs change to more than two axes would need a storage change.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
