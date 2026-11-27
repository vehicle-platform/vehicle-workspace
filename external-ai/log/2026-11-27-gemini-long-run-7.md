---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-7
repos:
  - vehicle-workspace
  - vehicle-defs
  - vehicle-server
  - vehicle-ml
branches:
  - vehicle-workspace:ext/gemini-long-run-7-log
  - vehicle-defs:ext/gemini-visibility-inventory
  - vehicle-defs:ext/gemini-time-sync
  - vehicle-server:ext/gemini-mt-llm-turns
  - vehicle-defs:ext/gemini-cache-round3
  - vehicle-ml:ext/gemini-marks-labels
  - vehicle-defs:ext/gemini-vss-two-wheeler
prs: []
zone: yellow
review: pending
---

# long-run-7 (visibility inventory, time-sync options, cache round 3, marks weak labels, VSS two-wheeler draft)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-7.md` end to end (G7-0, G7-1, G7-2, G7-3a, G7-3b, G7-4, G7-5, G7-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes

### G7-0 and G7-9 — Session log (`vehicle-workspace`, `ext/gemini-long-run-7-log`, GREEN)
- `external-ai/log/2026-11-27-gemini-long-run-7.md`: opened at session start (G7-0).

## Result
(In progress.)

## Checks
- G7-0: pending zone check and push.

## Unsure about
(None yet.)

## For Claude
(None yet.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
