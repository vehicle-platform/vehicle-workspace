---
date: 2026-11-27
tool: gemini-cli/gemini-4
topic: long-run-5
repos:
  - vehicle-workspace
  - vehicle-defs
  - vehicle-mobile
  - vehicle-mcp
  - vehicle-server
  - vehicle-analyzer
branches:
  - vehicle-workspace:ext/gemini-long-run-5-log
  - vehicle-defs:ext/gemini-cubemx-cli
  - vehicle-defs:ext/gemini-diagrams
  - vehicle-mobile:ext/gemini-marks-followup
  - vehicle-mcp:ext/gemini-mcp-marks
  - vehicle-server:ext/gemini-multiturn-eval
  - vehicle-mobile:ext/gemini-readmes
  - vehicle-server:ext/gemini-readmes
  - vehicle-analyzer:ext/gemini-analyzer-tests-2
prs:
  - https://github.com/vehicle-platform/vehicle-defs/pull/214
  - https://github.com/vehicle-platform/vehicle-defs/pull/215
  - https://github.com/vehicle-platform/vehicle-mobile/pull/60
  - https://github.com/vehicle-platform/vehicle-mcp/pull/39
  - https://github.com/vehicle-platform/vehicle-server/pull/110
  - https://github.com/vehicle-platform/vehicle-mobile/pull/61
  - https://github.com/vehicle-platform/vehicle-server/pull/111
  - https://github.com/vehicle-platform/vehicle-analyzer/pull/85
zone: yellow
review: pending
---

# long-run-5 (CubeMX CLI note, diagrams, ride-mark follow-ups, multi-turn cache measurement, READMEs, analyzer tests)

