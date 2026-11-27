# Gemini long run 7 — 2026-11-27 (visibility inventory, time-sync options, cache round 3, marks weak labels, VSS two-wheeler draft)

Written by Claude for Gemini CLI. Runs 1-6 are reviewed and merged. Start from an up-to-date `main` in
every repo (`git switch main && git pull --ff-only && git submodule update --init`). Run the tasks in
order without asking between them; do not stop and do not wait for an answer. One branch and one PR
per task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>`
trailer), push after every commit, update and push the log after every task. If a task makes no
progress for about 90 minutes, write why in *For Claude*, push what is done and go on. **Never merge a
PR. Never force-push. Never publish anything outside the vehicle-platform org** (no upstream issues,
no comments on other projects, no forum posts).

Order: G7-0, G7-1, G7-2, G7-3, G7-4, G7-5, and G7-9 **last**.

| Task | Repo / path | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G7-0 and G7-9 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-7-log` | green |
| G7-1 | vehicle-defs `docs/ideas/visibility-inventory.md` | `ext/gemini-visibility-inventory` | green |
| G7-2 | vehicle-defs `docs/ideas/time-sync-options.md` | `ext/gemini-time-sync` | green |
| G7-3a | vehicle-server `src/vehicle_server/chat/eval/` (dev items only), `tests/` | `ext/gemini-mt-llm-turns` | green |
| G7-3b | vehicle-defs `docs/test-results/chat-eval/` (results page only) | `ext/gemini-cache-round3` | **yellow** (`needs-claude-review`) |
| G7-4 | vehicle-ml `src/vehicle_ml/` (new module), `tests/` | `ext/gemini-marks-labels` | green |
| G7-5 | vehicle-defs `docs/ideas/upstream-vss-two-wheeler.md` | `ext/gemini-vss-two-wheeler` | green |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every path in
vehicle-defs outside `docs/`, every `*ota*` path, anything under `local/` in the workspace. Before every
push: `python3 scripts/check_zones.py <repo> --base origin/main` (exit 2 = red path → revert it, note it
in *For Claude*). Use the zone the script prints; if it differs from this table, the script wins and you
add `needs-claude-review` for yellow.

## 0. Rules for every task

- Read first: `GEMINI.md` (its §3 hard rules are the lessons of runs 1-6; run 6 added "totals
  reconcile", "untrusted text stays quoted on every path" and "examples in docs must work"), then
  `STATUS.md`, then the target repo's `CLAUDE.md` (read only) and the decisions named in the task
  (search them in `vehicle-defs/docs/DECISIONS.md`; never read whole large docs).
- **Lessons of run 6, all of them review findings — do not repeat them:**
  1. Follow a value past the place you render it: what is stored is often fed back later (conversation
     history, caches, exports). Untrusted text must not reach an LLM on any of those paths.
  2. A breakdown adds up to its total; never count a truncated list.
  3. A missing input (no database, no table, no file) is a warning or an error, never a silent empty
     result.
  4. Do not write "observed" for something nobody measured. Quote the measurement and its file.
  5. Every number in an example (durations, thresholds) is checked against its source file, and the
     example must be able to produce what it claims.
  6. Identifiers in examples exist in vehicle-defs or in the code; if none fits, describe the check in
     words.
  7. Python imports that cross a module use the package name (`from vehicle_x.mod import y`), never
     `from ..mod` (D-107).
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish appears
  only in locale resource files (`*/locales/tr.json`, `*.arb`, `l10n_src/parts/*.tr.json`).
- **Public repos (D-033):** no personal data, no `/Users/...` paths, no tokens, no real ride or position
  data in any commit.
- No new runtime dependencies. Mirror every step of each repo's CI locally before pushing (read the
  workflow files; include type-checks of tests and build steps); all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G7-0 Log

