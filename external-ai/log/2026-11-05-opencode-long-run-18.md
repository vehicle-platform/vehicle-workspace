---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-18-d079-window-instances
repos: [vehicle-workspace, vehicle-server, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-long-run-18-log, vehicle-server:ext/opencode-server-window-instances, vehicle-analyzer:ext/opencode-analyzer-health-windows]
prs: [vehicle-server#55, vehicle-analyzer#48]
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
  - `src/components/HealthWindows.tsx` + `SessionPanel.tsx` + `App.tsx`: view E stores the full
    report it already fetched, renders the Health windows card below ride summary, the rule
    badge, per-defs-window SVG timeline bands (qualifying filled, others outlined, first
    qualifying marked), instance tables, computed `/summary` signals and the unknown/not
    evaluated states. `App` passes the loaded replay end on the same t0 axis when E has it;
    otherwise the timeline uses the last instance end. No new npm package. Commit `be60dc7`.
  - `tests/components/HealthWindows.test.tsx`: missing/malformed/loaded states, band count,
    first-qualifying mark, unknown key, not-evaluated row, fallback span.
  - `ui-tests/health-windows.spec.ts`: mocked report shows the card and bands, only the app and
    configured server are requested. Commit `0b90a11`.
  - `docs/ROADMAP.md`: A15 done (long run 18), analyzer#48. Commit `64b33da`.
  - `HealthWindows.tsx`: plain loading message before the report arrives (no false "older
    server" flash). Commit `d276c85`.
  - PR: https://github.com/vehicle-platform/vehicle-analyzer/pull/48 (not merged; needs
    vehicle-server#55 first).

## Result
Complete. Task list:

- [x] LR18-0 — log first
- [x] LR18-1 — server: keep `WindowResult`s in `SummaryEvaluation`
- [x] LR18-2 — server: `health_windows` report block + text report + tests
- [x] LR18-3 — server: README, checks, PR
- [x] LR18-4 — analyzer: pure health-windows parser + Vitest
- [x] LR18-5 — analyzer: Health windows card in view E + component tests
- [x] LR18-6 — analyzer: Playwright, ROADMAP, checks, PR
- [x] LR18-7 — close the log

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
- `npm test -- --run`: 44 files, 341 passed.
- `npm run build`: pass (Vite chunk-size warning only).
- `npx playwright test`: 21 passed.
- PR #48: https://github.com/vehicle-platform/vehicle-analyzer/pull/48 (not merged).
- `uv.lock` unchanged; `package-lock.json` unchanged; `src/defs/*` untouched.

## Unsure about
- `health_windows` t0 reuses `series.load_all`, so it matches `/series` exactly; `load_all`
  also reads `derived.parquet`, which `store_all` writes before the summary.
- The block is only added on a successful summary evaluation; a failed evaluation still writes
  the existing `{"error": ...}` block and no `health_windows`.
- `HealthWindows` fetches `/summary` independently from `RideSummary`, so view E makes two
  summary requests for one selected session. The card needs the computed signals and the task
  only forbade a second report request; sharing the fetch would be a small follow-up refactor.
- The timeline uses the loaded replay end only when the selected session is the loaded one;
  otherwise it falls back to the last instance end, because the report has no session span.
- The text report window line has two leading spaces (`  W3_WARM_IDLE: ...`) to sit under the
  existing derived-summary indentation; the task example omits them.

## For Claude
- vehicle-server `CLAUDE.md` §Derived signals line 17: append to the Part 3 sentence
  "→ `derived_summary.parquet` + the `derived_summary` report block" the words
  "including the D-079 `health_windows` instances on the `/series` t0 axis".
- No rule-2 surprise: golden A/B pass, `derived_summary` records/values are unchanged; only the
  new `health_windows` key is added.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
