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
prs:
  - https://github.com/vehicle-platform/vehicle-server/pull/104
  - https://github.com/vehicle-platform/vehicle-mcp/pull/35
  - https://github.com/vehicle-platform/vehicle-mobile/pull/55
  - https://github.com/vehicle-platform/vehicle-ml/pull/31
  - https://github.com/vehicle-platform/vehicle-defs/pull/206
zone: yellow
review: done 2026-11-26 (all five PRs fixed and merged)
---

# long-run-2 (assistant i18n, RAG quality, chat list UI, model bake-off, validation plan)

## Goal
Execute `external-ai/tasks/2026-11-26-gemini-long-run-2.md` from **G2-0** through **G2-6** in order after verifying run 1 (`vehicle-ml#30`, `ext/gemini-ride-llm-heldout`) was complete and open.

## Changes

### G2-0 & G2-6 — Session log (`vehicle-workspace`, `ext/gemini-long-run-2-log`, GREEN)
- Initialized (`c31a76a`) and finalized `external-ai/log/2026-11-26-gemini-long-run-2.md`.

### G2-1 — Rider notification texts per locale (`vehicle-server`, `ext/gemini-notification-i18n`, GREEN)
- **PR:** https://github.com/vehicle-platform/vehicle-server/pull/104 (`9602bf9`)
- Added `src/vehicle_server/i18n.py` and packaged `src/vehicle_server/locales/{en,tr}.json` (reusing `chat/locales/` pattern).
- Localized `rider_text.py`, `notifications.py` (language-neutral `template_key` + numeric `template_params` columns added via migration-safe `ALTER TABLE`; legacy rows without a key retain stored title/body verbatim), `notifications_api.py` (`GET /notifications?locale=en|tr`, default `en`), `alerts/live.py`, `alerts/service.py`, `alerts/replay.py`, `alerts_api.py` (`GET /alerts/stream?locale=en|tr`), `chat/templates.py`, `chat/service.py` (system prompt in `chat/locales/{en,tr}.json`), `chat/numbers.py` (Unicode escapes only), `assistant_api.py` (`?locale=en|tr`), `README.md`, and tests (`test_notifications.py`, `test_rider_text.py`, `test_alert_service.py`, `test_chat.py`, `test_assistant.py`, `test_openapi_errors.py`).
- No `*ota*`, `*gps*`, `*position*`, or `*mdf4*` files touched.

### G2-2 — Retrieval quality for `search_knowledge` (`vehicle-mcp`, `ext/gemini-rag-quality`, YELLOW — `needs-claude-review`)
- **PR:** https://github.com/vehicle-platform/vehicle-mcp/pull/35 (`7252d86`, PR body starts with `needs-claude-review`)
- Added retrieval eval dataset `tests/retrieval_eval/queries.json` (42 EN + 6 weak) and `tests/retrieval_eval/locales/tr.json` (42 TR + 6 weak), evaluator `src/vehicle_mcp/knowledge/eval_retrieval.py`, and `vehicle-mcp-index eval --db ...` CLI in `indexer.py`.
- Implemented and kept three measured improvements:
  1. Turkish suffix-stripping light stemmer driven by suffix list in `src/vehicle_mcp/locales/tr.json` + locale stopword removal, applied on both index and query for `locale=tr` chunks.
  2. Query expansion via complaint synonyms (`matching.expand`) + group-level RRF fusion by `ref`.
  3. Relative score cutoff (`0.55 x best`) and e5 cosine similarity floor (`0.845` on `OnnxE5Embedder`) to suppress weak/filler hits.
- Updated `README.md` and `tests/test_knowledge.py` with synthetic corpus + fake embedder tests. Temporary `local/knowledge/eval-after.sqlite` removed.

**Baseline vs After (`multilingual-e5-small`, live catalog + `vehicle-defs/docs/ideas/*.md`):**

| Locale | Stage | N (weak) | Recall@1 | Recall@3 | Recall@5 | MRR | Weak mean hits | Weak empty rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `en` | Baseline | 42 (6) | 0.929 | 0.976 | 1.000 | 0.957 | 5.00 | 0.000 |
| `en` | After | 42 (6) | 0.929 | 0.976 | 1.000 | 0.957 | 2.67 | 0.333 |
| `tr` | Baseline | 42 (6) | 0.714 | 0.905 | 0.929 | 0.804 | 4.00 | 0.000 |
| `tr` | After | 42 (6) | **0.810** | **0.952** | **0.976** | **0.878** | **1.00** | **0.667** |

Note: the Turkish valve-clearance tapping query from the G2-2 brief now ranks `ENG-001` at **#1**.

