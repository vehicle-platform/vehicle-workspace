---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-7
repos:
  - vehicle-workspace
  - vehicle-defs
  - vehicle-server
branches:
  - vehicle-workspace:ext/gemini-long-run-7-log
  - vehicle-defs:ext/gemini-visibility-inventory
  - vehicle-defs:ext/gemini-time-sync
  - vehicle-server:ext/gemini-mt-llm-turns
  - vehicle-defs:ext/gemini-cache-round3
  - vehicle-defs:ext/gemini-vss-two-wheeler
prs:
  - https://github.com/vehicle-platform/vehicle-defs/pull/221
  - https://github.com/vehicle-platform/vehicle-defs/pull/222
  - https://github.com/vehicle-platform/vehicle-server/pull/117
  - https://github.com/vehicle-platform/vehicle-defs/pull/223
  - https://github.com/vehicle-platform/vehicle-defs/pull/224
zone: yellow
review: pending
---

# long-run-7 (visibility inventory, time-sync options, cache round 3, marks weak labels, VSS two-wheeler draft)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-7.md` end to end (G7-0, G7-1, G7-2, G7-3a, G7-3b, G7-4, G7-5, G7-9) from up-to-date `main` branches, opening one PR per completed task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes

### G7-0 and G7-9 — Session log (`vehicle-workspace`, `ext/gemini-long-run-7-log`, GREEN)
- `external-ai/log/2026-11-27-gemini-long-run-7.md`: opened at session start (G7-0), updated and pushed after each task, and finalized with all PRs, checks, measurements, skipped task analysis, and Claude follow-ups (G7-9).

### G7-1 — Repository visibility inventory (`vehicle-defs`, `ext/gemini-visibility-inventory`, GREEN, card T76, D-135)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/221
- `docs/ideas/visibility-inventory.md`: inventory-only catalog of vehicle-specific and commercially sensitive files across all 12 platform repos, `vehicle-workspace`, and archived `HondaCl250_Telemetry`, with cited public build/test consumers, **proposed** public replacements (`nothing`, `generic catalog`, or `synthetic example vehicle`), GitHub Free plan constraints (2,000 Actions minutes/month, no rulesets on private repos, public history retention), and 7 open questions for the user. No files moved/deleted/rewritten and no repo settings changed.

### G7-2 — Time synchronisation options (`vehicle-defs`, `ext/gemini-time-sync`, GREEN, Q-008)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/222
- `docs/ideas/time-sync-options.md`: per-node clock/timestamp audit (`rt-core`, `safety-node`, `connectivity-node`, `linux-node`, `vehicle-mobile`, `vehicle-server`) with code citations (`hal_time.h`, `safety_app.h`, `BLETelemetryPacket.h`, `GpsFix.h`, `session_recorder.dart`, `alerts/service.py`, `marks.py`, `series.py`) and `hardware-architecture.md` §5b.8; verified `dbc/platform.dbc` has no time-sync frame today (only 16-bit 1 s heartbeat uptime counters) without inventing any message name or ID; compared four **proposed** options (a) `rt-core` CAN master, (b) GNSS + 1PPS into `rt-core`, (c) Pi 5 `chrony`/NTP + `rt-core`, (d) per-node monotonic + post-ride offset; consumer accuracy table and invariant 1/3/7 constraints. Q-008 remains open.

### G7-3a — Multi-turn dev conversations `mt-11`..`mt-15` (`vehicle-server`, `ext/gemini-mt-llm-turns`, GREEN, card T72)
- PR: https://github.com/vehicle-platform/vehicle-server/pull/117 (commit `d4f283b`)
- `src/vehicle_server/chat/eval/{spec.json,locales/en.json,locales/tr.json}`: appended 5 new 4-turn dev conversations (`mt-11`..`mt-15`, 20 turns per locale) using deterministic `compare_sessions` follow-ups and confirmed displayable `check_symptom` complaints (`ENG-001`, `IGN-003`, `CLU-001`, `LUB-004`, `FDR-003`, `SUS-004`) so turns 2-4 exercise LLM phrasing (`uses_llm == True` on 2-3 turns per conversation, 5 LLM turns on turn 4). No existing items or held-out files touched.
- `tests/test_chat_eval.py`: added `test_mt11_to_mt15_exercise_llm_phrasing_on_at_least_two_turns` verifying all 5 conversations in both `en` and `tr` with `ChatService` + counting fake LLM + fake `ToolRunner`.

