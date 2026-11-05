---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-18-d079-window-instances
repos: [vehicle-workspace, vehicle-server, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-long-run-18-log, vehicle-server:ext/opencode-server-window-instances, vehicle-analyzer:ext/opencode-analyzer-health-windows]
prs: []
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

## Result
In progress. Task list:

- [x] LR18-0 — log first
- [ ] LR18-1 — server: keep `WindowResult`s in `SummaryEvaluation`
- [ ] LR18-2 — server: `health_windows` report block + text report + tests
- [ ] LR18-3 — server: README, checks, PR
- [ ] LR18-4 — analyzer: pure health-windows parser + Vitest
- [ ] LR18-5 — analyzer: Health windows card in view E + component tests
- [ ] LR18-6 — analyzer: Playwright, ROADMAP, checks, PR
- [ ] LR18-7 — close the log

## Checks
- `python3 scripts/check_zones.py`: green so far (log only).

## Unsure about
- Starting point read: LR18 task and section 0.

## For Claude
- (to be filled)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
