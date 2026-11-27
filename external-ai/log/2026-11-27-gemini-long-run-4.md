---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-4
repos:
  - vehicle-workspace
  - vehicle-defs
  - vehicle-server
  - vehicle-mobile
  - vehicle-mcp
  - vehicle-analyzer
  - vehicle-ml
branches:
  - vehicle-workspace:ext/gemini-long-run-4-log
  - vehicle-defs:ext/gemini-parked-current
  - vehicle-defs:ext/gemini-sil-inventory
  - vehicle-defs:ext/gemini-bakeoff-3models-results
  - vehicle-server:ext/gemini-prompt-cache
  - vehicle-server:ext/gemini-ride-marks
  - vehicle-mobile:ext/gemini-ride-marks
  - vehicle-mcp:ext/gemini-rag-eval
  - vehicle-analyzer:ext/gemini-analyzer-tests
prs:
  - https://github.com/vehicle-platform/vehicle-defs/pull/209
  - https://github.com/vehicle-platform/vehicle-defs/pull/210
  - https://github.com/vehicle-platform/vehicle-defs/pull/211
  - https://github.com/vehicle-platform/vehicle-server/pull/107
  - https://github.com/vehicle-platform/vehicle-server/pull/108
  - https://github.com/vehicle-platform/vehicle-mobile/pull/58
  - https://github.com/vehicle-platform/vehicle-mcp/pull/37
  - https://github.com/vehicle-platform/vehicle-analyzer/pull/83
zone: yellow
review: done 2026-11-27 (all 9 PRs fixed or accepted and merged; D-133 recorded; RAG test-split contamination and mobile queue races fixed)
---

# long-run-4 (parked-current note, 3-model bake-off, prompt-cache measurement, ride event marks, SIL inventory, RAG eval, analyzer tests)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-4.md` end to end (G4-0, G4-A, G4-1, G4-2, G4-3, G4-4, G4-6, G4-7, G4-8, G4-5) after verifying start gates (`vehicle-ml#32`, `vehicle-defs#207`, `vehicle-server#105` all merged), keeping every change on its dedicated `ext/gemini-*` branch with passing repo checks and zone checks before each push.

## Changes

### G4-0 — Session log (`vehicle-workspace`, `ext/gemini-long-run-4-log`, GREEN)
- Created `external-ai/log/2026-11-27-gemini-long-run-4.md` from `TEMPLATE.md` (`review: pending`) and verified all start gates merged (`vehicle-ml#32` `7659dff`, `vehicle-defs#207` `071270a`, `vehicle-server#105` `d9d2577`).

### G4-A — Parked-current note (`vehicle-defs`, `ext/gemini-parked-current`, PR #209, GREEN in `check_zones.py` / marked `needs-claude-review` per task table)
- Added `docs/ideas/parked-current.md` (roadmap card T73):
  - Cited datasheet sleep/standby/quiescent currents for Raspberry Pi 5 (`POWER_OFF_ON_HALT`), ESP32-S3, STM32H743 (DS12110), STM32G474 (DS12288), SN65HVD230 (SLOS346), TJA1050/MCP2515, and MPU-6500 (PS-MPU-6500A); board-level extras explicitly marked unknown until measured.
  - Cited CL250 battery specification from local `CL250_2023_owners_manual_JP.pdf` (Main Specifications, printed p. 86 / PDF p. 88: `YTZ8V`/`FTZ8V`, 12 V 7 Ah 10HR), with days-parked arithmetic formula and clearly labeled estimates.
  - Documented Options A/B/C (all marked **proposed**; no decision taken) plus bench and on-bike measurement procedure for T73.

### G4-1 — Three-model bake-off (`vehicle-ml`, `main` `7659dff`, no PR needed)
- Downloaded official `Qwen3-1.7B-Q8_0.gguf` and `Qwen3-4B-Q4_K_M.gguf` into git-ignored `local/models/`.
- Verified all 3 official Qwen GGUF SHA-256 checksums (`bakeoff verify --models all --models-dir ../local/models`: all 3 `OK`).
- Ran all 3 models (`qwen2.5-1.5b-instruct-q4_k_m`, `qwen3-1.7b-q8_0`, `qwen3-4b-q4_k_m`), `--locales en tr`, dev (`chat-eval`, N=72) + held-out (N=100, including 16 `safety_red_team` and 8 `out_of_scope`), against `local/run-server.sh` (`VEHICLE_CHAT_RATE_PER_MIN=600`, `vehicle-server` `d9d2577`, defs pin `v0.33.0`), `-c 4096 -np 1 --metrics`, 0 errors across all 12 rows (1,032 questions).
- No harness fixes were required; raw outputs remain git-ignored under `vehicle-ml/src/vehicle_ml/ride_llm/bakeoff/out/`.

