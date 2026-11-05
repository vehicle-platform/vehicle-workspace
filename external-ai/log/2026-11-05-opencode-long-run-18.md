---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-18-d079-window-instances
repos: [vehicle-workspace, vehicle-server, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-long-run-18-log, vehicle-server:ext/opencode-server-window-instances, vehicle-analyzer:ext/opencode-analyzer-health-windows]
prs: [vehicle-server#55]
zone: green
review: pending
---

# DeepSeek long run 18 — D-079 window instances

## Goal
Store the D-079 window instances the server already finds in the `derived_summary` report block
and render them in vehicle-analyzer view E, with the window rules unchanged and the analyzer
reading only the report and bundled defs.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-05-opencode-long-run-18.md`: this session log.
- `vehicle-server` branch `ext/opencode-server-window-instances`:
  - `src/vehicle_server/derived/summary.py`: `SummaryEvaluation.windows` keeps the
    `WindowResult`s that already feed the 17 class-B scalars; `evaluate` fills it from
    `_window_results`. Commit `fd92b2b`.
  - `src/vehicle_server/derived/__init__.py`: `derived_summary.health_windows` block with
    all evaluated instances (start/end/duration on the `/series` t0 axis, close reason,
    qualifies, first-qualifying flag), per-window counts, `t0_device_ms` and the provisional
    D-079 rule label. Commit `9a9d0b5`.
  - `src/vehicle_server/report.py`: one text line per window after the ride-summary line.
  - `tests/test_health_window_summaries.py`: checks the kept W3 result is the one the scalars
    use. `tests/test_health_windows_ingest.py`: end-to-end block/API/CLI/text checks, t0
    equality with `/series`, and unchanged `derived_summary` keys. Commit `9a9d0b5`.
  - `README.md`: block shape, `/series` t0 axis, one entry per evaluated window, empty instance
    arrays, exactly one `first_qualifying`, and analyzer-never-recomputes. Commit `2891eb7`.
  - PR: https://github.com/vehicle-platform/vehicle-server/pull/55 (not merged).
- `vehicle-analyzer` branch `ext/opencode-analyzer-health-windows`:
  - New `src/services/healthWindows.ts`: pure defensive parser of
    `report.derived_summary.health_windows`; rejects missing key as `not in report`, malformed
    fields as `malformed: <what>`, keeps report order and marks keys absent from the bundled
    defs with `unknownInDefs: true`. No recomputation. Commit `22d6c82`.
  - `tests/healthWindows.test.ts`: valid block, missing block, malformed instance/time/type,
    unknown key, order kept.

## Result
In progress. Task list:

- [x] LR18-0 — log first
- [x] LR18-1 — server: keep `WindowResult`s in `SummaryEvaluation`
- [x] LR18-2 — server: `health_windows` report block + text report + tests
- [x] LR18-3 — server: README, checks, PR
- [x] LR18-4 — analyzer: pure health-windows parser + Vitest
- [ ] LR18-5 — analyzer: Health windows card in view E + component tests
- [ ] LR18-6 — analyzer: Playwright, ROADMAP, checks, PR
- [ ] LR18-7 — close the log

## Checks
- `python3 scripts/check_zones.py . --base origin/main` (workspace): green.
- `python3 ../scripts/check_zones.py vehicle-server --base origin/main`: green.
- `uv run ruff check .`: pass.
- `uv run ruff format --check .`: 94 files already formatted.
- `uv run pytest -q`: 684 passed, 1 third-party warning.
- `uv run pytest tests/test_golden.py tests/test_golden_b.py -q`: 21 passed.
- `git push` to `origin/ext/opencode-server-window-instances`: commits `9a9d0b5`, `2891eb7`.
- PR #55: https://github.com/vehicle-platform/vehicle-server/pull/55 (not merged).
- `npm test -- --run tests/healthWindows.test.ts`: 3 passed.
- `python3 ../scripts/check_zones.py vehicle-analyzer --base origin/main`: green.

## Unsure about
- `health_windows` t0 reuses `series.load_all`, so it matches `/series` exactly; `load_all`
  also reads `derived.parquet`, which `store_all` writes before the summary.
- The block is only added on a successful summary evaluation; a failed evaluation still writes
  the existing `{"error": ...}` block and no `health_windows`.

## For Claude
- (nothing yet)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