### G7-3b — Prompt-cache measurement, round 3 (`vehicle-defs`, `ext/gemini-cache-round3`, YELLOW `needs-claude-review`, card T72)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/223
- `docs/test-results/chat-eval/2026-11-27-multiturn-cache-round3/README.md`, 12 English summary Markdown files (`arm-{a,b}-{en,tr}-run{1,2,3}.md`), 6 English raw JSON files (`arm-{a,b}-en-run{1,2,3}.json`; Turkish raw JSONs were kept in `/tmp` outside git and deleted after aggregation per D-125), plus 1 row appended to `docs/test-results/chat-eval/README.md`.
- Measured Arm A (`-np 1 -c 4096` via `local/run-llama.sh`) vs. Arm B (`-np 2 -c 8192`) on `qwen2.5-1.5b-instruct-q4_k_m.gguf` (`llama-server` `b1b770d`) against `vehicle-server` `ext/gemini-mt-llm-turns` (`d4f283b`) and `vehicle-mcp` `71b1af6`, **restarting `llama-server` fresh before every single run and locale** (12 cold restarts, `mt-01`..`mt-15`, 55 turns/run, 0 request errors).
- **Measured summary:**
  - Cross-run replay confounder eliminated: identical cached token counts across Runs 1–3 (`en` A `6856/19882` `34.5%` vs. B `7199/19882` `36.2%` [`+343` tok/run]; `tr` A `4531/20110` `22.5%` vs. B `4790/20110` `23.8%` [`+259` tok/run]).
  - Turn-4 LLM phrasing now measured (`15` pooled timed Turn-4 turns per arm/locale): identical `15.5%` (`2046/13230`, `en`) and `18.5%` (`2661/14346`, `tr`) in both arms (`0` extra cached tokens from `-np 2`).
  - Consistent TTFT/wall-time improvement from Arm B: **not shown** (Arm A faster in `en`: pooled p50 `1242.8` vs. `1289.7 ms`, wall `59.9–60.7 s` vs. `61.3–62.5 s`; Arm B slightly faster in `tr`: pooled p50 `1393.5` vs. `1421.8 ms`, wall `75.2–77.6 s` vs. `78.7–84.1 s`).

### G7-5 — COVESA VSS two-wheeler draft (`vehicle-defs`, `ext/gemini-vss-two-wheeler`, GREEN, card T74 item 1)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/224
- `docs/ideas/upstream-vss-two-wheeler.md`: draft-only upstream issue (nothing sent outside `vehicle-platform`). Filtered `vss/overlay.vspec` to generic two-wheeler signals (leaving out `IsEcuPresent`, `Nodes.*`, `Validity.*`, and all CL250 DIDs/CAN IDs), verified every candidate directly against official COVESA VSS **`v6.1`** (published 2026-09-17, 1,737 nodes) and `v6.1/units.yaml` (noting `Vehicle.Orientation.Roll` was added in `v6.1` while absent in pinned `v6.0`, whereas two-wheeler branch, side/center stand, and estimator `Quality`/`State` are not found in `v6.1`), and drafted the proposed GitHub issue following COVESA `CONTRIBUTING.md` and `rule_set/basics.md`.

## Skipped / Stopped
- **G7-4 (`vehicle-ml` ride marks weak-label reader, card T65, D-133 item 4) — STOPPED per brief instruction (no PR opened):**
  - Read `vehicle-ml/src/vehicle_ml/{windows.py,dataset.py,data/store.py,evaluate.py}` and `vehicle-server/src/vehicle_server/{marks.py,marks_export.py,series.py,parquet.py}`.
  - The codebase does **not** make the mapping between `Mark.offset_s` (elapsed seconds from UTC `created_utc`) and `Window.start_ms`/`end_ms` (raw MCU `device_time_ms`) unambiguous without guessing. Stopped without implementing `marks.py`, removed the empty local branch in `vehicle-ml`, and recorded the full analysis and options under *For Claude*.

## Result
Five PRs opened across `vehicle-defs` (`#221`, `#222`, `#223` [YELLOW `needs-claude-review`], `#224`) and `vehicle-server` (`#117`), plus this workspace session-log PR; G7-4 intentionally stopped per brief instruction on the time-axis mismatch.

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
- **G7-5 (`vehicle-defs`, `ext/gemini-vss-two-wheeler`):**
  - Verified directly against official COVESA VSS `v6.1` (`vss.yaml`, `units.yaml`), pinned `v6.0` cache, `CONTRIBUTING.md`, and `rule_set/basics.md`.
  - Hygiene scan (no `/Users/`, CL250 DIDs/CAN IDs, or tokens): clean.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **GREEN**.
- **G7-9 (`vehicle-workspace`, `ext/gemini-long-run-7-log`):**
  - `python3 scripts/check_zones.py . --base origin/main`: **GREEN**.