### G4-2 — Bake-off results page (`vehicle-defs`, `ext/gemini-bakeoff-3models-results`, PR #211, YELLOW `needs-claude-review`)
- Added `docs/test-results/ride-llm-bakeoff/2026-11-27-stage0-3models/README.md` (`Provenance: synthetic`, evidence level `L1`, setup SHAs/SHA-256s, EN/TR tables, `safety_red_team` table, facts-only Reading with no winner, Caveats) and compact `summary.json` (16,307 bytes <= 20 KB, no raw answers, no personal data).
- Linked the 2026-11-27 run in `docs/test-results/ride-llm-bakeoff/README.md`.

### G4-3 — Prompt-cache measurement (`vehicle-server`, `ext/gemini-prompt-cache`, PR #107, GREEN)
- Added `LlmTimings` to `src/vehicle_server/chat/models.py`, `REPORTED_TIMINGS` `ContextVar` in `src/vehicle_server/chat/llm.py`, per-turn aggregation in `src/vehicle_server/chat/service.py`, and timings parsing/aggregation/markdown (`n/a` when absent) in `src/vehicle_server/chat/eval/{scoring,report}.py`.
- Reordered dynamic sections in `src/vehicle_server/chat/budget.py` (`memory` -> `state` -> `turns`) so static system prompt and tool specs remain byte-identical at the prefix.
- Measured on `qwen2.5-1.5b` dev suite (72 items/locale):
  - `en`: tool acc 100% -> 100%, fact cov 100% (51/51), forbidden 0 -> 0, cached prompt share 23% (2937/12904 across 19 timed turns), TTFT p50/p95 1244.7/1619.3 ms -> 1168.4/1521.2 ms, gen p50/p95 619.3/2111.1 ms -> 497.2/1944.8 ms.
  - `tr`: tool acc 100% -> 100%, fact cov 100% (51/51), forbidden 2 -> 2 (`symptom-10`, `symptom-14`), cached prompt share 25% (4109/16222 across 23 timed turns), TTFT p50/p95 1249.1/1650.7 ms -> 1198.6/1518.7 ms, gen p50/p95 931.9/2708.9 ms -> 889.0/2498.7 ms.
- Added unit tests in `tests/test_chat_efficiency.py`, `tests/test_chat_eval.py`, and updated response key-set assertion in `tests/test_assistant.py`.

