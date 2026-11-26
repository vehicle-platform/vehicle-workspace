# Gemini long run 4 — 2026-11-27 (parked-current note, 3-model bake-off, prompt-cache measurement, ride event marks)

Written by Claude for Gemini CLI. Run 3 is under Claude review (vehicle-ml#32, vehicle-defs#207,
vehicle-server#105). Run the tasks in order without asking between them. One branch and one PR per
task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>` trailer),
push after every commit. If a task is blocked, write why in the log's *For Claude* section and go on
to the next one. **Never merge a PR. Never force-push.**

**Start gates (check, do not wait idle):** G4-1 and G4-2 start only when `gh pr view 32 -R
vehicle-platform/vehicle-ml --json state` and `gh pr view 207 -R vehicle-platform/vehicle-defs --json
state` both say `MERGED`; G4-3 and G4-4 only when `gh pr view 105 -R vehicle-platform/vehicle-server
--json state` says `MERGED`. If a gate is closed, do the next open task and come back. Before each task
`git switch main && git pull --ff-only` in the target repo (Claude's review moves the checkouts back to
`main`).

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G4-0 (first!) and G4-5 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-4-log` | green |
| G4-A (no gate, do it first) | vehicle-defs `docs/ideas/parked-current.md` | `ext/gemini-parked-current` | **yellow** (`needs-claude-review`) |
| G4-1 | vehicle-ml (run; code only if the run needs a fix) | `ext/gemini-bakeoff-3models` | green |
| G4-2 | vehicle-defs `docs/test-results/ride-llm-bakeoff/` | `ext/gemini-bakeoff-3models-results` | **yellow** (`needs-claude-review`) |
| G4-3 | vehicle-server `src/vehicle_server/chat/` (prompt assembly, llm client), `tests/` | `ext/gemini-prompt-cache` | green |
| G4-4 | vehicle-server (marks API + storage) and vehicle-mobile (UI) | `ext/gemini-ride-marks` (one per repo) | green (server: do not touch `*ota*`, `*gps*`, `*position*`, `*mdf4*`) |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every other path in
vehicle-defs outside `docs/`. Before every push: `python3 scripts/check_zones.py <repo> --base origin/main`
(exit 2 = red path → revert it, note it in *For Claude*).

## 0. Rules that apply to every task

- Read first: `GEMINI.md`, `STATUS.md`, then the target repo's `CLAUDE.md` (read only) and the
  decisions named in the task (search them in `vehicle-defs/docs/DECISIONS.md`; never read whole
  large docs).
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish
  appears **only** in locale resource files (`*/locales/tr.json`, `*.arb`).
- **Invariant 2:** signal names, DIDs, units and scales come only from the generated defs package.
  **Invariant 7:** the LLM never computes; numbers come from tools.
- **Public repos (D-033):** no model weights, no real GPS/ride data, no personal data (no usernames,
  no `/Users/...` paths, no hostnames, no tokens) in any commit. Models stay in `local/models/`.
- No new runtime dependencies. Mirror each repo's CI locally before pushing; all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

**Lessons from the run 1-3 reviews (Claude fixed these every time; get them right first):**
1. Never tune thresholds, keywords, prompts or templates on an evaluation set; held-out items are
   read-only, and a cutoff is chosen on a separate split.
2. Every value with a meaning (signal, unit, range, threshold) comes from vehicle-defs, never from a
   copied number or an older defs version.
3. Write proposals as proposals. Targets, recommendations and design choices are marked
   **proposed**; only measured or cited facts are stated plainly. Never pick a winner model.
4. Handle the unhappy path: errors surfaced (not swallowed), late async replies dropped, temp files
   removed, timeouts, empty/missing inputs fail loudly. Each gets a test.
5. Reuse the existing module (HTTP transport, locale loader, storage layer) instead of a new copy.
6. Every number in a doc has a source (datasheet + section/table, or the command that produced it).

## Tasks

### G4-0 Log

Create `external-ai/log/2026-11-27-gemini-long-run-4.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G4-A Parked (key-off) current note (vehicle-defs `docs/ideas/`, yellow, roadmap card T73)

The CL250 battery must survive days parked with our nodes fitted. Write
`docs/ideas/parked-current.md` (style of the other `docs/ideas/*.md`):

1. Table per node: Raspberry Pi 5 (halted, with and without `POWER_OFF_ON_HALT`), ESP32-S3 (deep and
   light sleep, with BLE advertising if documented), STM32H743 (Stop, Standby), STM32G474 (Stop,
   Standby, Shutdown), the CAN transceivers listed in the BOM (standby), IMU in sleep — each value
   with its datasheet/document and section/table. Board-level extras (regulators, LEDs, ST-LINK on
   the NUCLEO) are listed as unknown-until-measured, not guessed.
2. Battery: capacity of the CL250 battery from the manuals in `~/Desktop/vehicle-refs/` (local, never
   commit or quote pages; cite document + page) and the days-parked arithmetic as a formula with the
   inputs shown. Mark estimates as estimates.
3. Options (all **proposed**): who wakes whom on key-on, what stays powered, a measurement procedure
   for when the boards arrive. No decision; Claude records any D-xxx.

### G4-1 Three-model bake-off (vehicle-ml, D-132 stage 0, T58) — gate: ml#32 + defs#207 merged

1. Download from the **official** `Qwen/*-GGUF` repos into `local/models/`: `Qwen3-1.7B-Q8_0.gguf`
   and `Qwen3-4B-Q4_K_M.gguf`. `uv run python -m vehicle_ml.ride_llm.bakeoff verify --models all
   --models-dir ../local/models` must pass (SHA-256 against `models.json`); a mismatch stops G4-1/G4-2.
   If the download fails again, note it and skip to G4-3.
2. Run all three models, `--locales en tr`, dev + held-out, against `local/run-server.sh` (mock data
   only), one `llama-server` at a time (`-np 1`), with the scorer as merged in ml#32 (Claude's review
   changed it; use `main`). Raw output stays git-ignored. Same metrics as run 3.
3. Commit only harness fixes (each with a test); otherwise no PR for G4-1.

### G4-2 Results page (vehicle-defs `docs/test-results/ride-llm-bakeoff/`, yellow) — gate as G4-1

New folder `2026-11-27-stage0-3models/` in the exact style of the merged `2026-11-26-stage0/`
(read it and Claude's edits to it first): `Provenance: synthetic`, setup with SHA-256 and commit SHAs,
per-locale tables, `safety_red_team` table, the same caveats, facts-only "Reading", no winner,
`summary.json` ≤ 20 KB, no raw answers, no personal data.

### G4-3 Prompt-cache measurement (vehicle-server, roadmap card T72) — gate: server#105 merged

`chat/wiring.py` already sends llama.cpp's `cache_prompt`. Measure whether it actually helps:

1. Record llama-server's per-response `timings` (`prompt_n`, `cache_n`, `prompt_ms`, `predicted_ms`)
   in the chat-eval report when present (absent → `n/a`, never a crash).
2. Run the dev suite on `qwen2.5-1.5b` (en, tr) and report the cached share of prompt tokens and
   time-to-first-token p50/p95.
3. If dynamic content (memory facts, ride data, the user turn) sits before the static system prompt
   or tool specs and so breaks the cached prefix, reorder the prompt assembly so the static part comes
   first and is byte-identical across requests. Keep it only if the **dev** suite tool accuracy and
   forbidden counts do not get worse (held-out is not used for this decision). Before/after numbers in
   the PR.

### G4-4 Ride event marks (vehicle-server + vehicle-mobile, roadmap card T68) — gate: server#105 merged

The rider taps a button during a ride to mark "something happened here"; marks become consented weak
labels for the anomaly model later (D-132 item 1a / T65). Data model (**proposed**, Claude records the
decision in review):

- A mark = `{id, t_utc (ms), kind, note?}`; `kind` ∈ `misfire, noise, vibration, warning_light,
  rough_road, traffic, other`; `note` ≤ 200 chars. **No position** in a mark (D-076); the time links
  it to the ride.
- Server: `POST /marks`, `GET /rides/{ride_id}/marks` (marks whose `t_utc` falls in that ride's time
  window), `DELETE /marks/{id}`; same auth and per-user isolation as the ride endpoints; stored through
  the existing storage layer with a migration; validation errors → 422; another user's mark → 404.
  Tests for each, including isolation.
- Mobile: a large glove-friendly "Mark" button on the live screen opens a quick picker (4 most common
  kinds + other) that closes itself after a few seconds; marks made offline are queued and retried
  (drop duplicates by `id`); the ride detail in the Logbook lists the marks with delete. Strings in
  the ARB files (en default, tr). Widget tests for the button, picker, queue and delete.
- One PR per repo; merge order server first (state it in both PR bodies).

### G4-5 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the
`review: pending` line (Claude closes it), commit, push, open the log PR.
