---
date: 2026-11-26
tool: gemini-cli/gemini-4
topic: long-run-2
repos: [vehicle-workspace, vehicle-server, vehicle-mcp, vehicle-mobile, vehicle-ml, vehicle-defs]
branches:
  - vehicle-workspace:ext/gemini-long-run-2-log
  - vehicle-server:ext/gemini-notification-i18n
  - vehicle-mcp:ext/gemini-rag-quality
  - vehicle-mobile:ext/gemini-chat-list
  - vehicle-ml:ext/gemini-model-bakeoff
  - vehicle-defs:ext/gemini-validation-plan
prs: []
zone: yellow
review: pending
---

# long-run-2 (assistant i18n, RAG quality, chat list UI, model bake-off, validation plan)

## Goal
Execute `external-ai/tasks/2026-11-26-gemini-long-run-2.md` tasks G2-0 through G2-6 in order:
- G2-0: Initialize session log (`vehicle-workspace`).
- G2-1: Rider notification texts per locale (`vehicle-server`, D-123, D-125).
- G2-2: Retrieval quality for `search_knowledge` (`vehicle-mcp`, D-132, T60 follow-up).
- G2-3: Conversation list and memory UI + AlertBanner layout fix (`vehicle-mobile`, D-128, D-130, T47).
- G2-4: Base-model bake-off harness (`vehicle-ml`, D-132 stage 0, T58).
- G2-5: Validation plan draft (`vehicle-defs`, `docs/ideas/validation-plan.md`).
- G2-6: Finalize session log (`vehicle-workspace`).

## Changes
- `vehicle-workspace/external-ai/log/2026-11-26-gemini-long-run-2.md`: initialized session log (G2-0).

## Result
In progress.

## Checks
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-gemini-long-run-2.md`: pending

## Unsure about
(None yet.)

## For Claude
(None yet.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
