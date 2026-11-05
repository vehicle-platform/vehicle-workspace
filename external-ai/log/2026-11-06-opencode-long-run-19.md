---
date: 2026-11-06
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-19-window-invariants-mobile-demo
repos: [vehicle-workspace, vehicle-server, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-19-log, vehicle-server:ext/opencode-server-window-invariants, vehicle-mobile:ext/opencode-mobile-health-windows, vehicle-server:ext/opencode-server-demo-session]
prs: []
zone: green
review: pending
---

# DeepSeek long run 19 — window invariants, phone card, synthetic demo

## Goal
Test the provisional D-079 state machine against general properties, show the stored window
instances on the phone, and add a synthetic demo session that exercises every window; no window
rule, formula, dependency or real data changes.

## Changes
- `<repo>/<path>`: what changed and why.

## Result
In progress. Task list:

- [x] LR19-0 — log first
- [ ] LR19-1 — server: property tests for the window state machine
- [ ] LR19-2 — mobile: read the block
- [ ] LR19-3 — mobile: health windows on the ride summary screen
- [ ] LR19-4 — server: a synthetic demo session
- [ ] LR19-5 — server: test, README, PR
- [ ] LR19-6 — close the log

## Checks
- `<command>`: pass / fail (paste the failing part).
- `python3 scripts/check_zones.py <repo>`: <result>

## Unsure about
Assumptions, shortcuts, things you could not verify (hardware, CI-only checks, missing context).

## For Claude
Red-zone requests (path + wanted change), signals or decisions that would be needed, suspected conflicts with PLATFORM-RULES or DECISIONS.md, refactors you would suggest.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
