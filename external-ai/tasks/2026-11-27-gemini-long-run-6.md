# Gemini long run 6 — 2026-11-27 (cache measurement round 2, marks in the assistant, marks label export, multi-node SIL note, analyzer tests, rider-facing labels)

Written by Claude for Gemini CLI. Runs 1-5 are reviewed and merged. Start from an up-to-date `main` in
every repo (`git switch main && git pull --ff-only && git submodule update --init`). Run the tasks in
order without asking between them; do not stop and do not wait for an answer. One branch and one PR
per task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>`
trailer), push after every commit, update and push the log after every task. If a task makes no
progress for about 90 minutes, write why in *For Claude*, push what is done and go on. **Never merge a
PR. Never force-push.**

Order: G6-0, G6-1, G6-2, G6-3, G6-4, G6-5, G6-6, and G6-9 **last**.

| Task | Repo / path | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G6-0 and G6-9 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-6-log` | green |
| G6-1 | vehicle-defs `docs/test-results/chat-eval/` (results page only) | `ext/gemini-cache-round2` | green |
| G6-2 | vehicle-server `src/vehicle_server/chat/` (router, templates, locales), `chat/eval/` (dev set only), `tests/` | `ext/gemini-chat-marks` | green |
| G6-3 | vehicle-server `cli.py`, new `marks_export.py`, `tests/`, `README.md` | `ext/gemini-marks-export` | green |
| G6-4 | vehicle-defs `docs/ideas/multi-node-sil.md` | `ext/gemini-multi-node-sil` | green |
| G6-5 | vehicle-analyzer `tests/` | `ext/gemini-analyzer-tests-3` | green |
| G6-6 | vehicle-mcp (`tools.py`, `knowledge/`, tests) | `ext/gemini-mcp-labels` | **yellow** (`needs-claude-review`) |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every path in
vehicle-defs outside `docs/`, `vehicle-analyzer/src/services/webSerialCan*`, `src/services/udsComposer*`,
`src-tauri/*`, every `*ota*` path. Before every push: `python3 scripts/check_zones.py <repo> --base
origin/main` (exit 2 = red path → revert it, note it in *For Claude*).

## 0. Rules for every task

- Read first: `GEMINI.md` (its §3 hard rules are the lessons of runs 1-5), then `STATUS.md`, then the
  target repo's `CLAUDE.md` (read only) and the decisions named in the task (search them in
  `vehicle-defs/docs/DECISIONS.md`; never read whole large docs).
- **Lessons of run 5, all of them review findings — do not repeat them:**
  1. A doc "update" never deletes still-true content. Condense or move it; list every removed fact in
     the PR body with the reason (the code no longer does it, with the file).
  2. A timeout, auto-close or retry never discards a choice or text the user already entered.
  3. Counts and totals are computed over the full data, not over a truncated list; one value appears
     once (no `x_s` next to a quantity `x`); a missing input gives a `warnings` entry, never a silent
     `None`; an unknown category is its own bucket, never merged into `other`.
  4. A scripted multi-step run (conversation, retry chain) stops at the first failed step and marks the
     remaining steps as not run; cleanup in `finally` never masks the original error.
  5. A copied path, flag or rule in a doc is checked against the source it names (`ls`, `grep`), and a
     rule sentence is never reworded into a different rule.
  6. Every diagram arrow and every "who sends what on which bus" sentence is checked against the code
     or the DBC.
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish appears
  only in locale resource files (`*/locales/tr.json`, `*.arb`, `l10n_src/parts/*.tr.json`).
- **Public repos (D-033):** no personal data, no `/Users/...` paths, no tokens, no real ride or position
  data in any commit.
- No new runtime dependencies. Mirror every step of each repo's CI locally before pushing (read the
  workflow files; include type-checks of tests and build steps); all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G6-0 Log