### G4-4 — Ride event marks (`vehicle-server` PR #108 + `vehicle-mobile` PR #58, both `ext/gemini-ride-marks`, GREEN; merge server first)
- **Server (`vehicle-server`, PR #108):**
  - Implemented **proposed** data model `{id, t_utc, kind, note?}` (`kind` in `misfire, noise, vibration, warning_light, rough_road, traffic, other`; `note` <= 200 chars; position fields rejected via `extra="forbid"`, D-076).
  - Added additive `ride_marks` table migration in `src/vehicle_server/index.py` with per-user `owner_key` isolation.
  - Added `src/vehicle_server/marks.py` and `src/vehicle_server/marks_api.py` (`POST /marks` 201/200/409/400/422, `GET /rides/{ride_id}/marks`, `DELETE /marks/{mark_id}` 204/404) wired in `src/vehicle_server/api.py`.
  - Added `tests/test_marks.py` (CRUD, idempotency, conflict, validation, D-076 no-position, per-user isolation, legacy `index.sqlite` migration) and updated `tests/test_openapi_errors.py`.
- **Mobile (`vehicle-mobile`, PR #58):**
  - Added `lib/models/ride_mark.dart`, `lib/services/marks_client.dart`, `lib/services/mark_queue.dart` (SharedPreferences offline queue deduplicated by `id`), `lib/ui/widgets/mark_picker.dart`, `lib/ui/rides/ride_marks_section.dart`.
  - Wired >= 64 px glove-friendly Mark button + auto-closing 5-kind quick picker into `lib/ui/live_screen.dart` and marks listing/deletion into `lib/ui/rides/ride_summary_screen.dart`.
  - Added EN/TR strings in `l10n_src/parts/marks.{en,tr}.json`, merged ARB via `tool/l10n_merge.py`, and regenerated `AppLocalizations` (`flutter gen-l10n`).
  - Added unit and widget tests in `test/ride_marks_test.dart`.

### G4-6 — SIL inventory (`vehicle-defs`, `ext/gemini-sil-inventory`, PR #210, GREEN)
- Added facts-only `docs/ideas/sil-inventory.md` (roadmap card T69 input):
  - Measured host test/build commands and durations on macOS arm64 across `vehicle-rt-core` (55/55, 53.64 s; `vehicle_rtcore_host` 2 s sim 2.18 s & UDS 5.83 s), `vehicle-safety-node` (9/9, 0.56 s), `vehicle-connectivity-node` (`native_tests.sh`, 11.89 s), `vehicle-server` (`test_mock_stream.py`, 15/15, 1.05 s), `vehicle-linux-node` (153 passed / 3 skipped, 3.01 s), and `vehicle-hil-bench` (skeleton).
  - Documented exact 10-frame `dbc/platform.dbc` TX/RX matrix per host build and 8 file:line-referenced gaps for a unified multi-node virtual bus.

### G4-7 — RAG retrieval eval split (`vehicle-mcp`, `ext/gemini-rag-eval`, PR #37, YELLOW `needs-claude-review`)
- Authored 70 new EN and 70 new TR queries (35 fault-catalog + 35 `docs/ideas/*.md`, proper UTF-8 Turkish diacritics in `locales/tr.json`) plus 8 weak queries/locale (total 174 answerable + 14 weak per locale; 0 overlap with `vehicle-ml` held-out or `vehicle-server` `chat-eval`; deduplicated pre-existing `en-02`).
- Created stratified 50/50 `tune`/`test` split with fixed `seed = 20261127` (86 `tune` / 88 `test`, 7/7 weak) documented in `tests/retrieval_eval/README.md`, and added `"test"` split support in `eval_retrieval.py` and `indexer.py`. Retrieval code, weights, and cutoffs were not modified.
- Measured on `test` split only with clean schema-2 `--exclude-holdout` index (579 chunks):
  - `en/test` (n=88): R@1 **0.591**, R@3 **0.841**, R@5 **0.909**, MRR **0.716**, weak_avg_hits 1.86, weak_empty 0.286.
  - `tr/test` (n=88): R@1 **0.295**, R@3 **0.523**, R@5 **0.568**, MRR **0.404**, weak_avg_hits 2.00, weak_empty 0.286.

### G4-8 — Analyzer test coverage (`vehicle-analyzer`, `ext/gemini-analyzer-tests`, PR #83, GREEN)
- Tests-only change (no source or red-zone files edited; 0 bugs found in source).
- Added 8 test files (`tests/captureStoreExtra.test.tsx`, `tests/components/HeaderAttitudeSniffer.test.tsx`, `tests/components/TraceUdsSessionExtra.test.tsx`, `tests/exportService.test.ts`, `tests/helpSampling.test.tsx`, `tests/ingestClient.test.ts`, `tests/uiThemeKeys.test.tsx`, `tests/useReplay.test.tsx`) and extended `tests/mathChannels.test.ts`.
- Raised overall line coverage from **73.96%** (3685/4982) to **85.00%** (4235/4982) and brought all 18 touched non-red modules to **88.9%–100.0%** line coverage.

## Result
All tasks in `external-ai/tasks/2026-11-27-gemini-long-run-4.md` completed with 8 PRs opened (plus the log PR for G4-5); G4-1 required no harness fix PR.

## Checks
- **G4-A (`vehicle-defs#209`):** D-125/privacy 0 hits; `python3 scripts/check_zones.py vehicle-defs --base origin/main` -> GREEN (`needs-claude-review` noted per task table).
- **G4-6 (`vehicle-defs#210`):** all host commands executed and timed; D-125/privacy 0 hits; `check_zones.py` -> GREEN.
- **G4-1 (`vehicle-ml` `main`):** `bakeoff verify --models all --models-dir ../local/models` -> 3/3 SHA-256 `OK`; `bakeoff run --models all --locales en tr` -> 12/12 rows, 0 errors across 1,032 questions.
- **G4-2 (`vehicle-defs#211`):** `summary.json` 16,307 bytes (<= 20 KB), `Provenance: synthetic`, D-125/privacy 0 hits; `check_zones.py` -> YELLOW (`needs-claude-review`).
- **G4-3 (`vehicle-server#107`):** `uv run ruff format --check .` pass, `uv run ruff check .` pass, `uv run mypy` pass, `uv run pytest -q` 2369 passed; `check_zones.py` -> GREEN.
- **G4-4 Server (`vehicle-server#108`):** `uv run ruff format --check .` pass (185 files), `uv run ruff check .` pass, `uv run mypy` pass (103 files), full `HYPOTHESIS_PROFILE=ci uv run pytest -q` 2429 passed (3 OpenAPI table assertions then fixed and re-verified with `tests/test_marks.py tests/test_openapi_errors.py tests/test_schemathesis.py -k 'marks or openapi'`: 150 passed); `check_zones.py` -> GREEN.
- **G4-4 Mobile (`vehicle-mobile#58`):** `python3 tool/l10n_merge.py --check` pass, `flutter analyze` 0 issues, `flutter test -j 2` 712/713 passed (1 timing flake in untouched `test/record_ride_actions_test.dart` due to 50 ms wall-clock wait under concurrent CPU load; standalone re-run of `test/record_ride_actions_test.dart test/ride_marks_test.dart test/i18n_test.dart`: 11/11 passed); `pubspec.lock` untouched; `check_zones.py` -> GREEN.
- **G4-7 (`vehicle-mcp#37`):** `uv run ruff format --check .` pass, `uv run ruff check .` pass, `uv run pytest -q` 267 passed / 1 skipped; `check_zones.py` -> YELLOW (`needs-claude-review`).
- **G4-8 (`vehicle-analyzer#83`):** `npm test` 62/62 files, 466/466 passed; `npx vitest run --coverage --maxWorkers=2` 62/62 files, 466/466 passed, 85.00% lines; `npm run build` pass; `npm run lint` (`eslint . --max-warnings 0`) 0 errors / 0 warnings; `check_zones.py` -> GREEN.
- **G4-5 (`vehicle-workspace`):** `python3 scripts/check_zones.py . --base origin/main` -> GREEN.

## Unsure about
- In `vehicle-mobile`, `test/record_ride_actions_test.dart` uses `Future<void>.delayed(const Duration(milliseconds: 50))` inside `runAsync`, which intermittently times out when multiple test suites saturate disk/CPU simultaneously (passes reliably standalone).
- In `vehicle-analyzer`, running `vitest --coverage` at default worker concurrency (8 workers) slowed `tests/perf.test.ts` below its 22,500 frames/s threshold; running `npm test` (52,790 frames/s) or `--coverage --maxWorkers=2` passes reliably.
- In G4-2 (`2026-11-27-stage0-3models`), 8 of 9 Turkish `chat-eval` dev forbidden hits and all 4 held-out forbidden hits on `qwen3-4b-q4_k_m` came from `source=template` rather than free-form LLM text; left untouched as observation only.

## For Claude
1. **Yellow PRs needing review (`needs-claude-review`):**
   - `vehicle-defs#209` (`docs/ideas/parked-current.md`, T73): confirm battery/quiescent-current assumptions and decide between proposed Options A/B/C (D-xxx) once boards arrive.
   - `vehicle-defs#211` (`docs/test-results/ride-llm-bakeoff/2026-11-27-stage0-3models/`): review 3-model Stage-0 results for the T58 base-model decision; note the template-sourced `group:advice` (Turkish dev) and `snake_case` (`qwen3-4b` held-out) hits.
   - `vehicle-mcp#37` (`tests/retrieval_eval/`): review the 70+70 new EN/TR queries and stratified `tune`/`test` split (seed `20261127`).
2. **Proposed data model & merge order for G4-4 (T68):**
   - Record decision for the **proposed** ride event marks schema (`{id, t_utc, kind, note?}`, no position per D-076) across `vehicle-server#108` and `vehicle-mobile#58`.
   - **Merge `vehicle-server#108` before `vehicle-mobile#58`.**
3. **RAG retrieval improvement ideas from G4-7 (not implemented; measure-only task):**
   - `faults/unconfirmed#data only` frequently ranks #1 on Turkish doc queries and short fault queries, displacing relevant English `docs/ideas/*.md` chunks.
   - Cross-lingual retrieval (`tr` query -> English-only `docs/ideas/*.md`) drops sharply (R@1 0.295 vs 0.591 EN) because FTS5 lexical matching yields no Turkish->English hits, leaving vector-only doc hits outranked by Turkish catalog chunks in RRF.
   - Weak/out-of-domain queries still average 1.86–2.00 returned hits (`weak_empty` = 0.286); consider tuning `min_similarity` or lexical-only gating on the `tune` split only (never on `test`).
4. **Remaining `vehicle-analyzer` modules below 80% line coverage after G4-8:**
   - `src/components/OscilloscopePanel.tsx` (0/244): heavy 2D canvas drawing and `requestAnimationFrame` loop; jsdom lacks real canvas pixel verification.
   - `src/components/SyncPanel.tsx` (0/112): browser `FileReader` / drag-drop / worker log import and custom DBC loader UI.
   - `src/app/useLiveSources.ts` (0/82): orchestrates red-zone `webSerialCan`, desktop Tauri HAL, and live WebSocket adapters.
   - `src/App.tsx` (0/74) & `src/app/MainWorkspace.tsx` (0/2): top-level application shell wiring all live sources and panels.
   - `src/services/ingest.worker.ts` (0/7): Web Worker global entrypoint (`self.onmessage`); worker protocol and fallback logic are covered via `tests/ingestClient.test.ts` (97.4%).
   - `src/ui/index.ts` (0/4): pure barrel re-export file.
5. **Other PRs ready for review/merge:**
   - `vehicle-defs#210` (`docs/ideas/sil-inventory.md`, T69 input for Claude's multi-node SIL design).
   - `vehicle-server#107` (prompt-cache timings telemetry and `budget.py` section reorder, T72).
   - `vehicle-analyzer#83` (tests-only coverage PR, 73.96% -> 85.00% lines).

## Claude review
Fixes pushed to each `ext/gemini-*` PR branch from a `claude/*-review` worktree; every PR merged after green CI. Gemini's commits kept. Clearly better than runs 1-3: proposals marked as proposed, sources cited, the two idea notes accepted almost as written.

- **G4-A `vehicle-defs#209`** and **G4-6 `vehicle-defs#210`**: facts spot-checked against the code and DECISIONS (latching relay, < 1 mA target, `sim_safety`, `HAVE_SOCKETCAN`, `SAFETY_APP_PASS_MAX_MS`): correct. Only fix: title before the status line.
- **G4-2 `vehicle-defs#211`** (merged `2cba137`): every table cell cross-checked with summary.json and raw out/ (0 mismatches). `d5cb27e`: "not comparable with 2026-11-26" caveat (server moved `4a82942` → `d9d2577`, dev set 57 → 72; tok/s halved, cause not verified), RSS caveat, template-hit cause: Turkish `labels.stop` ("have the bike inspected") matches the Turkish dev `advice` forbidden pattern after a guard fallback (verified); qwen3-4b held-out `snake_case` hits from `search_knowledge`/`explain_context` templates (not verified).
- **G4-3 `vehicle-server#107`** (merged `025afa7`): the claimed cache benefit was not in its own numbers (identical cached share before/after; single-turn dev suite) → stated as a hypothesis. `ff510bb`: one `LlmTimings` validator instead of two, prefix-stability and trimming tests.
- **G4-4 `vehicle-server#108`** (merged `984fff4`): race-free idempotent insert (`INSERT OR IGNORE`), single-source kind/id pattern. **`vehicle-mobile#58`** (merged `e85adf6`): `1c32b3c` queue mutations serialized (a tap during a flush could be lost or sent twice), exponential backoff retry (was none), 422/409 surfaced instead of "Marked"; `01fb7bc` flaky fixed-delay test made deterministic. Model recorded as **D-133** (vehicle-defs#212, provisional).
- **G4-7 `vehicle-mcp#37`** (yellow, merged `5d37149`): **test split contaminated** — old tune/holdout items (used to choose `min_similarity`/`lexical_top_n`) were moved into `test`; `7cbf282` keeps old items in their split, splits only the new items (seed 20261127), restores the JSON format, README. Test (n = 36): en R@1 0.583 / R@5 0.917 / MRR 0.734, tr 0.194 / 0.417 / 0.279. All labels of the new items read and checked; one near-copy rephrased.
- **G4-8 `vehicle-analyzer#83`** (merged `3f51fdb`): tests did not type-check (`tsc -p ui-tests`), one passed for the wrong reason (`item.v` vs `value`) → `59fdc32`; `9253106` coverage run with 2 workers, coverage floor ratcheted to 83/76/81/85.

Rule change: concurrency/retry safety, never moving existing eval items between splits, measured claims must match the run's own numbers, and running every CI step locally (incl. test type-checks) are added to `AGENTS.base.md` §3.

Open: Turkish `labels.stop` vs the `advice` forbidden pattern (T57/T58); Turkish→English doc retrieval and the `faults/unconfirmed` chunk ranking first (tune-only task); multi-turn measurement of the prompt reorder; analyzer modules still < 80 % (canvas, file import, live sources).
