---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-6
repos:
  - vehicle-workspace
  - vehicle-defs
  - vehicle-server
  - vehicle-analyzer
  - vehicle-mcp
branches:
  - vehicle-workspace:ext/gemini-long-run-6-log
  - vehicle-defs:ext/gemini-cache-round2
  - vehicle-server:ext/gemini-chat-marks
  - vehicle-server:ext/gemini-marks-export
  - vehicle-defs:ext/gemini-multi-node-sil
  - vehicle-analyzer:ext/gemini-analyzer-tests-3
  - vehicle-mcp:ext/gemini-mcp-labels
prs:
  - https://github.com/vehicle-platform/vehicle-defs/pull/219
  - https://github.com/vehicle-platform/vehicle-server/pull/113
  - https://github.com/vehicle-platform/vehicle-server/pull/114
  - https://github.com/vehicle-platform/vehicle-defs/pull/218
  - https://github.com/vehicle-platform/vehicle-analyzer/pull/87
  - https://github.com/vehicle-platform/vehicle-mcp/pull/41
zone: yellow
review: done 2026-11-27 (all 6 PRs merge after Claude fixes: defs#218/#219, server#113/#114, mcp#41, analyzer#87; follow-up server#115)
---

# long-run-6 (cache measurement round 2, marks in the assistant, marks label export, multi-node SIL note, analyzer tests, rider-facing labels)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-6.md` end to end (G6-0 through G6-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes

### G6-0 and G6-9 — Session log (`vehicle-workspace`, `ext/gemini-long-run-6-log`, GREEN)
- `external-ai/log/2026-11-27-gemini-long-run-6.md`: opened at session start (G6-0) and finalized with all PRs, checks, measurements, and Claude follow-ups (G6-9).

### G6-1 — Multi-turn prompt-cache measurement, round 2 (`vehicle-defs`, `ext/gemini-cache-round2`, YELLOW `needs-claude-review`, T72)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/219
- Prerequisite (`vehicle-server#110` on `vehicle-server/main`) merged mid-session (`vehicle-server` `main` at `e5837a5`), so G6-1 was executed in full.
- `docs/test-results/chat-eval/2026-11-27-multiturn-cache-round2/README.md`: `Provenance: synthetic`, exact commands and versions (`vehicle-server` `e5837a5`, `vehicle-mcp` `853c012`, `llama-server` commit `b1b770d`, `qwen2.5-1.5b-instruct-q4_k_m.gguf`), Step 1 audit of `llama-server` calls per `/chat` turn and `timings` aggregation (`chat/service.py`, `llm.py`, `planner.py`, `wiring.py`, `providers/{openai_compat,factory}.py`), per-run cold/warm summary, pooled 3-run per-turn tables (`n`, LLM-timed `n`, cached share, `prompt_ms` p50/p95), and evidence-backed findings.
- `docs/test-results/chat-eval/2026-11-27-multiturn-cache-round2/arm-{a,b}-{en,tr}-run{1,2,3}.md` (12 English aggregate summary files, no raw answers) and `arm-{a,b}-en-run{1,2,3}.json` (6 English raw JSON files; Turkish raw JSON was kept outside the repo and deleted per D-125).
- `docs/test-results/chat-eval/README.md`: appended one row to the Runs table without removing existing content.
- **Measured summary:**
  - All 12 runs completed with `0` request errors (`35` turns/run, `105` turns pooled per arm and locale).
  - Cold Run 1 phrasing-prefix retention: Arm B (`-np 2 -c 8192`) cached `+254` more tokens in `en` (`59.1%` vs `56.4%`, `n=14` timed) and `+262` more tokens in `tr` (`35.8%` vs `32.8%`, `n=11` timed) during alternating tool-choice (`~560` tok) and phrasing (`~133–134` tok) calls.
  - TTFT (`prompt_ms`) improvement from Arm B: **not shown** — Arm B did not lower `prompt_ms` p50/p95 in Run 1 (`en` p50 `122.5` vs `123.8 ms`, p95 `1671.8` vs `1598.5 ms`; `tr` p50 `1265.3` vs `1198.3 ms`, p95 `1820.0` vs `1669.7 ms`) and was slower in warm Runs 2–3 (`en` p50 `93.2–93.8` vs `75.2–75.3 ms`; `tr` p50 `52.7–59.3` vs `34.8–40.2 ms`) and in wall time on all 12 runs.
  - Warm Runs 2–3 confounder: both arms reached identical `95.9%` (`8881/9259`, `en`) and `95.1%` (`8087/8507`, `tr`) cached share because `llama-server` retains evicted prompt checkpoints across repeated identical runs (`prompt_n=1` on repeated phrasing calls).
  - Turn-4 caching: **not shown** (`LLM-timed n = 0` on turn 4 across all 12 runs because all 5 turn-4 items resolve deterministically).

### G6-2 — Ride marks in the rider assistant (`vehicle-server`, `ext/gemini-chat-marks`, GREEN, D-133 item 4, T65)
- PR: https://github.com/vehicle-platform/vehicle-server/pull/113
- `src/vehicle_server/chat/locales/{en,tr}.json`: added `routes.marks`, `answers.mark_kinds` (all 7 D-133 kinds + neutral `unknown`), `answers.marks_*` templates, `followups.cue` (`"and did"` in `en`), and `chips.about_marks`.
- `src/vehicle_server/chat/router.py`, `followup.py`, `chips.py`, `toolcache.py`: routed marks questions (with explicit `session_id` extraction and clean fallback when `get_ride_marks` is absent from an older MCP server), added follow-up refocus (`"marks"`), added ride-bound marks chips, and added `"get_ride_marks"` to `NEVER_CACHED`.
- `src/vehicle_server/chat/answers.py`: `uses_llm` always returns `False` for `get_ride_marks`; added template-only rendering with full per-kind counts from `values`, up to 5 marks formatted as `"offset — kind"` via `rider_text.format_duration`, quoted notes truncated to `<= 80` chars with control characters stripped, neutral label for unknown kinds, and separate zero-marks/`truncated`/`warnings` sentences.
- `src/vehicle_server/chat/eval/{spec.json,locales/en.json,locales/tr.json}`: appended 7 new dev items (`marks-1`..`marks-7`) per locale without modifying existing `mt-01..mt-10` or held-out items.
- `tests/test_chat_marks.py`: full routing, template, injection-quoting/truncation, unknown kind, missing-tool fallback, follow-up, and end-to-end `ChatService` tests confirming LLM is never called.

### G6-3 — Marks label export CLI (`vehicle-server`, `ext/gemini-marks-export`, GREEN, D-133 item 4, T65)
- PR: https://github.com/vehicle-platform/vehicle-server/pull/114
- `src/vehicle_server/marks_export.py` and `src/vehicle_server/cli.py`: added proposed CLI `vehicle-server marks export --out <file.jsonl> [--owner <principal>] [--from <date>] [--to <date>] [--include-notes]`. Reuses `marks.ride_window_ms` and `ride_summary.parse_utc_bound`, opens `index.sqlite` read-only (`?mode=ro`), excludes rider notes by default, never emits position or `owner` tokens, counts outside-window marks on stderr, writes output atomically, and exits `1` on bad/inverted dates or unreadable data dirs/DBs.
- `README.md`: added CLI entry and a short "Marks export (proposed)" section without removing existing content.
- `tests/test_marks_export.py`: unit and CLI tests covering inclusive window bounds, outside-window stderr counts, notes default vs `--include-notes`, `--owner`/`--from`/`--to`, empty store, legacy DB without `ride_marks`, bad/inverted dates, unreadable/missing data dir, corrupt DB, and missing output dir.

### G6-4 — Multi-node SIL design note (`vehicle-defs`, `ext/gemini-multi-node-sil`, GREEN, T69)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/218
- `docs/ideas/multi-node-sil.md`: proposed multi-node SIL design grounded in `docs/ideas/sil-inventory.md`, `dbc/platform.dbc`, `vehicle-rt-core/src/hal/host/`, `vehicle-safety-node/src/hal/host/`, `vehicle-hil-bench`, and `vehicle-server`. Covers Linux `vcan` vs macOS in-process/UDP transport, exact platform-bus message names and producers/consumers from `dbc/platform.dbc`, `Q-008` time-base options left open, scenario startup/verdict reuse, CI cost, and gaps. All design choices marked **proposed**.

### G6-5 — Analyzer tests, third pass (`vehicle-analyzer`, `ext/gemini-analyzer-tests-3`, GREEN)
- PR: https://github.com/vehicle-platform/vehicle-analyzer/pull/87
- `tests/components/OscilloscopePanel.test.tsx`, `tests/components/App.test.tsx`, `tests/ingestWorker.test.ts`: behavioral tests strictly under `tests/` (zero `src/` edits, no threshold changes in `vite.config.ts`) covering all 5 modules previously under 80% lines (`OscilloscopePanel.tsx` 0.00% -> 98.77%, `App.tsx` 0.00% -> 86.49%, `ingest.worker.ts` 0.00% -> 100.00%, `ui/index.ts` 0.00% -> 100.00%, `MainWorkspace.tsx` 0.00% -> 100.00%). Overall lines: 88.77% -> **95.36%** (0 modules remaining under 80% lines).

### G6-6 — No internal identifiers in rider-facing MCP tool output (`vehicle-mcp`, `ext/gemini-mcp-labels`, YELLOW `needs-claude-review`, T58 follow-up)
- PR: https://github.com/vehicle-platform/vehicle-mcp/pull/41
- `src/vehicle_mcp/matching.py`, `tools.py`, `knowledge/sources.py`: added reusable `slug_name()` / `human_label()`, humanized `_symptom_summary`, removed raw tool names (`get_data_card`, `list_fault_catalog`) from `check_symptom` `reason` text, and populated humanized `Chunk.display` + `citation.title` while leaving `Chunk.text` untouched (preserving retrieval, ranking, cutoffs, and RAG eval splits).
- `tests/test_rider_labels.py`, `tests/test_faults.py`, `tests/test_knowledge.py`: executes all 15 registered MCP tools on fixtures and asserts zero `\b[a-z]+(?:_[a-z0-9]+)+\b` or `did.`/`sensor.` leaks across `RIDER_TEXT_FIELDS` with explicit `EXEMPT_FIELDS`.

## Skipped
- None (all tasks G6-0 through G6-6 and G6-9 completed).

## Checks
- **G6-1 (`vehicle-defs`, `ext/gemini-cache-round2`):**
  - 12 `vehicle-server chat-eval` runs (`en`/`tr` x 3 runs x Arms A/B): 12/12 exited 0, 0 request errors.
  - Hygiene scan (`grep` for `/Users/`, usernames, tokens, secrets): clean.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **YELLOW** (`docs/test-results/*`, PR marked `needs-claude-review`).
- **G6-2 (`vehicle-server`, `ext/gemini-chat-marks`):**
  - `uv run ruff check .`: passed.
  - `uv run ruff format --check .`: passed (186 files).
  - `uv run mypy`: passed (103 source files).
  - `HYPOTHESIS_PROFILE=ci uv run pytest -q --cov --cov-report=term-missing`: **2474 passed**, 94% coverage.
  - `python3 scripts/check_zones.py vehicle-server --base origin/main`: **GREEN**.
- **G6-3 (`vehicle-server`, `ext/gemini-marks-export`):**
  - `uv run ruff check .`: passed.
  - `uv run ruff format --check .`: passed (187 files).
  - `uv run mypy`: passed (104 source files).
  - `HYPOTHESIS_PROFILE=ci uv run pytest -q --cov --cov-report=term-missing`: **2457 passed**, 94% coverage (`marks_export.py` 91%).
  - `python3 scripts/check_zones.py vehicle-server --base origin/main`: **GREEN**.
- **G6-4 (`vehicle-defs`, `ext/gemini-multi-node-sil`):**
  - Facts cross-checked against `sil-inventory.md`, `dbc/platform.dbc`, and host HAL sources.
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: **GREEN**.
- **G6-5 (`vehicle-analyzer`, `ext/gemini-analyzer-tests-3`):**
  - `npx tsc -p tests/tsconfig.json --noEmit`: passed.
  - `npx tsc -p ui-tests/tsconfig.json --noEmit`: passed.
  - `npm run lint` (`eslint . --max-warnings 0`): passed.
  - `npm run test:coverage`: **67 files / 485 tests passed** (Statements 92.86%, Branches 83.82%, Functions 91.90%, Lines **95.36%**, 0 modules under 80% lines).
  - `npm run build` (`tsc -b && vite build`): passed.
  - `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: **GREEN**.
- **G6-6 (`vehicle-mcp`, `ext/gemini-mcp-labels`):**
  - `uv run ruff check .`: passed.
  - `uv run ruff format --check .`: passed.
  - `uv run mypy`: passed (22 source files).
  - `uv run pytest -q --cov --cov-report=term-missing`: **280 passed, 1 skipped**, 94.26% coverage (floor 91.0%).
  - `python3 scripts/check_zones.py vehicle-mcp --base origin/main`: **YELLOW** (PR marked `needs-claude-review`).
- **G6-9 (`vehicle-workspace`, `ext/gemini-long-run-6-log`):**
  - `python3 scripts/check_zones.py . --base origin/main`: **GREEN**.

## Unsure about
- **G6-1 zone classification:** the task table listed `vehicle-defs` `docs/test-results/chat-eval/` as green, while `external-ai/zones.json` classifies `docs/test-results/*` as **yellow** (only `docs/ideas/*` is green in `vehicle-defs`). Treated it as yellow and added `needs-claude-review` to PR #219.
- **G6-1 run order:** `en` ran 3 times and then `tr` ran 3 times without restarting `llama-server` between runs or locales, matching "llama-server restarted before each arm". As documented in `README.md`, this revealed cross-run exact-prompt caching in `llama-server` `b1b770d` (Runs 2–3 hit `95.9%`/`95.1%` in both arms).
- **`vehicle-workspace` branch base:** `ext/gemini-long-run-6-log` was branched from `origin/main` (`ad02ef8`) before `vehicle-workspace#266` and `#263` merged to `main` (`3719638`); only `external-ai/log/2026-11-27-gemini-long-run-6.md` is added, so it merges cleanly without conflict.

## For Claude
- **G6-1 (`vehicle-defs#219`, `needs-claude-review`):**
  - Code audit noticed `vehicle-server/src/vehicle_server/chat/providers/factory.py:33` constructs `OpenAiCompatLlm` without `cache_prompt=True` (default `False`), whereas the default local client in `chat/wiring.py:21` passes `cache_prompt=True`. If a user explicitly selects the `local` preset in per-user LLM settings, prompt caching would be off.
  - If a follow-up measurement (round 3) wants to isolate within-conversation caching without cross-run exact-prompt replay, pass `--cache-ram 0` (or restart `llama-server` between runs) and add multi-turn conversations whose turns 2–4 exercise LLM phrasing (`timed=0` on turn 4 in the current `mt-01..mt-10` set).
- **G6-4 (`vehicle-defs#218`):** `Q-008` (multi-node SIL time base) is intentionally left open; all transport/harness choices are marked **proposed** for Claude/user decision.
- **G6-5 (`vehicle-analyzer#87`):** Line coverage is now `95.36%` with zero modules below `80%` lines; ready for Claude to ratchet the `vite.config.ts` coverage thresholds in a follow-up if desired.
- **G6-6 (`vehicle-mcp#41`, `needs-claude-review`):**
  - Audit of `vehicle-defs/faults/catalog.yaml` and `vehicle-defs/faults/i18n/tr.yaml`: **0** `snake_case` or `did.`/`sensor.` tokens found in rider-facing fields (`root_cause`, `rider_text`, `action`, `complaints`).
  - Markdown architecture/design docs under `vehicle-defs/docs/*.md` legitimately contain technical identifiers (`did.*`, `ride_*`, signal/module names) when indexed via `--docs`; `vehicle-mcp` does not rewrite raw doc chunks (`Chunk.text` left untouched per G6-6 constraint 3). If rider-facing doc search results should hide or translate those identifiers, that requires a defs-side or display-layer policy decision.
  - `undated_ride_reason` in `get_ride_summary` (`tests/test_tools.py:492` explicitly pins `"created_utc"`) is kept in `EXEMPT_FIELDS` as an API-schema diagnostic string.

## Claude review
Zones: no red path. G6-1 and G6-6 yellow as declared (the brief wrongly listed `docs/test-results/` as green; `zones.json` is right). Reviews: architecture-guard on the code PRs, a fact-check of the SIL note against the DBC and host HAL code. Claude's commits are on top of each ext branch.

- **G6-1 (defs#219):** numbers check out. Fixed: "all 12 runs" → 6 paired runs; caption that the pooled per-turn rows mix the cold run with replay-dominated runs; `tr` Run 1 is not cold; outcome for T72 (keep `-np 1`; round 3 needs a restart or `--cache-ram 0` between runs and LLM-phrased later turns). The `cache_prompt` finding was real: fixed in **server#115** (the explicit `local` preset also skipped `check_llm_url`).
- **G6-2 (server#113):** the rider note was quoted in the answer, stored, and fed back as a recent turn into the next LLM prompt (verbatim on cloud): `recent_pairs` now returns a placeholder for `policy.UNTRUSTED_TEXT_TOOLS`. Kind counts fell back to counting a truncated list and could disagree with the total; now they always add up (remainder = neutral bucket). Note sanitiser now drops Unicode format characters (bidi, zero-width) and swaps inner `"`. "Only the first 5" takes N from the constant.
- **G6-3 (server#114):** a missing `index.sqlite` or `ride_marks` table gave a silent empty export; now a warning. Marks in overlapping session windows (one line per window) and exports without `--owner` (mark ids are unique per owner only) are warned and documented.
- **G6-4 (defs#218):** 7 fixes: safety-node pass overruns were written as observed (only rt-core step gaps were); ALR-001 sustain is 10 s, not 60 s; the example scenario could not raise the alert (15 s, no engine-running step); the SIL bridge cannot be combined with the mock live source (`api.py`); D-118 item 6 attribution; an unsourced "~3 s incremental" build; invented identifiers in the example YAML (now a proposed new schema with defs names).
- **G6-5 (analyzer#87):** good. Worker test asserts the message kind instead of skipping its checks and unstubs `self`; Claude ratcheted the global coverage floors (91/82/90/94).
- **G6-6 (mcp#41):** good. D-107 fix (`from vehicle_mcp.matching`, not `..`), aliases instead of wrapper functions. Humanised chunk titles give the same FTS5 tokens (unicode61 splits on `_`), so ranking is unchanged. Tool-name hints removed from `reason` texts are accepted (rider-facing). Doc chunks with identifiers (defs `docs/*.md`) stay as they are: a display-layer policy, not needed now.

Rule changes: three hard rules added to `AGENTS.base.md` §3 (totals reconcile; untrusted text stays quoted on every path; examples in docs must work), rendered with `scripts/sync_claude.py`.
