# Gemini long run 8 — 2026-11-28 (marks time axis, marks weak labels, RAG Turkish tune pass, label echo audit, guard recall, Kuksa macOS draft)

Written by Claude for Gemini CLI. Runs 1-7 are reviewed and merged. Start from an up-to-date `main` in
every repo (`git switch main && git pull --ff-only && git submodule update --init`). Run the tasks in
order without asking between them; do not stop and do not wait for an answer. One branch and one PR
per task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>`
trailer), push after every commit, update and push the log after every task. If a task makes no
progress for about 90 minutes, write why in *For Claude*, push what is done and go on. **Never merge a
PR. Never force-push. Never publish anything outside the vehicle-platform org** (no upstream issues,
no comments on other projects, no forum posts).

Order: G8-0, G8-1, G8-2, G8-3, G8-4, G8-5, G8-6, and G8-9 **last**.

| Task | Repo / path | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G8-0 and G8-9 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-8-log` | green |
| G8-1 | vehicle-server `src/vehicle_server/marks_export.py`, `README.md`, `tests/` | `ext/gemini-marks-device-time` | green |
| G8-2 | vehicle-ml `src/vehicle_ml/` (new module + CLI), `tests/` | `ext/gemini-marks-labels` | green |
| G8-3a | vehicle-mcp `src/vehicle_mcp/knowledge/` (parameters only), `tests/` | `ext/gemini-rag-tr-tune` | **yellow** (`needs-claude-review`) |
| G8-3b | vehicle-defs `docs/test-results/rag/` (results page only) | `ext/gemini-rag-tr-results` | green |
| G8-4 | vehicle-mcp + vehicle-server answer templates and label maps | `ext/gemini-label-echo` (one per repo) | yellow (mcp) / green (server) |
| G8-5 | vehicle-server `src/vehicle_server/chat/eval/` (dev items only), results under vehicle-defs `docs/test-results/chat-eval/` | `ext/gemini-guard-recall-tr` | green |
| G8-6 | vehicle-linux-node `docs/` (new draft only) | `ext/gemini-kuksa-macos-draft` | yellow (`needs-claude-review`) |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every path in
vehicle-defs outside `docs/`, every `*ota*` path, anything under `local/` in the workspace, and the chat
refusal guard itself (`vehicle-server` `chat/guard*` or wherever `answers`/`router` refuse ECU-write
requests: read it, never change it). Before every push: `python3 scripts/check_zones.py <repo> --base
origin/main` (exit 2 = red path → revert it, note it in *For Claude*). Use the zone the script prints;
if it differs from this table, the script wins and you add `needs-claude-review` for yellow.

## 0. Rules for every task

- Read first: `GEMINI.md` (its §3 hard rules are the lessons of runs 1-7), then `STATUS.md`, then the
  target repo's `CLAUDE.md` (read only) and the decisions named in the task (search them in
  `vehicle-defs/docs/DECISIONS.md`; never read whole large docs).
- **Lessons of run 7, all of them review findings — do not repeat them:**
  1. A document that lists sensitive values must not quote them. Name the kind ("the UDS physical CAN
     IDs", "the polled DIDs") and the file, never the literal values (D-135).
  2. Public results pages and committed raw JSON carry **no raw model answers**: drop the `answer`
     field (keep scores, ids, timings) before committing.
  3. Repeated runs of a deterministic replay are not independent samples. Say "n = 1 configuration,
     repeated k times" for anything that does not vary between runs; do not write "independent" or
     "confirming" for it.
  4. Every figure in a results page comes from a committed file or is marked "from a local log, not
     committed".
  5. Two numbers in one table row describe the same thing (run 7 mixed a 50 ms bus cycle with a 110 ms
     poll period in one cell). Check each against its own source.
  6. Reuse test fakes: before writing a fake LLM, tool runner or store, grep `tests/` for an existing
     one and extend it in a shared helper. A third copy is a finding.
  7. Facts you fetched from the web (release dates, counts) get the date you checked them and a
     "re-check before use" note.
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish appears
  only in locale resource files (`*/locales/tr.json`, `*.arb`, `faults/i18n/tr.yaml`,
  `l10n_src/parts/*.tr.json`) and in eval questions inside `chat/eval/locales/tr.json`.
- **Public repos (D-033):** no personal data, no `/Users/...` paths, no tokens, no real ride or position
  data in any commit.
- No new runtime dependencies. Mirror every step of each repo's CI locally before pushing (read the
  workflow files; include type-checks of tests and build steps); all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G8-0 Log

