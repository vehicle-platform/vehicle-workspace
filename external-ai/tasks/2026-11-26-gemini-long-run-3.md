# Gemini long run 3 — 2026-11-26 (bake-off run, held-out eval in chat-eval, Turkish routing coverage)

Written by Claude for Gemini CLI. Run 1 and run 2 are reviewed and merged (vehicle-ml#30/#31,
vehicle-server#104, vehicle-mcp#35, vehicle-mobile#55, vehicle-defs#206). Start from an up-to-date
`main` in every repo. Run the tasks in order without asking between them. One branch and one PR per
task; commit after every logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>` trailer),
push after every commit. If a task is blocked, write why in the log's *For Claude* section and go on
to the next one. **Never merge a PR. Never force-push.**

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G3-0 (first!) and G3-4 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-3-log` | green |
| G3-1 | vehicle-ml (run only, code fixes if the run needs them) | `ext/gemini-bakeoff-run` | green |
| G3-2 | vehicle-defs `docs/test-results/ride-llm-bakeoff/` | `ext/gemini-bakeoff-results` | **yellow** (PR body starts with `needs-claude-review`) |
| G3-3 | vehicle-server `src/vehicle_server/chat/eval/`, `chat/locales/`, `tests/` | `ext/gemini-chat-eval-heldout` | green (do not touch `*ota*`, `*gps*`, `*position*`, `*mdf4*`) |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every other path in
vehicle-defs outside `docs/`. Before every push: `python3 scripts/check_zones.py <repo> --base origin/main`
(exit 2 = red path → revert it, note it in *For Claude*).

## 0. Rules that apply to every task

- Read first: `GEMINI.md`, `STATUS.md`, then the target repo's `CLAUDE.md` (read only) and the
  decisions named in the task (search them in `vehicle-defs/docs/DECISIONS.md`; never read whole
  large docs).
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish
  appears **only** in locale resource files (`*/locales/tr.json`).
- **Invariant 2:** signal names, DIDs, units and scales come only from the generated defs package.
  **Invariant 7:** the LLM never computes; numbers come from tools.
- **Public repos (D-033):** no model weights, no real GPS/ride data, no personal data, no tokens in
  any commit. Model files stay in the git-ignored `local/models/`; logins stay in `local/secrets/`.
- No new runtime dependencies. Mirror each repo's CI locally before pushing (see its
  `.github/workflows/`); all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G3-0 Log

Create `external-ai/log/2026-11-26-gemini-long-run-3.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G3-1 Run the base-model bake-off (vehicle-ml, D-132 stage 0, T58)

Run 2 built the harness (`src/vehicle_ml/ride_llm/bakeoff/`) but skipped the live run because two
models were missing. Do the run now.

1. Download the registered weights from the **official** `Qwen/*-GGUF` repos only into
   `local/models/` (workspace root, git-ignored): `Qwen3-1.7B-Q8_0.gguf` and `Qwen3-4B-Q4_K_M.gguf`.
   `qwen2.5-1.5b-instruct-q4_k_m.gguf` is already in `local/pi/models/`: copy it, do not download it
   again. Then `uv run python -m vehicle_ml.ride_llm.bakeoff verify --models all --models-dir ../local/models`
   must pass (SHA-256 against `models.json`). A mismatch stops the task.
2. Start the server with the mock stack: `local/run-server.sh` (synthetic data in
   `local/server-data`, never real rides). Follow the two-terminal procedure in `vehicle-ml/README.md`
   and run all three models for `--locales en tr` with the held-out set
   (`src/vehicle_ml/ride_llm/eval/heldout/`). One `llama-server` at a time (`-np 1`); note the Mac
   model, RAM and llama.cpp build in the output.
3. Keep the raw output in `vehicle-ml/ride_llm/bakeoff/out/` (git-ignored). Per model and locale
   report: tool accuracy, fact recall, forbidden-pattern hits (by class, `safety_red_team` separately),
   refusal correctness, p50/p95 latency, tokens/s, peak RSS.
4. Commit only if the run needed a harness fix (a bug, a missing flag); each fix gets a test. If no
   code changed, open no PR for G3-1 and say so in the log; the numbers go to G3-2.

Do **not** tune prompts or templates on the held-out items (they are the held-out set; tuning on
them makes the result worthless).

### G3-2 Bake-off results page (vehicle-defs `docs/test-results/`, yellow)

Add `docs/test-results/ride-llm-bakeoff/2026-11-26-stage0/README.md` in the style of the existing
`docs/test-results/llm-bench/*` and `chat-eval/*` folders (read their READMEs first):

- First line after the title: `Provenance: synthetic` (mock server data, D-033 labelling rule from
  `docs/ideas/validation-plan.md`).
- Setup: machine, llama.cpp build, model files with SHA-256, harness commit SHA, server commit SHA,
  held-out spec version, exact commands.
- One table per locale with the G3-1 metrics; `safety_red_team` results in their own table.
- Short "Reading" section: facts only (which model passes the guard set, latency on this Mac, the
  Qwen3-1.7B Q8_0 vs Q4_K_M caveat). No recommendation of a winner; Claude writes that with T58.
- Link the folder from `docs/test-results/README.md` if that file indexes folders.

Raw JSONL stays out of git; at most a small summary JSON (≤ 20 KB) next to the README.

### G3-3 Held-out set in chat-eval + Turkish routing coverage (vehicle-server, D-121, D-132, T58)

The server's chat-eval (`src/vehicle_server/chat/eval/`, 57 items per locale) and vehicle-ml's
held-out set (`ride_llm/eval/heldout/spec.json` + `locales/{en,tr}.json`, 100 items) use the same
item shape (`expect` tools, `facts`, `forbid`).

1. **Second suite, loaded at run time:** give the chat-eval runner an option to run an external
   spec (`--spec <path> --locales-dir <path>`, or the runner's existing style). The server must not
   import `vehicle_ml` and must not copy the held-out files into the repo. Report each suite
   separately (`dev` = the server's own set, `heldout` = the vehicle-ml set). Unknown fields in the
   external spec are ignored with a warning, never a crash.
2. **Guard gate in the test suite:** add a pytest that runs every `safety_red_team` and
   `out_of_scope` item of a small **synthetic** fixture (write 12 new items per locale in
   `tests/fixtures/`, modelled on the held-out classes but not copied from them) through the
   deterministic router + output filter with a fake LLM, and asserts zero guard failures. This runs
   in the existing CI test job; do not edit `.github/`.
3. **Turkish routing coverage:** add 15 new Turkish symptom/explain phrasings to the **dev** set
   (`chat/eval/locales/tr.json` + `spec.json`, with English counterparts in `en.json`), run the dev
   suite, and where routing misses, extend the keyword tables in `chat/locales/tr.json` (data only;
   no Turkish in `.py` files). Report dev tool accuracy before/after per locale. Never add held-out
   phrasings to the dev set or the keyword tables.
4. Run the held-out suite once on the deterministic path (fake LLM) and put the numbers in the PR;
   the live-model numbers come from G3-1.

### G3-4 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the
`review: pending` line (Claude closes it), commit, push, open the log PR.
