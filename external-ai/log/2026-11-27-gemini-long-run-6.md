---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-6
repos:
  - vehicle-workspace
  - vehicle-server
  - vehicle-defs
  - vehicle-analyzer
  - vehicle-mcp
branches:
  - vehicle-workspace:ext/gemini-long-run-6-log
prs: []
zone: yellow
review: pending
---

# long-run-6 (cache measurement round 2, marks in the assistant, marks label export, multi-node SIL note, analyzer tests, rider-facing labels)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-6.md` end to end (G6-0 through G6-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-27-gemini-long-run-6.md` (`ext/gemini-long-run-6-log`): opened session log (G6-0).

## Result
- **G6-1 (skipped):** Prerequisite not met — `vehicle-server#110` (`ext/gemini-multiturn-eval`) is still open (`UNSTABLE`) and not merged to `vehicle-server/main` (`e39fc24`), so `src/vehicle_server/chat/eval/spec.json` has no `conversation`/`turn` items and `report.py` has no `by_turn` reporting. Per G6-1 instructions, skipped cleanly.

## Checks
- `python3 scripts/check_zones.py vehicle-workspace --base origin/main`: pending

## Unsure about
- Note: `external-ai/tasks/2026-11-27-gemini-long-run-6.md` was read from `origin/claude/g6-brief` (open PR `vehicle-workspace#266`), while `ext/gemini-long-run-6-log` is branched from `origin/main` (`ad02ef8`).

## For Claude
- (Will be filled as tasks proceed.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
