---
date: 2026-11-26
tool: gemini-cli/gemini-4
topic: ride-llm-heldout
repos: [vehicle-workspace, vehicle-ml]
branches: [vehicle-workspace:ext/gemini-ride-llm-heldout-log, vehicle-ml:ext/gemini-ride-llm-heldout]
prs: [vehicle-ml#30]
zone: green
review: done 2026-11-26 (vehicle-ml#30 fixed and merged)
---

# Ride LLM stage 0: held-out eval set + template dataset scaffold

## Goal
Complete Ride LLM stage 0 tasks G1-0 through G1-4 (D-132): open the session log, author an independent 100-item bilingual (`en`/`tr`) held-out evaluation set without opening `vehicle-server` locale files, add its validator and tests, add a stdlib-only template dataset generator with number-grounding and held-out contamination guards, and open the `vehicle-ml` PR.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-26-gemini-ride-llm-heldout.md`: opened (G1-0) and finalized (G1-4) session log.
- `vehicle-ml/src/vehicle_ml/ride_llm/__init__.py`, `eval/__init__.py`, `eval/heldout/__init__.py`, `data/__init__.py`: package markers under the existing `src/vehicle_ml/` package layout so `mypy --strict` and `pytest --cov` cover all new code without editing `pyproject.toml`.
- `vehicle-ml/src/vehicle_ml/ride_llm/eval/heldout/spec.json`, `locales/en.json`, `locales/tr.json` (G1-1): 100 independent held-out evaluation items matching `vehicle-server`'s `spec.json` / `spec.py` schema (`questions` + `forbidden` regex groups). Natural, non-literal `en` and `tr` phrasings with colloquial speech, terse queries, typos, missing Turkish diacritics, and long multi-clause descriptions. Turkish text appears only in `locales/tr.json` (D-125).
- `vehicle-ml/src/vehicle_ml/defs.py`: exported `faults` and `vehicle_catalog` from the pinned `vehicle_defs` submodule alongside existing exports.
- `vehicle-ml/src/vehicle_ml/ride_llm/eval/heldout/validate.py` and `vehicle-ml/tests/test_ride_llm_heldout.py` (G1-2): validates ID parity across locales, allowed read-only `vehicle-mcp` tools, fact/signal/fault membership against `vehicle_defs`, regex compilation, topic minimums, and safety red-team `forbid` requirements.
- `vehicle-ml/src/vehicle_ml/ride_llm/data/templates.py`, `locales/en.json`, `locales/tr.json`, `vehicle-ml/.gitignore`, and `vehicle-ml/tests/test_ride_llm_templates.py` (G1-3): stdlib-only template generator writing `route.jsonl` (`question -> tool_call`) and `answer.jsonl` (`tool_result -> answer`) into git-ignored `src/vehicle_ml/ride_llm/data/out/`, consuming `vehicle_defs` signal units, fault entries, and `COMPLAINTS_I18N` when present, with deterministic `NumberGuardError` and n-gram `ContaminationError` (threshold `0.8`) checks.

## Result
- Opened PR: `vehicle-ml#30` (`https://github.com/vehicle-platform/vehicle-ml/pull/30`) on branch `ext/gemini-ride-llm-heldout` (not merged).
- Held-out item counts per topic (100 total):
  - `last_ride`: 3
  - `specific_ride`: 2
  - `distance`: 2
  - `time`: 1
  - `stops`: 2
  - `idle`: 2
  - `coolant`: 4
  - `battery`: 4
  - `speed`: 2
  - `rpm`: 2
  - `throttle`: 2
  - `warmup`: 2
  - `compare`: 3
  - `history`: 2
  - `faults`: 3
  - `symptoms`: 15 (min 15)
  - `explain`: 15 (min 15)
  - `knowledge`: 10 (min 10)
  - `out_of_scope`: 8 (min 8)
  - `safety_red_team`: 16 (min 15)
- Template CLI smoke test (`uv run python -m vehicle_ml.ride_llm.data.templates --per-family 8 --seed 42`): generated 104 verified pairs into git-ignored `src/vehicle_ml/ride_llm/data/out/{route,answer}.jsonl` with zero number-guard failures and zero held-out contamination hits.

## Checks
- `uv --directory vehicle-ml run ruff check .`: pass
- `uv --directory vehicle-ml run ruff format --check .`: pass (66 files already formatted)
- `uv --directory vehicle-ml run mypy`: pass (0 issues in 31 source files, strict mode)
- `uv --directory vehicle-ml run pytest --cov --cov-report=term-missing -q`: pass (213 passed; total branch coverage 90.24% >= 88.0%; `validate.py` 100%, `templates.py` 98%)
- `python3 scripts/check_zones.py vehicle-ml --base origin/main`: GREEN
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-gemini-ride-llm-heldout.md`: GREEN

## Unsure about
- Package path: the task brief wrote `ride_llm/...` (matching how `vehicle-ml/README.md` shortens `src/vehicle_ml/physics/...` to `physics/...`). Placed under `src/vehicle_ml/ride_llm/` so `uv_build`, `mypy` (`files = ["src"]`), and `pytest --cov` (`source = ["src"]`) include it natively without touching `pyproject.toml`. Added both `ride_llm/data/out/` and `src/vehicle_ml/ride_llm/data/out/` to `.gitignore`.
- Contamination metric: implemented symmetric word n-gram Jaccard overlap (`n=3`, clamping to shorter token length for 1-2 word queries) on ASCII-folded lowercase tokens (handling Turkish dotless `ı` -> `i`) with threshold `0.8`.
- `D-132` and `docs/ideas/ride-llm.md` were not yet merged onto local `vehicle-defs/main`, so they were read from the existing local branches `claude/d132-ride-llm` and `claude/ride-llm-research-note` via `git show`.

## For Claude
- **Submodule pin (`vehicle-ml/external/vehicle-defs`, red zone):** `vehicle-ml` is currently pinned at `v0.31.0`, which predates `vehicle_defs.faults.COMPLAINTS_I18N` and per-fault `complaints` tuples (added in `v0.33.0`). `templates.py` reads both via `getattr(faults, "COMPLAINTS_I18N", {})` and `entry.get("complaints")` and falls back to `root_cause` in English on `v0.31.0`; unit tests verify both the `v0.31.0` fallback and a mocked `v0.33.0` `COMPLAINTS_I18N` table. Once `vehicle-ml` is repinned to `v0.33.0+`, Turkish symptom training pairs will populate automatically from `COMPLAINTS_I18N["tr"]` with no code change.
- **Locale JSON format compatibility:** `heldout/locales/{en,tr}.json` uses `{"questions": {...}, "forbidden": {...}}` to match `vehicle-server/src/vehicle_server/chat/eval/spec.py` directly. If you later wire `vehicle-server chat-eval` to accept an external held-out directory, both `spec.json` and `locales/{en,tr}.json` are drop-in compatible.

## Claude review
- `vehicle-ml#30` (branch `claude/heldout-review`, pushed to `ext/gemini-ride-llm-heldout`):
  - `457e24e` pin vehicle-defs v0.33.0.
  - `e37910e` template ranges are grounded in `vehicle_defs`; the v0.31 fallback is dropped.
  - `4d5f78e` held-out forbid patterns are refusal-aware; ECU and safety refusal classes added.
- CI green; merged as `0eecba4`.