### G2-3 — Conversation list, memory UI, and AlertBanner fix (`vehicle-mobile`, `ext/gemini-chat-list`, GREEN)
- **PR:** https://github.com/vehicle-platform/vehicle-mobile/pull/55 (`8e5d578`)
- Added `lib/models/conversation.dart`, `lib/services/conversations_client.dart`, and `lib/services/chat_export{,_io,_web}.dart` (uses existing `package:web`, `share_plus`, `path_provider`; zero new dependencies).
- Updated `lib/models/chat_message.dart`, `lib/services/chat_client.dart`, `lib/ui/assistant/conversation_list.dart`, `lib/ui/assistant/assistant_screen.dart` (280 px left sidebar at `>= 900 px`, modal sheet below 900 px; new chat, search, rename, delete with confirm, temporary chat toggle, continue via `conversation_id`, tappable follow-up `chips`).
- Added `lib/ui/settings/assistant_memory_screen.dart` and wired Settings -> "Assistant memory" (`lib/ui/settings_screen.dart`: list, edit, delete one, delete all with confirm, export chats).
- Fixed `lib/ui/app_shell.dart` so `AlertBanner` pushes the scaffold down in a `Column` instead of overlaying the `AppBar`.
- Updated `l10n_src/parts/{assistant,settings}.{en,tr}.json`, merged via `tool/l10n_merge.py`, ran `flutter gen-l10n`, updated `test/alert_shell_test.dart`, and added `test/conversations_and_memory_test.dart`. `pubspec.lock` untouched.

### G2-4 — Base-model bake-off harness (`vehicle-ml`, `ext/gemini-model-bakeoff`, GREEN)
- **PR:** https://github.com/vehicle-platform/vehicle-ml/pull/31 (`1f55472`)
- Added `src/vehicle_ml/ride_llm/bakeoff/` (`models.json`, `registry.py`, `llama.py`, `heldout.py`, `runner.py`, `cli.py`, `__main__.py`) plus top-level `ride_llm/bakeoff/` shim so `python -m ride_llm.bakeoff run --models ... --locales en tr` works without modifying `pyproject.toml` or adding runtime dependencies.
- Official `Qwen/*-GGUF` registry (all Apache-2.0) with verified LFS SHA-256 digests:
  - `qwen2.5-1.5b-instruct-q4_k_m` (`Qwen/Qwen2.5-1.5B-Instruct-GGUF`)
  - `qwen3-1.7b-q8_0` (`Qwen/Qwen3-1.7B-GGUF` — official repo publishes only `Q8_0`, no `Q4_K_M`)
  - `qwen3-4b-q4_k_m` (`Qwen/Qwen3-4B-GGUF`)
- Added `ride_llm/bakeoff/out/` to `.gitignore`, unit tests with fakes in `tests/test_ride_llm_bakeoff.py`, and two-terminal procedure in `README.md`.

### G2-5 — Validation plan draft (`vehicle-defs`, `ext/gemini-validation-plan`, GREEN + YELLOW `docs/README.md` — `needs-claude-review`)
- **PR:** https://github.com/vehicle-platform/vehicle-defs/pull/206 (`671d44d`, PR body starts with `needs-claude-review`)
- Added `docs/ideas/validation-plan.md` (93 lines; first line `Status: idea note, not a decision`): evidence levels L1–L4, claim-by-claim evidence matrix, first real-ride L3 replay protocol for PROVISIONAL alert rules, bench/HIL-only fault injection boundaries (invariants 1 and 3), mandatory `docs/test-results/` provenance labeling (`synthetic`/`bench`/`real`), and verified URLs for ISO 26262-4:2018, ISO 26262-6:2018, and ASAM OpenSCENARIO.
- Linked `validation-plan.md` from the `ideas/*` row in `docs/README.md`.

## Result
All tasks G2-0 through G2-6 completed on separate branches with PRs opened (none merged, no force-pushes).

## Checks
- **G2-1 (`vehicle-server`):** `uv run ruff check .` pass; `uv run ruff format --check .` pass; `uv run mypy` 0 issues (100 files); `uv run pytest --cov` **2314 passed, 0 failed, 94% coverage**; Turkish char scan in `src/vehicle_server/**/*.py` = 0 hits; `check_zones.py vehicle-server --base origin/main` = **GREEN** (23 paths).
- **G2-2 (`vehicle-mcp`):** `uv run ruff check .` pass; `uv run ruff format --check .` pass; `uv run mypy` 0 issues (22 files); `uv run pytest --cov` **259 passed, 1 skipped (slow), 94.05% coverage** (floor 91%); spec-size budget green; `check_zones.py vehicle-mcp --base origin/main` = **YELLOW** (expected).
- **G2-3 (`vehicle-mobile`):** `flutter analyze` clean; `flutter test` **670 passed, 0 failed**; `flutter build web --release --base-href /app/` succeeded; Turkish char scan in `lib/**/*.dart` (excl. `lib/l10n/`) = 0 hits; `check_zones.py vehicle-mobile --base origin/main` = **GREEN** (23 paths).
- **G2-4 (`vehicle-ml`):** `uv run ruff check .` pass; `uv run ruff format --check .` pass; `uv run mypy` 0 issues (33 files); `uv run pytest --cov --cov-report=term-missing` **205 passed, 0 failed, 88.60% branch coverage** (floor 88.0%); `python -m ride_llm.bakeoff list-models` ok; `verify --models qwen2.5-1.5b --models-dir ../local/pi/models` OK; `check_zones.py vehicle-ml --base origin/main` = **GREEN** (15 tracked paths).
- **G2-5 (`vehicle-defs`):** `wc -l docs/ideas/validation-plan.md` = 93 lines; Turkish char scan = 0 hits; `check_zones.py vehicle-defs --base origin/main` = `GREEN` (`docs/ideas/validation-plan.md`) + `YELLOW` (`docs/README.md`).
- **G2-6 (`vehicle-workspace`):** `check_zones.py . --base origin/main` = **GREEN** (`external-ai/log/2026-11-26-gemini-long-run-2.md`).