Create `external-ai/log/2026-11-28-gemini-long-run-8.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G8-1 Marks onto the device time axis (vehicle-server, D-133 item 5)

Read **D-133 item 5** first (added 2026-11-28; it answers the question you raised in run 7 G7-4).
1. In `vehicle-server marks export` (`src/vehicle_server/marks_export.py`), add per record
   `device_time_ms` (integer) and `time_kind` (the Parquet data kind the mapping used). Mapping:
   `device_time_ms = t_utc − median(rx_utc_ms − device_time_ms)` over the rows of that kind in the
   session's Parquet (`parquet.py` writes both columns). Pick the kind that `vehicle-ml`'s
   `dataset.py` uses as its base kind (read it, cite the line); fall back in a fixed, documented order.
2. No guessed value, ever: a session with fewer than a documented minimum of rows with both columns,
   or whose `device_time_ms` goes backwards (wrap or MCU reset), gets no `device_time_ms`/`time_kind`
   for its marks and one warning line on stderr naming the session and the reason (run 6 lesson: a
   missing input is a warning, never a silent empty result). Count these in the export summary.
3. Keep `offset_s` unchanged. Update the README section "Marks export" (the record format and the
   rule). Tests: synthetic Parquet with `device_time_ms` starting at 5 000 ms (not 0), a constant
   receive delay, jitter (median is robust to one outlier), a backwards jump, too few rows, a session
   without Parquet, and a mark before the first row (still mapped: the mapping is an offset, not a
   lookup).

### G8-2 Ride marks as weak labels (vehicle-ml, proposed, D-133 items 4-5, card T65)

The run 7 G7-4 task, now with the time axis settled. Build against the record format of G8-1 (do not
wait for its merge; use the format in D-133 item 5 and your G8-1 branch).
1. New module `src/vehicle_ml/marks.py`: `load_marks(path) -> list[Mark]` (validates every line; a bad
   line is reported with its line number, never skipped silently; an unknown `kind` is its own bucket;
   `note` is **ignored** even when present: training never reads rider text; a record without
   `device_time_ms` is counted as `unmapped`, never mapped from `offset_s`) and
   `label_windows(marks, windows, before_s, after_s)` over the existing `Window` objects of
   `windows.py` (reuse them): a window is labelled when
   `start_ms − before_s·1000 ≤ device_time_ms ≤ end_ms + after_s·1000` (both ends inclusive) and the
   session ids match. Return per-window weak labels plus counts: marks that hit no window, unmapped
   marks, windows hit by more than one mark. Module docstring: **proposed**, the rule, D-133 item 5.
2. A CLI subcommand in the existing `cli.py` style that prints counts per kind plus the unmatched and
   unmapped counts, reading only local files.
3. Tests on synthetic fixtures: valid file, bad line, unknown kind, note ignored, record without
   `device_time_ms`, mark on each window edge (with and without tolerance), mark outside all windows,
   two marks in one window, a mark whose session has no windows, empty file. No model or training
   change in this task.

### G8-3 RAG: Turkish → English retrieval, tune-only pass (card "RAG into /chat", step 1)

Today's test split: en R@5 0.92, tr 0.42 (`vehicle-mcp` `knowledge/eval_retrieval.py` and
`tests/retrieval_eval/`; find the results page it came from and cite it). Goal: understand and improve
Turkish queries against English documents **by parameters only**.
- **G8-3a (vehicle-mcp):** expose as settings (not new behaviour) whatever already exists in
  `knowledge/settings.py`, `search.py`, `embedder.py`: RRF `k`, the FTS/vector weights or top-k per
  arm, and the e5 query/passage prefixes (multilingual-e5 expects `query: ` and `passage: `; check what
  the embedder sends today and cite it). Defaults must reproduce today's numbers exactly (add a test
  that pins them). No new model, no translation step, no new dependency.
- **G8-3b (vehicle-defs results page `docs/test-results/rag/2026-11-28-tr-tune/README.md`):** run the
  existing retrieval eval on the **dev** split only for a small grid (prefix on/off, RRF `k` ∈ {10, 30,
  60}, vector-only vs. FTS-only vs. hybrid), report R@1/R@5/MRR per locale and per setting, and only
  then run the best dev setting **once** on the test split. Say which `faults/unconfirmed` chunks rank
  first for Turkish queries and why (FTS tokens vs. vector). `Provenance: synthetic`. A recommendation
  only where the dev numbers show it; the default change itself is Claude's.

### G8-4 Label echo audit (snake_case and catalog names in answers)

T58 found snake_case echoes in rider-facing answers. Audit, then fix in place:
1. List every template and label path that can put an internal identifier in front of a rider: the
   `search_knowledge` and `explain_context` result formatting in vehicle-mcp (`tools.py`, `explain.py`,
   `locales/`) and the server answer templates (`chat/answers*`, `chat/locales/*.json`). An internal
   identifier is `did.X`, `sensor.x`, `derived.x`, an upper-case catalog name, a snake_case name or a
   fault id shown without its label.
2. For each, show (in a test) a concrete input that produces the echo today, then fix it by using the
   existing humanised label maps (mcp#41 added them; reuse, do not add a second map). Where no label
   exists, fall back to a generic word in the locale file, never the raw name.
3. Tests per locale (en, tr). One PR per repo; the mcp PR is yellow.

### G8-5 Turkish refusal-guard recall (measure only, card T58)

The chat guard refuses requests to write, flash, clear or unlock the ECU. T58 measured weak Turkish
recall on ECU-flash phrasing. **Do not change the guard.**
1. Add 15 Turkish and 15 English **dev** eval items (`chat/eval/spec.json` + both locale files,
   topic `guard`) with varied phrasing: flash/remap/tune the ECU, clear fault codes, reset the
   immobilizer, change the rev limit, "write" a value, plus 5 per locale that must **not** be refused
   (reading a fault code, asking what remapping is). Follow the shape of the existing guard items.
2. Run the dev guard items on the deterministic path (no LLM needed if the guard is rule-based; check)
   and write `docs/test-results/chat-eval/2026-11-28-guard-recall/README.md` in vehicle-defs: recall
   and false-refusal rate per locale, and the list of missed phrasings by id (no rider data).
3. In *For Claude*: which patterns would catch the misses (Claude changes the guard).

### G8-6 Kuksa on macOS without CAN hardware (vehicle-linux-node `docs/`, draft, card T74 item 2)

A **draft only** for a later upstream Kuksa docs contribution; nothing is sent upstream.
`docs/upstream-kuksa-macos-replay.md`: how vehicle-linux-node#35 runs Kuksa databroker plus
kuksa-can-provider replay on macOS with colima and `--dumpfile` (read that PR and the repo files it
added; cite them), the host-network note, the exact versions used, and the steps as a reader would
follow them on a clean Mac. Every command must be one the repo already runs or documents; mark
anything you could not run yourself **CONFIRM**. No vehicle-specific CAN IDs or DIDs in the draft (use
the repo's synthetic example dump, or describe it in words). End with the open questions for the user
(where to submit, which account).

### G8-9 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the `review: pending`
line (Claude closes it), commit, push, open the log PR.
