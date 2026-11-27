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
prs:
  - https://github.com/vehicle-platform/vehicle-defs/pull/221
  - https://github.com/vehicle-platform/vehicle-defs/pull/222
  - https://github.com/vehicle-platform/vehicle-server/pull/117
  - https://github.com/vehicle-platform/vehicle-defs/pull/223
zone: yellow
review: pending
---

# long-run-7 (visibility inventory, time-sync options, cache round 3, marks weak labels, VSS two-wheeler draft)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-7.md` end to end (G7-0, G7-1, G7-2, G7-3a, G7-3b, G7-4, G7-5, G7-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes

### G7-0 and G7-9 — Session log (`vehicle-workspace`, `ext/gemini-long-run-7-log`, GREEN)
- `external-ai/log/2026-11-27-gemini-long-run-7.md`: opened at session start (G7-0) and updated after each task.

### G7-1 — Repository visibility inventory (`vehicle-defs`, `ext/gemini-visibility-inventory`, GREEN, card T76, D-135)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/221
- `docs/ideas/visibility-inventory.md`: inventory-only catalog of vehicle-specific and commercially sensitive files across all 12 platform repos, `vehicle-workspace`, and archived `HondaCl250_Telemetry`, with cited public build/test consumers, **proposed** public replacements (`nothing`, `generic catalog`, or `synthetic example vehicle`), GitHub Free plan constraints (2,000 Actions minutes/month, no rulesets on private repos, public history retention), and 7 open questions for the user. No files moved/deleted/rewritten and no repo settings changed.

### G7-2 — Time synchronisation options (`vehicle-defs`, `ext/gemini-time-sync`, GREEN, Q-008)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/222
- `docs/ideas/time-sync-options.md`: per-node clock/timestamp audit (`rt-core`, `safety-node`, `connectivity-node`, `linux-node`, `vehicle-mobile`, `vehicle-server`) with code and `hardware-architecture.md` §5b.8 citations; verified `dbc/platform.dbc` has no time-sync frame today (only 16-bit 1 s heartbeat uptime counters); compared four **proposed** options (a) `rt-core` CAN master, (b) GNSS + 1PPS into `rt-core`, (c) Pi 5 `chrony`/NTP + `rt-core`, (d) per-node monotonic + post-ride offset; consumer accuracy table and invariant 1/3/7 constraints. Q-008 remains open.

### G7-3a — Multi-turn dev conversations `mt-11`..`mt-15` (`vehicle-server`, `ext/gemini-mt-llm-turns`, GREEN, card T72)
- PR: https://github.com/vehicle-platform/vehicle-server/pull/117 (commit `d4f283b`)
- `src/vehicle_server/chat/eval/{spec.json,locales/en.json,locales/tr.json}`: appended 5 new 4-turn dev conversations (`mt-11`..`mt-15`, 20 turns per locale) using deterministic `compare_sessions` follow-ups and confirmed displayable `check_symptom` complaints (`ENG-001`, `IGN-003`, `CLU-001`, `LUB-004`, `FDR-003`, `SUS-004`) so turns 2-4 exercise LLM phrasing (`uses_llm == True` on 2-3 turns per conversation, 5 LLM turns on turn 4). No existing items or held-out files touched.
- `tests/test_chat_eval.py`: added `test_mt11_to_mt15_exercise_llm_phrasing_on_at_least_two_turns` verifying all 5 conversations in both `en` and `tr` with `ChatService` + counting fake LLM + fake `ToolRunner`.

### G7-3b — Prompt-cache measurement, round 3 (`vehicle-defs`, `ext/gemini-cache-round3`, YELLOW `needs-claude-review`, card T72)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/223
- `docs/test-results/chat-eval/2026-11-27-multiturn-cache-round3/README.md`, 12 English summary Markdown files (`arm-{a,b}-{en,tr}-run{1,2,3}.md`), 6 English raw JSON files (`arm-{a,b}-en-run{1,2,3}.json`; Turkish raw JSON kept in `/tmp` outside git and deleted after aggregation per D-125), plus 1 row appended to `docs/test-results/chat-eval/README.md`.
- Measured Arm A (`-np 1 -c 4096` via `local/run-llama.sh`) vs. Arm B (`-np 2 -c 8192`) on `qwen2.5-1.5b-instruct-q4_k_m.gguf` (`llama-server` `b1b770d`) against `vehicle-server` `ext/gemini-mt-llm-turns` (`d4f283b`) and `vehicle-mcp` `71b1af6`, **restarting `llama-server` fresh before every single run and locale** (12 cold starts, `mt-01`..`mt-15`, 55 turns/run, 0 request errors).
- **Measured summary:** cross-run replay eliminated (identical cached counts across runs 1-3: `en` A `6856/19882` `34.5%` vs. B `7199/19882` `36.2%`, `tr` A `4531/20110` `22.5%` vs. B `4790/20110` `23.8%`); Turn-4 LLM phrasing now measured (`15` pooled timed Turn-4 turns per arm/locale, identical `15.5%` `en` / `18.5%` `tr` in both arms, `0` extra cached tokens from `-np 2`); consistent TTFT/wall-time improvement from Arm B **not shown** (Arm A faster in `en`: p50 `1242.8` vs `1289.7 ms`, wall `59.9–60.7 s` vs `61.3–62.5 s`; Arm B slightly faster in `tr`: p50 `1393.5` vs `1421.8 ms`, wall `75.2–77.6 s` vs `78.7–84.1 s`).

## Result
(In progress.)

## Checks
- **G7-0 (`vehicle-workspace`, `ext/gemini-long-run-7-log`):** `python3 scripts/check_zones.py . --base origin/main` -> **GREEN**.
- **G7-1 (`vehicle-defs`, `ext/gemini-visibility-inventory`):**
  - Hygiene scan (no `/Users/`, usernames, tokens): clean.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **GREEN**.
- **G7-2 (`vehicle-defs`, `ext/gemini-time-sync`):**
  - Verified `faults/alert_rules.yaml` `sustain_s` (5-60 s), `uds/vehicle_cl250.yaml` `VEHICLE_SPEED` (`poll_period_ms: 110`, `stale_after_ms: 300`), and `dbc/platform.dbc` messages.
  - Hygiene scan: clean.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **GREEN**.
- **G7-3a (`vehicle-server`, `ext/gemini-mt-llm-turns`):**
  - `uv run ruff check .`: passed.
  - `uv run ruff format --check .`: passed (188 files).
  - `uv run mypy`: passed (104 source files).
  - `HYPOTHESIS_PROFILE=ci uv run pytest -q --cov --cov-report=term-missing`: 2484/2484 pre-existing tests passed (94% coverage); after fixing fake runner schema in the new test, `uv run pytest -q -m "not fuzz" --cov --cov-report=term-missing` passed (**2383 passed**, 103 fuzz deselected, 94% coverage).
  - `python3 scripts/check_zones.py vehicle-server --base origin/main`: **GREEN**.
- **G7-3b (`vehicle-defs`, `ext/gemini-cache-round3`):**
  - 12 cold-restarted `vehicle-server chat-eval` runs (`en`/`tr` x 3 runs x Arms A/B, `mt-01`..`mt-15`): 12/12 exited 0, 0 request errors, 20/20 tool accuracy on `mt-11`..`mt-15` in both locales.
  - Hygiene scan (no `/Users/`, usernames, Bearer tokens, or Turkish raw JSONs): clean.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **YELLOW** (`needs-claude-review`).

## Unsure about
(None yet.)

## For Claude
(None yet.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