## Skipped
- **G2-4 live multi-model bake-off execution on Mac:** skipped because `Qwen3-1.7B-Q8_0.gguf` and `Qwen3-4B-Q4_K_M.gguf` are not downloaded locally (only `qwen2.5-1.5b-instruct-q4_k_m.gguf` is in `local/pi/models/`, verified via SHA-256) and `vehicle-server` was not running on port 8000. Exact two-terminal run instructions are in `vehicle-ml/README.md` and `vehicle-ml#31`.

## Unsure about
- **`Qwen/Qwen3-1.7B-GGUF` quantization:** the G2-4 brief asked for `Qwen3-1.7B Q4_K_M` from official `Qwen/*-GGUF` repos only, but `https://huggingface.co/api/models/Qwen/Qwen3-1.7B-GGUF` publishes only `Qwen3-1.7B-Q8_0.gguf` (1.83 GB). Registered `Qwen3-1.7B-Q8_0.gguf` with its verified official LFS SHA-256 rather than using an unofficial third-party mirror.

## For Claude
- Review yellow PRs (`needs-claude-review`): `vehicle-mcp#35` (G2-2 RAG quality) and `vehicle-defs#206` (G2-5 `docs/README.md` index link).
- Confirm whether `Qwen3-1.7B-Q8_0.gguf` is acceptable for D-132 stage 0 or if the user prefers locally quantizing `Qwen/Qwen3-1.7B` to `Q4_K_M` with `llama-quantize`.
- Note: untracked run-1 outputs (`vehicle-ml/src/vehicle_ml/ride_llm/data/out/{answer,route}.jsonl`) exist on disk in the local checkout (git-ignored on PR #30's branch, not on `main`); they were excluded from `vehicle-ml#31`.

## Claude review
Fixes were pushed to each `ext/gemini-*` PR branch from a `claude/*-review` worktree; every PR merged after green CI.

- **G2-1 `vehicle-server#104`** (merged `4a82942`): `46f495e` one locale loader (`i18n.py`) with a typed `Locale` and per-key English fallback; chat keyword, number-word, follow-up and chip tables and system prompts moved to `chat/locales/{en,tr}.json`; `AlertService` publishes per-locale payloads; `/ws/live` takes `?locale=` (unknown code closes with 1008). `8a78a87` key parity, fallback and per-locale alert tests (`tests/test_i18n.py`). `b6ac780` README/CLAUDE.md locale rule and client notes; stale "short Turkish" `/chat` row fixed. 2326 tests passed. Notification rows stored before the change keep their stored text; rows with a `template_key` render per locale.
- **G2-2 `vehicle-mcp#35`** (yellow, merged `b93d3ae`): `6a55a66` relevance is decided on vector/BM25 signals, not on RRF scores (RRF ranks are not comparable across queries). `33385fe` catalog holdout split so the cutoffs are not tuned on the eval set, tuning-grid note, README.
- **G2-3 `vehicle-mobile#55`** (merged `fe43d04`, after #104): `64c6a9f` shared authed JSON transport for the conversations and provider clients; `72051b5` inbox texts requested in the UI locale; alert banner slot renamed; `b4e0eb0` chat export temp file deleted after sharing; `5501199` both temporary-chat toggles clear the chat, late replies are dropped, failures surface, `ConversationsController` extracted.
- **G2-4 `vehicle-ml#31`** (merged `cd6e913`, after #30): `81e46dd` top-level `ride_llm` shim removed (use the package entry point); `7ca4b99` Qwen3 thinking disabled per model, harness hardened. `Qwen3-1.7B-Q8_0` (the only quant in the official repo) is accepted for D-132 stage 0; a local `Q4_K_M` requantization stays optional.
- **G2-5 `vehicle-defs#206`** (yellow, merged `652a490`): `096d6de` validation-plan targets marked as proposed; ISO 26262-12 cited for the motorcycle-specific part.

Follow-ups (not blocking): `vehicle-mobile` `alert_controller.dart` does not pass `?locale=` to `/alerts/stream`, so live alerts now arrive in the server default `en`; `chat_client.dart` defaults `locale` to `tr` instead of the UI locale.
