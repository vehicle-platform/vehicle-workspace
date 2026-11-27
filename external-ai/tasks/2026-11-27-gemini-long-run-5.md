# Gemini long run 5 — 2026-11-27 (CubeMX CLI note, diagrams, ride-mark follow-ups, multi-turn cache measurement, READMEs, analyzer tests)

Written by Claude for Gemini CLI. Runs 1-4 are reviewed and merged. Start from an up-to-date `main` in
every repo (`git switch main && git pull --ff-only`). Run the tasks in order without asking between
them; do not stop and do not wait for an answer. One branch and one PR per task; commit after every
logical step (Conventional Commits, `AI-Agent: gemini-cli/<model>` trailer), push after every commit,
update and push the log after every task. If a task makes no progress for about 90 minutes, write why
in *For Claude*, push what is done and go on. **Never merge a PR. Never force-push.**

Order: G5-0, G5-A, G5-1, G5-2, G5-3, G5-4, G5-5, G5-6, and G5-9 **last**.

| Task | Repo / path | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G5-0 and G5-9 | vehicle-workspace `external-ai/log/` | `ext/gemini-long-run-5-log` | green |
| G5-A | vehicle-defs `docs/ideas/cubemx-cli.md` | `ext/gemini-cubemx-cli` | green |
| G5-1 | vehicle-defs `docs/diagrams/` | `ext/gemini-diagrams` | **yellow** (`needs-claude-review`) |
| G5-2 | vehicle-mobile (marks UI) | `ext/gemini-marks-followup` | green |
| G5-3 | vehicle-mcp (`tools.py`, `specs.py`, `server.py`, tests) | `ext/gemini-mcp-marks` | **yellow** (`needs-claude-review`) |
| G5-4 | vehicle-server `src/vehicle_server/chat/eval/` (dev set only), `tests/` | `ext/gemini-multiturn-eval` | green |
| G5-5 | vehicle-server `README.md`, vehicle-mobile `README.md` | `ext/gemini-readmes` (one per repo) | green |
| G5-6 | vehicle-analyzer `tests/` | `ext/gemini-analyzer-tests-2` | green |

**Red everywhere, never touch:** `external/*`, `gen/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.claude/*`, `vehicle-defs/docs/DECISIONS.md`, `vehicle-defs/docs/ARCHITECTURE.md`, every path in
vehicle-defs outside `docs/`, `vehicle-analyzer/src/services/webSerialCan*`, `src/services/udsComposer*`,
`src-tauri/*`. Before every push: `python3 scripts/check_zones.py <repo> --base origin/main` (exit 2 = red
path → revert it, note it in *For Claude*).

## 0. Rules for every task

- Read first: `GEMINI.md` (its §3 hard rules are the lessons of runs 1-4: evaluation sets read-only and
  splits frozen, values from vehicle-defs, proposals marked as proposed, unhappy path handled and tested,
  concurrency and retries safe, claims backed by the same run's numbers, every CI step run locally, reuse
  before you write, no personal data on public pages), then `STATUS.md`, then the target repo's
  `CLAUDE.md` (read only) and the decisions named in the task (search them in
  `vehicle-defs/docs/DECISIONS.md`; never read whole large docs).
- **English only** in code, comments, docs, tests, commit messages and PR texts (D-125). Turkish appears
  only in locale resource files (`*/locales/tr.json`, `*.arb`).
- **Public repos (D-033):** no personal data, no `/Users/...` paths, no tokens, no real ride or position
  data in any commit.
- No new runtime dependencies. Mirror every step of each repo's CI locally before pushing; all green.
- PR body: what, why (task id + decision), how verified (commands + numbers), anything skipped.

## Tasks

### G5-0 Log

Create `external-ai/log/2026-11-27-gemini-long-run-5.md` from `external-ai/log/TEMPLATE.md`, commit, push.

### G5-A STM32CubeMX command-line reference (vehicle-defs `docs/ideas/cubemx-cli.md`, roadmap card T70)

Claude generated the two `.ioc` files with the CubeMX command line; the working scripts and logs are in
the workspace's git-ignored `local/cubemx/` (`run.sh`, `build_ioc.sh`, `patch_ioc.py`, `dma_args.py`,
`check_pins.py`, `rt-core/`, `safety-node/`). Write a reference so a later session does not have to
rediscover it, facts only, each from those files:

1. How to run headless (`STM32CubeMX -q <script>`), the kill guard (no `timeout` on macOS), and why
   every script starts with `popupwrapper set`.
2. The commands that work (`loadboard <board> nomode`, `get mode available <IP>`, `set pin`, `set mode`,
   `config saveas`, `config load`, `csv pinout`, `project name|path|toolchain`) and what does not
   (DMA has no command → `.ioc` text + `config load`; VCP UART `set mode` refused).
