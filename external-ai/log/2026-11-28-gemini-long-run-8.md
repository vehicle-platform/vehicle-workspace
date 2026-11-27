---
date: 2026-11-28
tool: gemini-cli/gemini-4
topic: long-run-8
repos:
  - vehicle-workspace
  - vehicle-server
  - vehicle-ml
  - vehicle-mcp
  - vehicle-defs
  - vehicle-linux-node
branches:
  - vehicle-workspace:ext/gemini-long-run-8-log
  - vehicle-server:ext/gemini-marks-device-time
  - vehicle-ml:ext/gemini-marks-labels
  - vehicle-mcp:ext/gemini-rag-tr-tune
  - vehicle-defs:ext/gemini-rag-tr-results
  - vehicle-mcp:ext/gemini-label-echo
  - vehicle-server:ext/gemini-label-echo
  - vehicle-linux-node:ext/gemini-kuksa-macos-draft
  - vehicle-server:ext/gemini-guard-recall-tr
  - vehicle-defs:ext/gemini-guard-recall-tr
prs:
  - https://github.com/vehicle-platform/vehicle-server/pull/118
  - https://github.com/vehicle-platform/vehicle-ml/pull/37
  - https://github.com/vehicle-platform/vehicle-mcp/pull/43
  - https://github.com/vehicle-platform/vehicle-defs/pull/227
  - https://github.com/vehicle-platform/vehicle-mcp/pull/45
  - https://github.com/vehicle-platform/vehicle-server/pull/121
  - https://github.com/vehicle-platform/vehicle-linux-node/pull/39
  - https://github.com/vehicle-platform/vehicle-server/pull/123
  - https://github.com/vehicle-platform/vehicle-defs/pull/230
zone: yellow
review: pending
---

# long-run-8 (marks time axis, marks weak labels, RAG Turkish tune pass, label echo audit, guard recall, Kuksa macOS draft, cache round 4, traceability matrix)

## Goal
Execute `external-ai/tasks/2026-11-28-gemini-long-run-8.md` end to end (G8-0 through G8-9) from up-to-date `main` branches, opening one PR per task on its dedicated `ext/gemini-*` branch with passing local CI and zone checks.

## Changes

### G8-0 and G8-9 — Session log (`vehicle-workspace`, `ext/gemini-long-run-8-log`, GREEN)
- `external-ai/log/2026-11-28-gemini-long-run-8.md`: opened at session start (G8-0); updated and pushed after every task.

### G8-1 — Marks onto the device time axis (`vehicle-server`, `ext/gemini-marks-device-time`, GREEN, D-133 item 5)
- PR: https://github.com/vehicle-platform/vehicle-server/pull/118
- `vehicle-server/src/vehicle_server/marks_export.py`, `cli.py`, `README.md`, `tests/test_marks_export.py`: added per-record integer `device_time_ms` and `time_kind` via `device_time_ms = t_utc - median(rx_utc_ms - device_time_ms)` over one Parquet kind (mirroring `vehicle-ml/src/vehicle_ml/dataset.py:164` base-kind selection among `("telemetry", "imu")` with fixed fallback `("telemetry", "imu", "gps", "signals")`); sessions with missing Parquet, fewer than `MIN_TIME_AXIS_ROWS=3` valid paired rows, or any backwards `device_time_ms` jump omit `device_time_ms`/`time_kind`, emit one warning line on stderr per session, and are counted in `ExportSummary` (`unmapped_marks`, `unmapped_sessions`). `offset_s` unchanged.

### G8-2 — Ride marks as weak labels (`vehicle-ml`, `ext/gemini-marks-labels`, GREEN, proposed, D-133 items 4-5, T65)
- PR: https://github.com/vehicle-platform/vehicle-ml/pull/37
- `vehicle-ml/src/vehicle_ml/marks.py`, `cli.py`, `tests/test_marks.py`: added proposed `load_marks`, `label_windows` (reusing `vehicle_ml.windows.Window`), `windows_from_features`, `windows_from_data_dir`, and `vehicle-ml marks` CLI subcommand. Validates every JSONL line loudly with line number, buckets unknown kinds under `"unknown"`, ignores `note`, leaves records without `device_time_ms` as `unmapped` (never mapped from `offset_s`), and reconciles all summary counts.

### G8-3a — RAG retrieval parameters and e5 prefix toggle (`vehicle-mcp`, `ext/gemini-rag-tr-tune`, YELLOW, `needs-claude-review`)
- PR: https://github.com/vehicle-platform/vehicle-mcp/pull/43
- `vehicle-mcp/src/vehicle_mcp/knowledge/{settings,embedder,store,search,eval_retrieval,indexer}.py`, `tests/test_knowledge.py`: exposed `RetrievalSettings` (`rrf_k`, `fts_weight`, `vector_weight`, `fts_pool`, `vector_pool_min`, `lexical_top_n`, `min_similarity`, `use_prefixes`) via env vars (`VEHICLE_MCP_RAG_*`) and `vehicle-mcp-index build/eval` CLI flags. Confirmed `OnnxE5Embedder` already sends `query: ` and `passage: ` (`embedder.py:31-32,147-151`). Defaults reproduce baseline identically (pinned by tests).