Create `external-ai/log/2026-11-27-gemini-long-run-7.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G7-1 Repository visibility inventory (vehicle-defs `docs/ideas/visibility-inventory.md`, card T76, D-135)

Inventory only: **move, rename, delete or rewrite nothing**, change no repo setting.
1. List, per repo, the files and directories that are vehicle-specific or commercially sensitive:
   reverse-engineered CL250 facts (`dbc/cl250.dbc`, `uds/vehicle_cl250.yaml`, CL250 entries in other
   defs files, generated code that embeds them under `gen/` in vehicle-defs and in each consumer's
   pinned submodule), CL250 constants or fixtures in consumer repos (grep for the CL250 CAN IDs and DIDs
   **as they appear in the defs files**, and for `cl250`), the archived `HondaCl250_Telemetry`, and
   anything model- or customer-specific. One table row per path: repo, path, what it holds, why it is
   sensitive, which public code needs it at build or test time (cite the file that reads it).
2. Per row, mark what a public build would need instead: nothing, the generic catalog, or a synthetic
   example vehicle. Mark every such suggestion **proposed**.
3. Note the constraints D-135 and the card name (Free plan: 2,000 Actions minutes/month for private
   repos, no rulesets on private repos; content already public stays in clones and forks). Decide
   nothing; list the open questions for the user at the end.

### G7-2 Time synchronisation options (vehicle-defs `docs/ideas/time-sync-options.md`, Q-008)

Q-008 is open and must stay open. Write the options so Claude and the user can decide before the
boards arrive.
1. Per node (rt-core H743, safety-node G474, connectivity ESP32-S3, linux-node Pi 5, phone, server):
   which clock it has today and where its timestamps come from. Cite the code (`hal_time*`, the
   telemetry/session timestamp fields, `device_time_ms`, the server's receive-time use in
   `alerts/service.py`) and the docs (`hardware-architecture.md` §5b.8, read only that section).
2. Options, each with what it needs on which node, accuracy class, failure behaviour (what happens
   when the time source is missing), and cost: at least (a) rt-core as time master with a periodic
   platform-bus time frame, (b) GNSS time + PPS into rt-core, (c) NTP/chrony on the Pi with the MCUs
   following rt-core, (d) no common clock, per-node monotonic time plus offsets estimated after the
   ride. For (a): check `dbc/platform.dbc` for an existing time message and quote it exactly; if there is
   none, say so and **do not** invent a message name or ID.
3. Constraints to respect: the safety node must work without any time source (invariant 3, D-042); the
   ECU bus stays read-only (invariant 1). A table of which consumers need which accuracy (logging
   alignment, sensor fusion, ride marks matching `t_utc`, multi-node SIL from
   `docs/ideas/multi-node-sil.md`). Everything **proposed**; no recommendation is final.

### G7-3 Prompt-cache measurement, round 3 (card T72, measure only)

Round 2 (`docs/test-results/chat-eval/2026-11-27-multiturn-cache-round2/`) showed two confounders:
llama-server kept prompts across runs, and no turn after turn 3 used the LLM.
- **G7-3a (vehicle-server, dev eval only):** add five new multi-turn dev conversations `mt-11`..`mt-15`
  per locale (en, tr) whose turns 2-4 go through LLM phrasing on the current code (read
  `answers.uses_llm` and `chat/router.py` to pick questions that do: for example `compare_sessions`
  and symptom checks that match a catalog entry). Do not touch held-out files or existing items. Add a
  test that each new conversation has at least two turns that are not answered by a template
  (check with the existing eval helpers or a fake LLM, not with a real model). Open the PR, then go on;
  G7-3b runs from this branch's commit.
- **G7-3b (vehicle-defs results page):** two arms as in round 2 (A `-np 1 -c 4096` via
  `local/run-llama.sh`, B `-np 2 -c 8192` started by hand) on `qwen2.5-1.5b-instruct-q4_k_m`, but
  **restart llama-server before every single run and every locale** (state the restart in the page).
  Run `--only mt-01,...,mt-15` three times per arm and locale. Report per turn and arm: n, LLM-timed n,
  cached share, `prompt_ms` p50/p95, plus wall time per run. Results page
  `docs/test-results/chat-eval/2026-11-27-multiturn-cache-round3/README.md` (`Provenance: synthetic`,
  commands, server branch commit, llama commit, the tables) plus English summary Markdown files; raw
  JSON only for the English runs. A conclusion only where the same run's numbers show it; otherwise
  "not shown" and the next hypothesis. Do not edit anything under `local/`.

### G7-4 Ride marks as weak labels (vehicle-ml, proposed, D-133 item 4, card T65)

vehicle-server now writes `vehicle-server marks export` JSON lines
`{session_id, mark_id, offset_s, kind, has_note, note?}` (see vehicle-server `README.md` "Marks export
(proposed)" and `src/vehicle_server/marks_export.py`). Add a reader in vehicle-ml:
1. New module `src/vehicle_ml/marks.py`: `load_marks(path) -> list[Mark]` (validates every line; a
   bad line is reported with its line number, never skipped silently; an unknown `kind` is its own
   bucket; `note` is **ignored** even when present: training never reads rider text) and
   `label_windows(marks, windows, before_s, after_s)` that maps each mark onto the existing `Window`
   objects of `windows.py` (`session_id`, `start_ms`, `end_ms`; reuse them). First find out which time
   axis `start_ms`/`end_ms` use (read `make_windows` and `dataset.py`) and how a mark's `offset_s`
   (seconds from the ride start of the server's window rule) maps onto it; write that mapping in the
   module docstring with the file references, and if the code does not make it clear, stop this
   task and put the question in *For Claude* instead of guessing. It returns
   per-window weak labels plus counts of marks that hit no window and of windows hit by more than one
   mark.
2. A CLI subcommand in the existing `cli.py` style that prints the counts per kind and the unmatched
   count, reading only local files.
3. Tests on synthetic fixtures under `tests/`: valid file, bad line, unknown kind, note ignored,
   mark on a window edge (both ends inclusive, as the server's window rule), mark outside all windows,
   two marks in one window, empty file. Mark the module docstring **proposed**; no model or training
   change in this task.

### G7-5 COVESA VSS two-wheeler draft (vehicle-defs `docs/ideas/upstream-vss-two-wheeler.md`, card T74 item 1)

A **draft only**, kept in this repo; nothing is sent upstream (the user approves every submission).
1. From `vss/overlay.vspec` (our `Vehicle.Motorcycle` overlay), list the generic two-wheeler signals
   (lean angle with its quality/state, side stand, friction and mass estimates and similar); leave out
   platform-specific ones (node health, validity flags) and every CL250 DID or CAN ID.
2. For each, check whether the current COVESA VSS release already has an equivalent: name the release
   and the exact path you found, or "not found in <release>". If you cannot reach the upstream spec,
   write **CONFIRM** instead of guessing.
3. Draft the issue text (title, motivation, proposed branch and signals with type, unit, min/max,
   description) following the upstream CONTRIBUTING rules; cite where you read them, or mark
   **CONFIRM**. End with the open questions for the user.

### G7-9 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the `review: pending`
line (Claude closes it), commit, push, open the log PR.