## Goal
Execute `external-ai/tasks/2026-11-27-gemini-long-run-5.md` end to end (G5-0, G5-A, G5-1, G5-2, G5-3, G5-4, G5-5, G5-6, G5-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-27-gemini-long-run-5.md` (`ext/gemini-long-run-5-log`): session log (G5-0, G5-9).
- `vehicle-defs/docs/ideas/cubemx-cli.md` (`ext/gemini-cubemx-cli`, PR `vehicle-defs#214`, green): facts-only STM32CubeMX `-q` headless CLI reference derived from workspace `local/cubemx/` scripts and logs (G5-A, T70). CubeMX was not launched and no packages were installed.
- `vehicle-defs/docs/diagrams/*` (`ext/gemini-diagrams`, PR `vehicle-defs#215`, **yellow**, `needs-claude-review`): 7 thesis Mermaid diagrams (`01-system-context.md` through `07-raspi-dataflow.md`) plus `docs/diagrams/README.md`, each with caption and explicit source traceability to recorded decisions and source files (G5-1).
- `vehicle-mobile` (`ext/gemini-marks-followup`, PR `vehicle-mobile#60`, green): added **More** entry in `showRideMarkPicker` showing all 7 D-133 kinds (`rough_road`, `traffic`, etc.), optional note (`<= 200` chars with counter, empty = no note) when picking **Other** or opening **More**, focus-paused 5 s auto-close (resumes on unfocus), EN/TR strings in `l10n_src/parts/marks.{en,tr}.json` merged via `tool/l10n_merge.py` + `flutter gen-l10n`, and widget tests reusing existing `MarkQueue`/`MarksClient` (G5-2, D-133).
- `vehicle-mcp` (`ext/gemini-mcp-marks`, PR `vehicle-mcp#39`, **yellow**, `needs-claude-review`): added read-only `get_ride_marks(session_id)` calling `GET /rides/{ride_id}/marks` via `client.py`, returning labelled `{name, unit, value, label}` quantities (`mark_count` + per-kind counts) plus chronological marks (`offset_s`, `offset` quantity in seconds from ride start, `kind`, `note` wrapped via `untrusted.mark`), small-model spec in `specs.py` (within existing `SPEC_BUDGET_CHARS`), registered in `server.py`, with unit tests for normal, empty, unknown ride (404), older server (404), server error (503), unexpected position fields stripped, and empty `session_id`. Assistant routing untouched (G5-3, D-133 item 4, T65).
- `vehicle-server` (`ext/gemini-multiturn-eval`, PR `vehicle-server#110`, green): added 10 brand-new multi-turn conversations (`mt-01`..`mt-10`, 3–4 turns each, 35 turns per locale) to the **dev** set only (`spec.json`, `locales/{en,tr}.json`), extended `spec.py`, `runner.py`, `scoring.py`, and `report.py` to execute multi-turn conversations sequentially via the conversation store with guaranteed `DELETE /conversations/{id}` cleanup and per-turn metrics (`by_turn` + `multiturn_summary`), and added unit tests in `tests/test_chat_eval.py`. Measure-only: no prompt, router, or template changes (G5-4, T72).
- `vehicle-mobile/README.md` (`ext/gemini-readmes`, PR `vehicle-mobile#61`, green): brought README up to date from code (D-130 screens & responsive shell, D-133 ride marks + offline queue, D-129 in-ride alerts, D-121 voice/intercom, D-125 ARB i18n pipeline, build/test commands) (G5-5).
- `vehicle-server/README.md` (`ext/gemini-readmes`, PR `vehicle-server#111`, green): brought README up to date from code (D-133 marks endpoints + `ride_marks` storage, `GET /alerts/stream`, `/ws/live` + mock/MQTT live sources, `POST /chat` timings/conversations/chips, CLI commands, `chat-eval` dev & held-out `--spec` usage) (G5-5).
- `vehicle-analyzer` (`ext/gemini-analyzer-tests-2`, PR `vehicle-analyzer#85`, green): added `tests/components/SyncPanel.test.tsx` and `tests/useLiveSources.test.tsx` mocking worker/adapters at module boundaries without modifying red-zone adapter files; raised overall line coverage from 85.00% to 88.77% (G5-6).

## Result

### G5-4 Live Multi-Turn Prompt-Cache Measurement (`qwen2.5-1.5b-instruct-q4_k_m`, T72)
Provenance: synthetic (8 demo rides in local `server-data`; `local/run-llama.sh` `-np 1` + `local/run-server.sh`).
Command: `uv run vehicle-server chat-eval --base-url http://127.0.0.1:8000 --token-file <user-token> --locale <en|tr> --only mt-01,mt-02,mt-03,mt-04,mt-05,mt-06,mt-07,mt-08,mt-09,mt-10 --out ... --summary-md ...`

**English (`en`, 10 conversations, 35 turns, 14 LLM-timed, 0 errors, 0 forbidden):**

| turn | n | tool ok | timed | cache_n / prompt_n | cached share | TTFT p50 / p95 |
|---|---|---|---|---|---|---|
| 1 | 10 | 5/10 (50%) | 4 | 1.01 (1213/1204) | 50% | 89.7 ms / 1292.6 ms |
| 2 | 10 | 6/10 (60%) | 4 | 1.82 (1684/923) | 65% | 125.8 ms / 1642.2 ms |
| 3 | 10 | 3/10 (30%) | 6 | 1.22 (2325/1910) | 55% | 128.8 ms / 1663.2 ms |
| 4 | 5 | 4/5 (80%) | 0 | n/a | n/a | n/a / n/a |

- Turn 1 cached share: **50%** (TTFT p50 89.7 ms) vs. turns 2+: **59%** (TTFT p50 128.8 ms).

**Turkish (`tr`, 10 conversations, 35 turns, 11 LLM-timed, 0 errors, 0 forbidden):**

| turn | n | tool ok | timed | cache_n / prompt_n | cached share | TTFT p50 / p95 |
|---|---|---|---|---|---|---|
| 1 | 10 | 7/10 (70%) | 5 | 0.69 (1393/2007) | 41% | 1150.7 ms / 1497.6 ms |
| 2 | 10 | 8/10 (80%) | 1 | 0.00 (3/773) | 0% | 1524.8 ms / 1524.8 ms |
| 3 | 10 | 6/10 (60%) | 5 | 0.47 (1391/2940) | 32% | 1629.5 ms / 1705.4 ms |
| 4 | 5 | 5/5 (100%) | 0 | n/a | n/a | n/a / n/a |

- Turn 1 cached share: **41%** (TTFT p50 1150.7 ms) vs. turns 2+: **27%** (TTFT p50 1524.8 ms).

**Conclusion:** The measured numbers do **not** show a consistent multi-turn prompt-cache benefit on `qwen2.5-1.5b` (EN cached share rose 50% -> 59% on turns 2+ while TTFT p50 rose 89.7 ms -> 128.8 ms; TR cached share dropped 41% -> 27% and TTFT p50 rose 1150.7 ms -> 1524.8 ms).

## Checks
- `python3 scripts/check_zones.py . --base origin/main` (G5-0 / G5-9): GREEN.
- **G5-A (`vehicle-defs#214`):**
  - `python3 local/cubemx/check_pins.py rt-core`: pass (`45 pins with a signal in CSV, 37 planned, 0 mismatches`).
  - `python3 local/cubemx/check_pins.py safety-node`: pass (`34 pins with a signal in CSV, 25 planned, 0 mismatches`).
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: GREEN.
- **G5-1 (`vehicle-defs#215`):**
  - `python3 scripts/check_zones.py vehicle-defs --base origin/main`: YELLOW (`docs/diagrams/*`, `needs-claude-review`).
  - `npx -y @mermaid-js/mermaid-cli`: timed out after 120 s (no local `mmdc` binary installed; skipped and noted in PR).
- **G5-2 (`vehicle-mobile#60`):**
  - `python3 tool/l10n_merge.py && flutter gen-l10n`: pass (`test/i18n_test.dart` green).
  - `flutter analyze`: pass (No issues found).
  - `flutter test`: pass (718 passed, 0 failed).
  - `flutter build web --release --base-href /app/`: pass (`Built build/web`).
  - `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: GREEN.
- **G5-3 (`vehicle-mcp#39`):**
  - `uv run ruff check .`: pass.
  - `uv run ruff format --check .`: pass (48 files).
  - `uv run mypy`: pass (0 issues in 22 source files).
  - `uv run pytest --cov --cov-report=term-missing`: pass (273 passed, 1 skipped; total coverage 93.86% >= 91.0% floor).
  - `python3 scripts/check_zones.py vehicle-mcp --base origin/main`: YELLOW (`needs-claude-review`).
- **G5-4 (`vehicle-server#110`):**
  - `uv run ruff check .`: pass.
  - `uv run ruff format --check .`: pass (185 files).
  - `uv run mypy`: pass (0 issues in 103 source files).
  - `uv run pytest --cov --cov-report=term-missing`: pass (2450 passed, 0 failed; total coverage 94%).
  - `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN.
- **G5-5 (`vehicle-mobile#61`, `vehicle-server#111`):**
  - `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: GREEN (`README.md`).
  - `python3 scripts/check_zones.py vehicle-server --base origin/main`: GREEN (`README.md`).
- **G5-6 (`vehicle-analyzer#85`):**
  - `npx tsc -p tests/tsconfig.json --noEmit`: pass (0 errors).
  - `npx tsc -p ui-tests/tsconfig.json --noEmit`: pass (0 errors).
  - `npm run lint` (`eslint . --max-warnings 0`): pass (0 errors, 0 warnings).
  - `npm run test:coverage`: pass (64 test files, 476 tests passed; Statements 86.66%, Branches 79.42%, Functions 84.98%, Lines 88.77%).
  - `npm run build` (`tsc -b && vite build`): pass (1.95 s).
  - `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: GREEN.

## Unsure about
- **G5-1 Mermaid CLI rendering:** `mmdc` is not installed locally and `npx -y @mermaid-js/mermaid-cli` timed out after 120 s (downloading Chromium). All 7 Mermaid blocks were manually audited for GitHub Mermaid syntax (quoted labels, no raw `<...>` HTML-like tags inside labels), but should be visually verified in the GitHub PR diff preview.
- **G5-6 `SyncPanel.tsx` drag-drop:** The task brief mentioned drag-drop, but `src/components/SyncPanel.tsx` only implements `<input type="file">` with `FileReader` (no drag-drop event handlers exist in the component). Because G5-6 is tests-only, no drag-drop code was added to `SyncPanel.tsx`.
- **Skipped CI-only steps:** Android APK Gradle build (`vehicle-mobile`), Docker image build and `pip-audit` (`vehicle-server`, `vehicle-mcp`), and Playwright E2E (`vehicle-analyzer`); no dependencies, Dockerfiles, or analyzer UI sources were changed.

## For Claude
1. **Yellow PRs marked `needs-claude-review`:**
   - `vehicle-defs#215` (G5-1: 7 thesis Mermaid diagrams under `docs/diagrams/`).
   - `vehicle-mcp#39` (G5-3: `get_ride_marks(session_id)` read-only MCP tool; assistant routing intentionally left for Claude).
2. **G5-4 prompt-cache finding (T72):**
   - Multi-turn measurement on `qwen2.5-1.5b` did not demonstrate a consistent cache/TTFT gain on turns 2+. Hypotheses to investigate: (a) deterministic router + template-first answers handle most turns (only 14/35 EN and 11/35 TR turns invoked `llama-server`, 0/5 on turn 4), and (b) with `llama-server -np 1`, alternating between the router system prompt (`system_text(tools)`) and the phrasing system prompt (`_system_prompt(locale)`) evicts the single KV cache slot between phases. Testing `-np 2` (or separating router vs. phraser slots) is a candidate hypothesis for T72.
3. **G5-6 coverage floor:**
   - Overall coverage is now 86.66% statements / 79.42% branches / 84.98% functions / 88.77% lines (thresholds in `vite.config.ts` remain at 83 / 76 / 81 / 85; Claude may ratchet if desired).

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