Create `external-ai/log/2026-11-27-gemini-long-run-6.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G6-1 Prompt-cache measurement, round 2 (roadmap card T72, measure only)

Run 5 measured multi-turn prompt caching with too few LLM-timed turns (11-14 of 35, none on turn 4) to
conclude anything. Prerequisite: vehicle-server `main` contains the multi-turn eval of vehicle-server#110
(`conversation`/`turn` items in `chat/eval/spec.json`, `by_turn` in the report). If it does not, skip
G6-1 and say so in the log.
1. **Read before measuring** (`chat/service.py`, `chat/llm.py`, `chat/providers/`): list every
   llama-server call one `/chat` turn can make (tool choice, phrasing, any other) with its system prompt
   source, and state which call's `timings` the `/chat` response reports. Write this list on the
   results page; if it is not clear from the code, say so instead of guessing.
2. Two arms on `qwen2.5-1.5b-instruct-q4_k_m`, same server, llama-server restarted before each arm:
   **A** = `local/run-llama.sh` (`-np 1 -c 4096`); **B** = the same binary and model started by hand with
   `-np 2 -c 8192` (the context is split per slot, so B keeps 4096 tokens per slot). Server from
   `local/run-server.sh`. Do not edit anything under `local/`.
3. Per arm and locale (en, tr): run the ten multi-turn conversations three times
   (`chat-eval --only mt-01,...,mt-10`, three separate runs). Report per turn and arm: n, LLM-timed n,
   cached share, `prompt_ms` p50/p95. Count only LLM-timed turns in cache numbers and always print n.
4. Results page `vehicle-defs/docs/test-results/chat-eval/2026-11-27-multiturn-cache-round2/README.md`
   (`Provenance: synthetic`, commands, server and llama commits, the table, the call list of step 1),
   plus the English summary Markdown files. Commit raw results JSON only for the English runs. A
   conclusion is allowed only where the same run's numbers show it; otherwise write "not shown" and the
   next hypothesis. No prompt, router, template or server change in this task.

### G6-2 Ride marks in the rider assistant (vehicle-server, D-133 item 4, T65)

vehicle-mcp now has the read-only tool `get_ride_marks(session_id)` (labelled `mark_count` and per-kind
counts, the mark list with an `offset` quantity, `kind`, `note` wrapped as untrusted text, `warnings`,
`truncated`). Make `/chat` use it:
1. Router: en and tr keyword routes in the existing locale route tables (`chat/router.py`
   `load_routes()` and its locale source) for questions such as "did I mark anything on my last ride",
   "what did I mark", "show my marks". The ride is resolved exactly as the other ride-bound tools do
   (last ride, follow-ups through `chat/followup.py`); reuse that code. If the tool is not in the
   tool list of the connected vehicle-mcp (older server), fall back as the other routes do.
2. Answer: **template only**, never LLM phrasing (`answers.uses_llm` returns false for this tool),
   because the note is rider-written untrusted text. The template gives the count, the counts per kind
   (kind names through the locale labels, never the raw `snake_case`), and up to five marks as
   "offset — kind" using the existing duration formatting of `rider_text.py`. A note is shown only as
   a quoted string, truncated to 80 characters, never interpreted. Zero marks has its own sentence.
   `warnings` and `truncated` get one short sentence each.
3. Chips/follow-ups: if the chips table has a pattern for ride-bound answers, add one for marks;
   otherwise none.
4. Eval: add new **dev** items only (at least 6 per locale, written new): marks on the last ride,
   marks on an older ride, zero marks, a follow-up after a ride summary ("and did I mark anything?").
   Do not touch held-out files or existing items.
5. Tests: routing en/tr, template with 0, 1 and > 5 marks, a note with an injection attempt is quoted
   and truncated, unknown kind uses a neutral label, tool missing → fallback, `uses_llm` false.

### G6-3 Marks label export for training (vehicle-server CLI, D-133 item 4, T65)

**Proposed** offline export so vehicle-ml can read marks as weak labels later:
`vehicle-server marks export --out <file.jsonl> [--owner <principal>] [--from <date>] [--to <date>]
[--include-notes]`. One JSON line per mark that falls inside a stored session window (the same window
rule as `GET /rides/{ride_id}/marks`; reuse `marks.py`, never a second window computation):
`{session_id, mark_id, offset_s, kind, has_note, note?}`; `note` only with `--include-notes` (notes may
hold personal text). Marks outside every session are counted and reported on stderr, not exported.
No position, no owner token in the output. Exit 1 on an unreadable data dir or a bad date. README:
a short "Marks export (proposed)" section. Tests: inside/outside window, both window ends inclusive,
notes excluded by default, `--owner` filter, empty store, bad date.

### G6-4 Multi-node SIL design note (vehicle-defs `docs/ideas/multi-node-sil.md`, roadmap card T69)

From `docs/ideas/sil-inventory.md` (run 4) and the code, write a **proposed** design for one SIL run
with the rt-core host build, the safety-node host build and vehicle-server (mock or recorded live input)
on one virtual bus: `vcan` on Linux CI, an in-process or UDP bus on macOS (check what each repo's host
port already supports: `src/hal/host/`, `HAVE_SOCKETCAN`, `sim_safety`). Cover: which platform-bus
messages each node sends and receives (message **names** from `dbc/platform.dbc` with the file
reference; IDs only if quoted from that file), time base per node (Q-008 is open: list the options,
decide nothing), how a scenario is started and judged (reuse the hil-bench scenario YAML idea if it
fits), CI cost, and gaps. Every fact cites its file; every design choice is marked **proposed**.

### G6-5 Analyzer tests, third pass (vehicle-analyzer `tests/`)

Run `npm run test:coverage` and list every module under 80 % lines. Add tests for as many of them as
fit (run 4 named canvas rendering and file import), mocking only at module boundaries; tests only, no
change under `src/`. Tests must assert behaviour (a state change, an output, an error path), not that
a mock was called with what the test passed in. Type-check the tests (`npx tsc -p tests/tsconfig.json
--noEmit`, `npx tsc -p ui-tests/tsconfig.json --noEmit`), lint, coverage, build. Report the per-module
before/after table in the PR. Do not change the coverage thresholds (Claude ratchets them).

### G6-6 No internal identifiers in rider-facing tool output (vehicle-mcp, yellow, T58 follow-up)

The bake-off saw `snake_case` identifiers in answers built from `search_knowledge` and `explain_context`
results (not verified). Check it:
1. Add a test that runs every tool on the existing test fixtures and collects each rider-facing text
   field (`label`, `title`, `summary`, `text` and the like; read the tools to find them) and fails on a
   token matching `\b[a-z]+(_[a-z0-9]+)+\b` or a dotted `did.`/`sensor.` name. Machine fields (`name`,
   `kind`, ids, `source`) are exempt; list the exempt field names in the test.
2. Fix the hits that come from this repo's own text (use the existing label sources; reuse, do not add
   a second label table). A hit whose text comes from vehicle-defs (generated labels, catalog phrases,
   docs chunks) is **not** fixed here: list it in *For Claude* with the defs file it comes from.
3. Do not change retrieval, ranking, cutoffs or the RAG eval splits.

### G6-9 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the `review: pending`
line (Claude closes it), commit, push, open the log PR.
