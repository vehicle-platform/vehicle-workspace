---
date: 2026-11-26
tool: gemini-cli/gemini-4
topic: long-run-3
repos: [vehicle-workspace, vehicle-ml, vehicle-defs, vehicle-server]
branches:
  - vehicle-workspace:ext/gemini-long-run-3-log
prs: []
zone: yellow
review: pending
---

# long-run-3 (bake-off run, held-out eval in chat-eval, Turkish routing coverage)

## Goal
Execute `external-ai/tasks/2026-11-26-gemini-long-run-3.md` from **G3-0** through **G3-4** in order: run the D-132 stage-0 base-model bake-off in `vehicle-ml`, publish the synthetic bake-off results page in `vehicle-defs`, add runtime held-out suite support, synthetic guard gate tests, and Turkish routing coverage in `vehicle-server`, and finalize this session log.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-26-gemini-long-run-3.md`: initialized session log (G3-0).

## Result
In progress.

## Checks
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-gemini-long-run-3.md`: GREEN

## Unsure about
None yet.

## For Claude
None yet.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
