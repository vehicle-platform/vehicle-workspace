# Gemini long run 2 — 2026-11-26 (assistant i18n, RAG quality, chat list UI, model bake-off, validation plan)

Written by Claude for Gemini CLI. **Start only after run 1 (`2026-11-26-gemini-ride-llm-heldout.md`) is
finished and its PR is open.** Run the tasks in order without asking between them. One branch and one
PR per task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>`
trailer), push after every commit. If a task is blocked, write why in the log's *For Claude* section
and go on to the next one. **Never merge a PR. Never force-push.**

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G2-0 (first!) and G2-6 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-2-log` | green |
| G2-1 | vehicle-server | `ext/gemini-notification-i18n` | green (do not touch `*ota*`, `*gps*`, `*position*`, `*mdf4*`) |
| G2-2 | vehicle-mcp | `ext/gemini-rag-quality` | **yellow** (PR body starts with `needs-claude-review`) |
| G2-3 | vehicle-mobile | `ext/gemini-chat-list` | green (do not touch `lib/services/session_upload*`, `lib/services/upload_client*`) |
| G2-4 | vehicle-ml | `ext/gemini-model-bakeoff` | green |
| G2-5 | vehicle-defs | `ext/gemini-validation-plan` | green **only** `docs/ideas/*`; everything else in vehicle-defs is red |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`. Before every push:
`python3 scripts/check_zones.py <repo> --base origin/main` (exit 2 = red path → revert it, note it in
*For Claude*).

## 0. Rules that apply to every task

- Read first: `GEMINI.md`, `STATUS.md`, then the target repo's `CLAUDE.md` (read only) and the
  decisions named in the task (search them in `vehicle-defs/docs/DECISIONS.md`; never read whole
  large docs).
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish
  appears **only** in locale resource files (`*/locales/tr.json`, the mobile `l10n_src/parts/*.tr.json`
  → `lib/l10n/app_tr.arb`, defs `faults/i18n/tr.yaml` which is red anyway).
- **Invariant 2:** signal names, DIDs, units and scales come only from the generated defs package;
  never hand-write them. **Invariant 7:** the LLM never computes; numbers come from tools.
- No new runtime dependencies unless the task allows it; say so in the PR if you add a dev
  dependency.
- Mirror each repo's CI locally before pushing (see its `.github/workflows/`); all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G2-0 Log

Create `external-ai/log/2026-11-26-gemini-long-run-2.md` from `external-ai/log/TEMPLATE.md`,
commit, push.

### G2-1 Rider notification texts per locale (vehicle-server, D-123, D-125)

**Problem.** The app is English by default (D-130), but notifications (`ride_summary`,
`data_quality`, `outlook`) are stored with Turkish title/body texts built in code
(`src/vehicle_server/rider_text.py`, `notifications.py`, also chat `templates.py` fixed texts and the
fixed rider texts in `assistant_api.py`). The English UI shows Turkish inbox rows.
**Do.**
1. Move every user-facing string of these modules into locale resource files
   (`src/vehicle_server/locales/en.json`, `tr.json`, packaged with the wheel; reuse the pattern of
   `src/vehicle_server/chat/locales/`). Keep the number formatting rules of `rider_text.py`
   (durations "18 min 36 s" / "18 dk 36 sn", one-decimal km, locale decimal separator).
2. Store notifications **language-neutral**: kind + a template key + the parameter values (numbers
   from the computed data, never from text). Render title/body **at read time** in the caller's
   locale: `GET /notifications?locale=en|tr` (default `en`), and the same for `/alerts/stream` texts
   that come from code (defs rule texts stay as they are). Migrate existing rows safely (keep the old
   text columns for rows without a key; add columns with a migration-safe ALTER).
3. Update the README rows and OpenAPI; tests for both locales and for the migration.
**Done when:** ruff, ruff format, mypy, full pytest (incl. Schemathesis/OpenAPI tests) green;
`grep -rnP '[çğıöşüÇĞİÖŞÜ]' src/vehicle_server --include=*.py` finds nothing.

### G2-2 Retrieval quality for `search_knowledge` (vehicle-mcp, D-132, T60 follow-up)

**Problem.** mcp#34 shipped hybrid RAG (`src/vehicle_mcp/knowledge/`: SQLite FTS5 + sqlite-vec,
multilingual-e5-small via ONNX, RRF k=60). Quality is moderate: the Turkish query "supaplardan
tıkırtı sesi" ranks a suspension phrase above ENG-001 (valve clearance), weak queries get filler
hits, e5 cosine scores sit in a narrow 0.80-0.90 band.
**Do.**
1. A **retrieval eval**: `tests/retrieval_eval/queries.json` (English) + `locales/tr.json` queries
   (≥ 40 per locale) with the expected source ids (catalog fault id or doc path#section), and a
   runner `vehicle-mcp-index eval --db ...` printing recall@1/@3/@5 and MRR per locale. Build the
   eval index from the live server catalog + `vehicle-defs/docs/ideas/*.md` (index file in
   git-ignored `local/knowledge/`; server on http://127.0.0.1:8000 if running, token from
   `local/secrets/mac-local-demo-session.txt`, never print it). Record the **baseline** numbers.
2. Improvements, each measured against the baseline and kept only if it helps:
   (a) Turkish-aware FTS tokenisation: a light suffix-stripping stemmer driven by a suffix list in
   `locales/tr.json` (no new dependency), applied to both index and query for `locale=tr` chunks;
   (b) a **relative score cutoff** (drop hits whose fused score is below x × best, x tuned on the eval)
   and an absolute floor on vector similarity so weak queries return fewer hits;
   (c) query expansion with the existing complaint synonyms (`locales/en.json` `synonyms`).
3. Unit tests with the synthetic corpus and fake embedder (no model download in CI); the spec-size
   budget test must stay green.
**Done when:** PR body has a baseline vs after table (recall@1/@3, MRR per locale); CI green.

### G2-3 Conversation list and memory UI (vehicle-mobile, D-128, D-130, T47)

**Context.** vehicle-server main has stored conversations (server#103):
`POST /chat` takes `conversation_id` and `temporary`, returns `conversation_id` and `chips`;
`GET/PATCH/DELETE /conversations`, `GET /conversations/{id}`, `GET /conversations/search?q=`,
`GET /conversations/export`, `GET/PUT/DELETE /assistant/memory`. Read the server README rows for
exact shapes.
**Do.**
1. Assistant screen: a conversation list (phone: a sheet/drawer from the header; ≥ 900 px: a left
   column inside the assistant pane), new chat, rename, delete (with confirm), search, a "temporary
   chat" toggle (nothing stored), continue a chat by `conversation_id`, show `chips` as tappable
   follow-ups under the latest answer.
2. Settings → "Assistant memory": list facts, edit value, delete one, delete all (confirm), and
   "Export my chats" (downloads the JSON on web, share sheet on phone).
3. **Fix:** the in-ride `AlertBanner` currently overlays the page header (title and model chip
   hidden). Make it push the content down while visible instead of covering it.
4. Follow D-130 (graphite, one teal accent, no bubbles/avatars, Instrument Sans + Barlow Semi
   Condensed numbers) and the ARB flow (`l10n_src/parts/*` → `python3 tool/l10n_merge.py` →
   `flutter gen-l10n`); English default, Turkish second.
5. Widget tests with fakes for every new flow. Flutter SDK: `~/development/flutter/bin`.
**Done when:** `flutter analyze` clean, `flutter test` green, `flutter build web --release --base-href /app/` ok.

### G2-4 Base-model bake-off harness (vehicle-ml, D-132 stage 0, T58)

**Do.** `ride_llm/bakeoff/` with a CLI `python -m ride_llm.bakeoff run --models ... --locales en tr`
that, for each model: starts `llama-server` (path from config/env; `-c 4096 -np 1`) on a free port
with the given GGUF, starts nothing else, runs `vehicle-server chat-eval` against an
already-running vehicle-server whose `VEHICLE_LLM_URL` the user points at that port (document the
two-terminal procedure; do not modify vehicle-server), plus your held-out set from run 1 if
present, and collects tool accuracy, fact coverage, forbidden hits, guard failures and p50/p95 into
one comparison table (Markdown + JSON) under git-ignored `ride_llm/bakeoff/out/`.
Model list (config file, with the official repo URLs and **SHA-256 to verify after download**;
download into `local/models/` outside git, never commit weights): Qwen2.5-1.5B-Instruct Q4_K_M,
Qwen3-1.7B Q4_K_M, Qwen3-4B Q4_K_M (official `Qwen/*-GGUF` repos only; note each licence).
Unit tests with fakes (no model download in CI). Run it once on the Mac if the user has the models;
otherwise leave the run instructions in the PR.
**Done when:** ruff + pytest green; README section with the exact procedure.

### G2-5 Validation plan draft (vehicle-defs `docs/ideas/validation-plan.md`)

**Write** an English idea note (not a decision; the first line says "Status: idea note, not a
decision") answering: which result of the platform is proven by which kind of data. Sections:
(1) the evidence levels — synthetic scenarios, HIL/restbus fault injection (`vehicle-hil-bench`),
recorded real rides, real faults with labels; (2) for each claim (alert rules thresholds, anomaly
model D-083, fault catalog matching, assistant tool accuracy and safety, lane keeping later) what
counts as evidence and what does not (synthetic data cannot validate thresholds: circular);
(3) a protocol for the user's first real rides (what to record, how many, which conditions,
false-alarm rate of the PROVISIONAL alert rules by replay); (4) safe fault injection only on the
bench/HIL, never by writing to the ECU (invariant 1) and never by disabling safety hardware;
(5) how each `docs/test-results/` write-up must label its data (synthetic / bench / real).
Cite standards only with what you can verify (ISO 26262 fault injection, ASAM OpenSCENARIO) and add
URLs. Max ~250 lines. Link it from the `ideas/*` row of `docs/README.md` only if that file is green
for you — it is **yellow** (`docs/*`), so put the README change in the same PR with
`needs-claude-review` at the top of the body.

### G2-6 Close the log

Fill the log (per task: branch, PR, numbers, what was skipped, *For Claude*), commit, push.
