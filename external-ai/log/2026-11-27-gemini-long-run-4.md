---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-4
repos: [vehicle-workspace]
branches:
  - vehicle-workspace:ext/gemini-long-run-4-log
prs: []
zone: green
review: pending
---

# long-run-4 (parked-current note, 3-model bake-off, prompt-cache measurement, ride event marks, SIL inventory, RAG eval, analyzer tests)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-4.md` across G4-0, G4-A, G4-1, G4-2, G4-3, G4-4, G4-6, G4-7, G4-8, and G4-5 in order, keeping every repo on its dedicated `ext/gemini-*` branch with green checks and zone checks before each push.

## Changes

### G4-0 — Session log (`vehicle-workspace`, `ext/gemini-long-run-4-log`, GREEN)
- Initialized `external-ai/log/2026-11-27-gemini-long-run-4.md` (status `review: pending`).
- Verified all start gates are open (`vehicle-ml#32`, `vehicle-defs#207`, `vehicle-server#105` all `MERGED`).

## Result
In progress.

## Checks
- `gh pr view 32 -R vehicle-platform/vehicle-ml --json state`: `MERGED`
- `gh pr view 207 -R vehicle-platform/vehicle-defs --json state`: `MERGED`
- `gh pr view 105 -R vehicle-platform/vehicle-server --json state`: `MERGED`

## Unsure about
(Will be updated as tasks complete.)

## For Claude
(Will be updated as tasks complete.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