## Unsure about
- **G7-3b server port isolation:** Port `8000` already had an older `vehicle-server serve` process running (started earlier at 17:00), so G7-3b launched a temporary `vehicle-server serve` on local port `8010` from the G7-3a branch (`d4f283b`) with `VEHICLE_CHAT_SELF_URL=http://127.0.0.1:8010` and `VEHICLE_CHAT_RATE_PER_MIN=600` (all other env vars matching `local/run-server.sh`), and shut it down cleanly on completion.
- **G7-3b demo session token refresh:** `local/secrets/mac-local-demo-session.txt` returned 401 on `/assistant/active`, so the benchmark runner logged in via `POST /auth/login` using `local/secrets/mac-local-demo-login.txt` into a temporary `0600` file outside `local/` and called `POST /auth/logout` in `finally` without editing anything under `local/`.
- **G7-2 hardware items marked CONFIRM:** whether the NEO-M8N breakout exposes a 1PPS pin, which NUCLEO-H743ZI2 timer input-capture pin would be wired, and whether a Pi 5 RTC backup battery is installed.

## For Claude
- **G7-4 (`vehicle-ml` marks weak labels, card T65, D-133 item 4) — Time-axis ambiguity (task stopped per brief instruction instead of guessing):**
  - **What `Window.start_ms`/`end_ms` use:** `vehicle-ml/src/vehicle_ml/windows.py:17,81-93,118-121` (`make_windows`) and `dataset.py:42,164-200` (`_session_windows`) place `Window.start_ms` and `Window.end_ms` on the **raw `device_time_ms`** axis of the session's base Parquet kind (`for start in range(int(times[0]), last_start + 1, stride_ms)`). It does **not** subtract a session `t0_ms`, does not unwrap 32-bit `device_time_ms` wraparound, drops `rx_utc` as metadata (`dataset.py:42`), and never attaches `created_utc` or `t0_ms` to `Window`. While `vehicle-ml/tests/{synthetic.py,physics_synthetic.py}` happen to start synthetic `device_time_ms` at `0`, `vehicle-server/src/vehicle_server/parquet.py:57,100` stores raw MCU monotonic `millis()` (e.g. `vehicle-server/tests/make_fixtures.py:272` starts at `5_000` ms, and real hardware boots before recording starts — which is why `vehicle-server/src/vehicle_server/series.py:11-13` explicitly shifts `t_ms = sample_time - t0`). Furthermore, `make_windows` can drop early windows (`gap`, `missing:<channel>`, `rate`), so `min(w.start_ms)` over kept `Window` objects is not guaranteed to equal the session's first `device_time_ms`.
  - **What `Mark.offset_s` uses:** `vehicle-server/src/vehicle_server/marks_export.py:158` computes `offset_s = round((mark.t_utc - start_ms) / 1000.0, 3)` where `start_ms` is the session's UTC `created_utc` from `marks.ride_window_ms` (`vehicle-server/src/vehicle_server/marks.py:173-188`), and `vehicle-mobile/lib/services/session_recorder.dart:436` stamps `created_utc` when recording starts — not `first_packet_utc` (`session_recorder.dart:100`) and not raw `device_time_ms`.
  - **Why guessing would silently break real rides:** Assuming `mark_ms = offset_s * 1000` fails whenever `device_time_ms` does not start at `0`; assuming `t0_ms = min(w.start_ms)` silently shifts every mark whenever early windows were dropped and still ignores `first_packet_utc - created_utc` (and Q-008 clock skew).
  - **Decision needed from Claude before implementing `vehicle-ml/src/vehicle_ml/marks.py`:**
    1. Should `label_windows` take an explicit per-session origin mapping (e.g. `session_origin_ms: Mapping[str, int]` from `SessionStore` raw Parquet `min(device_time_ms)`, optionally adjusted for `first_packet_utc - created_utc`), or
    2. Should `vehicle-ml` (`make_windows` / `Window`) adopt a session-relative `t_ms = device_time_ms - t0` axis (or carry `session_t0_ms` on `Window`) matching `vehicle-server/src/vehicle_server/series.py:11-13`, or
    3. Should `vehicle-server marks export` also emit `device_time_t0_ms` / `first_packet_offset_s` (or anchor `ride_window_ms` on `first_packet_utc` when present)?
- **G7-3b (`vehicle-defs#223`, `needs-claude-review`):** Round 3 confirms keeping `-np 1` (no consistent TTFT win from `-np 2 -c 8192`, and `0` extra cached tokens on Turn 4 because conversation history + tool result sit inside a changing single `user` message). Next hypothesis to test if further prompt-cache optimization is desired: structuring multi-turn history as append-only `user`/`assistant` messages so Turn 2–4 prefix reuse grows beyond the phrasing system prompt (~133–180 tokens).
- **G7-5 (`vehicle-defs#224`):** Checking upstream COVESA VSS `v6.1` revealed that `Vehicle.Orientation.Roll` was added in `v6.1` (absent in our pinned `v6.0`) and `Vehicle.Powertrain.CombustionEngine.TPS` already exists in `v6.0`/`v6.1`. Worth considering when bumping VSS to `v6.1` (D-024) whether `Vehicle.Motorcycle.LeanAngle` and `Vehicle.Motorcycle.ThrottlePosition` should align with those standard paths in a future `/signal-change`.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
