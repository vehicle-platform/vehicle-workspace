---
date: 2026-11-28
tool: gemini-cli/gemini-4
topic: long-run-8
repos:
  - vehicle-workspace
  - vehicle-server
  - vehicle-ml
  - vehicle-mcp
branches:
  - vehicle-workspace:ext/gemini-long-run-8-log
  - vehicle-server:ext/gemini-marks-device-time
  - vehicle-ml:ext/gemini-marks-labels
  - vehicle-mcp:ext/gemini-rag-tr-tune
prs:
  - https://github.com/vehicle-platform/vehicle-server/pull/118
  - https://github.com/vehicle-platform/vehicle-ml/pull/37
  - https://github.com/vehicle-platform/vehicle-mcp/pull/43
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
