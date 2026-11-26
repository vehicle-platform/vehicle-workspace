---
date: 2026-11-26
tool: gemini-cli/gemini-4
topic: ride-llm-heldout
repos: [vehicle-workspace, vehicle-ml]
branches: [vehicle-workspace:ext/gemini-ride-llm-heldout-log, vehicle-ml:ext/gemini-ride-llm-heldout]
prs: []
zone: green
review: pending
---

# Ride LLM stage 0: held-out eval set + template dataset scaffold

## Goal
Create an independent, held-out 100-item bilingual (en/tr) evaluation set, a validator with pytest coverage, and a stdlib-only template dataset generator with number and contamination guards in `vehicle-ml` (tasks G1-0 through G1-4, Ride LLM stage 0 / D-132).

## Changes
- `vehicle-workspace/external-ai/log/2026-11-26-gemini-ride-llm-heldout.md`: opened session log (G1-0).

## Result
In progress (G1-0 initialized).

## Checks
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-gemini-ride-llm-heldout.md`: GREEN

## Unsure about
- None yet.

## For Claude
- Note: `vehicle-ml/external/vehicle-defs` is currently pinned at `v0.31.0`, which predates `vehicle_defs.faults.COMPLAINTS_I18N` and per-fault `complaints` tuples (introduced in `v0.33.0`). Once `vehicle-ml` is repinned to `v0.33.0+`, `templates.py` will automatically consume `COMPLAINTS_I18N` and fault `complaints` without code changes.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
