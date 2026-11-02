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
- In progress.

## Result

| Task | Status | Evidence |
|---|---|---|
| RS-1 `GET /sessions/{id}/summary` | todo | |
| RS-2 `GET /rides` | todo | |
| RS-3 Server docs | todo | |
| RS-4 Analyzer clients | todo | |
| RS-5 Ride summary card (`E`) | todo | |
| RS-6 Compare summary table (`A`) | todo | |
| RS-7 Ride history view | todo | |
| RS-8 UI smoke + docs | todo | |

## Checks
- Not run yet.

## Unsure about
- To be filled while working.

## For Claude
- To be filled while working.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