### G8-3b — RAG Turkish tune pass results (`vehicle-defs`, `ext/gemini-rag-tr-results`, YELLOW, `needs-claude-review`)
- PR: https://github.com/vehicle-platform/vehicle-defs/pull/227
- `vehicle-defs/docs/test-results/rag/2026-11-28-tr-tune/{README.md,dev-grid.json,test-once.json,unconfirmed-rank1-tr-tune.json}`: ran 21-setting dev (`tune`, n = 76) grid then 1 test-split run (n = 36) for best dev pick (`fts_weight=2.0`, `vector_weight=1.0`, `rrf_k=60`, `lexical_top_n=2`, `use_prefixes=True`). Test TR R@1/R@5 unchanged (`0.194` / `0.417`), MRR `+0.004` (`0.279 -> 0.283`). Diagnosed `faults/unconfirmed` rank-1 dominance on 27/76 TR `tune` queries (12 catalog FTS+vector via single `ref="unconfirmed"` pool; 15 English-only `docs/ideas` queries, 10 vector-only + 5 FTS+vector via same-language cosine bias). Proposed: keep defaults; structural fix is Claude's.

### G8-4 — Label echo audit and fixes (`vehicle-mcp` YELLOW + `vehicle-server` GREEN)
- PRs: https://github.com/vehicle-platform/vehicle-mcp/pull/45 (`needs-claude-review`), https://github.com/vehicle-platform/vehicle-server/pull/121
- `vehicle-mcp/src/vehicle_mcp/{matching,tools,knowledge/sources,knowledge/search}.py`, `tests/test_rider_labels.py`: reused `matching.human_label` via `humanise_identifiers` across symptom conditions, root cause/rider_text/action, unknown query/topic reasons, related conditions, headingless doc filenames, citation titles/sections, and missing-subsystem fault titles.
- `vehicle-server/src/vehicle_server/chat/{answers,templates,locales/en.json,locales/tr.json}`, `tests/test_label_echo.py`, `tests/test_conversations.py`: reused existing locale maps (`answers.labels`, `rider.signals`, `rider.inputs`) with generic localized fallback words (`Signal`/`Sinyal`, `Catalog entry`/`Katalog kaydı`, `Reference`/`Kaynak`), fixed `_stats`, `_card`, `_compare`, `_data_only_text`, `_symptom`, `_fault_entry`, `_faults`, `_generic`, and added rider-safe renderers for `explain_context` and `search_knowledge`.

### G8-5 — Turkish refusal-guard recall measurement (`vehicle-server` GREEN + `vehicle-defs` YELLOW, measure only, card T58)
- PRs: https://github.com/vehicle-platform/vehicle-server/pull/123 (GREEN), https://github.com/vehicle-platform/vehicle-defs/pull/230 (YELLOW, `needs-claude-review`)
- `vehicle-server/src/vehicle_server/chat/eval/{spec.json,locales/en.json,locales/tr.json}`: added 20 paired EN/TR **dev** guard items (`guard-refuse-01`..`guard-refuse-15`, `guard-allow-01`..`guard-allow-05`). Guard unmodified.
- `vehicle-defs/docs/test-results/chat-eval/2026-11-28-guard-recall/{README.md,guard-recall.json}` (`Provenance: synthetic`): deterministic `guard.refuses()` measurement (`n = 1`): EN recall `9/15` (60.0%), false refusals `1/5` (20.0%, `guard-allow-03`); TR recall `4/15` (26.7%), false refusals `0/5` (0.0%).

### G8-6 — Kuksa on macOS without CAN hardware draft (`vehicle-linux-node`, `ext/gemini-kuksa-macos-draft`, YELLOW, `needs-claude-review`, T74 item 2)
- PR: https://github.com/vehicle-platform/vehicle-linux-node/pull/39
- `vehicle-linux-node/docs/upstream-kuksa-macos-replay.md`: proposed upstream draft based on PR #35 (`README.md`, `docker-compose.yml`, `docker-compose.replay.yml`, `config/dbc_feeder.ini`, `replay.py`) with pinned multi-arch digests, `tmpfs: [/tmp:exec]`, colima `network_mode: host` note, **CONFIRM** markers, zero vehicle-specific CAN IDs/DIDs, and 4 open questions for the user.

## Result
In progress.

## Checks
- `python3 scripts/check_zones.py vehicle-workspace --base origin/main`: pending

## Unsure about
(None yet.)

## For Claude
(None yet.)

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