3. The pin diff script: what it checks and how to run it.
4. Code generation needs the STM32Cube firmware packages; their install asks for a license acceptance
   in the GUI (Help > Manage embedded software packages); a script must never accept a license.
You may read the files and run `python3 local/cubemx/check_pins.py <board>`. **Do not start CubeMX**,
do not run `project generate`, do not install packages.

### G5-1 Architecture and sequence diagrams (vehicle-defs `docs/diagrams/`, yellow)

For the final thesis report, write Mermaid diagrams (one `.md` per diagram, each with a short caption and
a "Sources" list of the files/decisions every box and arrow comes from; no new facts):

1. System context: nodes, vehicle bus vs platform bus, server, app, analyzer (D-009, D-021, D-118).
2. Firmware layering (features → services → hal, target vs host port).
3. Sequence: read-only UDS polling on the vehicle bus and republish on the platform bus (D-020, D-037).
4. Sequence: in-ride alert from signal to app banner and voice (D-129).
5. Sequence: ride mark with the offline queue, retry and idempotent server insert (D-133).
6. Sequence: assistant question → guard → router → MCP tool → template → output filter (D-121, D-127).
7. Data flow on the Raspberry Pi: CAN → kuksa-can-provider → databroker (VSS) → consumers
   (`vehicle-linux-node/docker-compose.yml`, `config/dbc_feeder.ini`).
Add `docs/diagrams/README.md` indexing them. Check that GitHub renders each Mermaid block (no syntax
errors: run them through `npx -y @mermaid-js/mermaid-cli` if available, otherwise say so).

### G5-2 Ride marks follow-up (vehicle-mobile, D-133)

The merged picker offers five kinds and no note. Add:
1. A "More" entry in the picker that opens all seven kinds of D-133 (incl. `rough_road`, `traffic`).
2. An optional note (≤ 200 characters, counter shown) when the rider picks "other" or opens "More";
   empty note = no note. The 5 s auto-close pauses while the note field has focus.
3. Strings in the ARB files (en default, tr). Widget tests for More, note limit, auto-close pause,
   and that the note reaches the existing queue unchanged. Reuse the existing queue and client.

### G5-3 `get_ride_marks` MCP tool (vehicle-mcp, yellow, D-133 item 4, T65 first consumer)

Add a read-only tool `get_ride_marks(session_id)` that calls the server's existing
`GET /rides/{ride_id}/marks` through the existing `client.py` (GET only) and returns the labelled result
style of the other tools (`{name, unit, value, label}` items plus the mark list: time offset from the
ride start in seconds, kind, note). Small spec in `specs.py` like the other tools, registered in
`server.py`. No position anywhere. Tests: normal, empty, unknown ride (404 → safe message), server error.
The assistant routing to this tool is **not** part of this task (Claude decides it).

### G5-4 Multi-turn dev scenarios and cache measurement (vehicle-server, roadmap card T72)

The run-4 review found the prompt-cache benefit unproven because the dev suite is single-turn.
1. Add 10 multi-turn conversations per locale (3-4 turns each) to the **dev** set only, written new
   (do not reuse or paraphrase held-out or existing items); turns 2+ refer back ("and yesterday?",
   "is that normal?").
2. Extend the eval runner to send the turns of one conversation in order with the existing conversation
   store, and report per turn: tool accuracy, `cache_n / prompt_n`, time to first token.
3. Run it on `qwen2.5-1.5b` (en, tr) against `local/run-server.sh` + `local/run-llama.sh`, and report
   whether turns 2+ get a higher cached share than turn 1. Measure only: no prompt, router or template
   changes. If the numbers do not show a benefit, say so.

### G5-5 READMEs (vehicle-server, vehicle-mobile)

Bring each README up to date from the code (facts only, each endpoint/feature checked in the source):
server — endpoints for rides, marks, alerts (SSE), live (`/ws/live`), chat, accounts, how to run the
chat-eval (dev, held-out with `--spec`), the mock live scenarios; mobile — screens, ride marks and the
offline queue, alerts and voice, i18n (en default, tr), how to run tests. One PR per repo.

### G5-6 Analyzer tests, second pass (vehicle-analyzer)

Add tests for `src/components/SyncPanel.tsx` (file import, drag-drop, worker log import, custom DBC
load with jsdom `File`/`FileReader`) and `src/app/useLiveSources.ts` with the adapters mocked at their
module boundary (do not modify the red adapter files). Tests only; run the type-check of the tests
(`tsc -p ui-tests/tsconfig.json`), lint and `npm run test:coverage` locally. A bug found → its own commit
with the test, listed in the PR and in *For Claude*.

### G5-9 Close the log

Fill the log (changes, checks with numbers, skipped, unsure, *For Claude*), keep the `review: pending`
line (Claude closes it), commit, push, open the log PR.
