# AGENTS.md — vehicle-platform rules for AI coding tools other than Claude Code

You are an AI coding tool (Codex, Gemini, DeepSeek, Cursor, Aider, Copilot, …) working on vehicle-platform, a motorcycle diagnostics / telemetry / ADAS platform with safety-relevant firmware. Claude Code is the project's reviewing and safety-gating tool; you work **alongside** it under the rules below (D-071). If a rule here conflicts with what the user asks, say so and ask before acting.

## 1. Every session

1. Read `STATUS.md` at the workspace root (short): where the project is and what is next. If you are inside a single repo without the workspace, say so; the zone checker and the log folder live in the workspace.
2. For architecture facts read `vehicle-defs/docs/ARCHITECTURE.md` and `DECISIONS.md` (only the parts you need; `docs/README.md` indexes the large docs). Never guess an architecture fact and never re-decide a recorded decision.
3. Before editing a file, check its zone: `python3 scripts/check_zones.py <repo> --path <file>` (workspace root). **Red = do not edit.**
4. Open your log entry (section 5) at the start, not at the end.

## 2. Edit zones (`external-ai/zones.json`, first matching rule wins)

- **red** — Claude only. Do not edit, not even "small fixes". Describe the wanted change under *For Claude* in your log and continue with something else.
- **yellow** — allowed; the PR needs a Claude review before the user merges it (write `needs-claude-review` in the PR description).
- **green** — allowed; still log it.

{{ZONES}}

## 3. Hard rules that no path rule can catch

- **No hand-written signal facts.** CAN IDs, DIDs, signal names, scales, units, VSS paths and BLE layouts come only from the generated `gen/` code or the definition files of vehicle-defs. Never write such a literal in code; if a signal is missing, that is a red-zone request (`/signal-change` by Claude).
- **Nothing new on the vehicle bus.** No code that sends a CAN frame to the motorcycle outside the existing tester modules (red); no new UDS service, no write, clear, reset, unlock or reprogram, ever.
- **MCU code** (rt-core, safety-node, conn, hil-bench firmware): no heap (`malloc`, `new`, STL containers that allocate) after init, no string/JSON/DBC parsing, no blocking calls in the tester loop, MISRA C:2012 style in C.
- **Privacy:** never commit keys, passwords, real ride data, VINs, or GPS positions. Position may go only to the user's own servers (D-076, provisional); code that moves it is red (Claude only). The repos are public.
- **Safety path:** never make a safety decision (cornering, blind spot, immobilizer) depend on the Raspi, the phone, Wi-Fi, VSS or ML; ML may only tighten thresholds.
- **No new dependency** in firmware or in `pyproject.toml` / `pubspec.yaml` without asking the user.
- **Do not weaken checks:** no disabled tests, lowered coverage, new MISRA suppressions, `# noqa` or `// cppcheck-suppress` to make CI green. Fix the code or log the problem.
- **No new repositories.** Never create a repo in the org or a new top-level project; propose it under "For Claude" in your log (a new repo needs a D-xxx, its zones and the shared assets first, D-081).
- **Hardware facts need a source.** Part numbers, pinouts, dimensions and prices you could not verify are marked **CONFIRM**; never rank an open question's candidates (Q-xxx) as decided, and never move a safety input (M4 board, D-082) onto a QM or detachable board.
- **No releases:** no tags, no version bumps, no submodule pin changes, no `manifest.yaml` edits (D-036). Never merge a PR and never push to `main`; the user merges.

- **Evaluation sets are read-only.** Never tune thresholds, keywords, prompts or templates on an evaluation or held-out set, and never copy its items into a dev set, a fixture or a keyword table. Choose a cutoff on a separate split and say which. Ranking scores that are not comparable across queries (e.g. RRF) are not relevance cutoffs.
- **Meaningful values come from vehicle-defs at run time.** Ranges, thresholds, units and signal metadata are read from the pinned defs package, never copied as numbers and never taken from an older defs version as a fallback.
- **Proposals are marked as proposals.** Targets, recommendations, design choices and data models you introduce are written as **proposed**; only measured results (with the command that produced them) and cited facts (document + section) are stated plainly. Never pick a winner where the task says Claude decides.
- **Handle the unhappy path, with a test each:** errors surfaced to the caller or the UI (never swallowed), missing or invalid inputs fail loudly (non-zero exit, 4xx), late async replies dropped, timeouts bounded, temporary files removed.
- **Reuse before you write.** Use the repo's existing transport, locale loader, storage layer and helpers; a second copy of the same logic is a review finding.
- **Concurrency and retries are part of the job.** A read-modify-write of shared state (a queue, a file, a row) runs under one lock or one atomic statement; a create that a client may retry is idempotent through a key or a database constraint, never a SELECT-then-INSERT; a retry has a backoff and a cancel. Test the concurrent case.
- **Evaluation splits are frozen once used.** Never move, relabel or reword an existing evaluation item between tune, test and holdout; a new split takes only new items. A cutoff chosen on one split is never reported on that split.
- **Claims match the run.** A statement such as "X improves Y" needs the before/after numbers of the same run that show it; if the numbers do not show it, write it as a hypothesis.
- **Totals reconcile.** Counts and totals are computed over the full data, never over a truncated list; a per-category breakdown adds up to the total it explains (anything it does not cover is its own neutral bucket); a missing input gives a `warnings` entry, never a silent empty result.
- **Untrusted text stays quoted on every path.** Rider-written or other free text (notes, complaints) is shown only as quoted, sanitised text (control and Unicode format characters removed, the quote character replaced) and never reaches an LLM prompt. Trace the value past the render: storage, conversation history and recent-turn context, caches, exports.
- **Examples in docs must work.** An example scenario, config or command must be able to produce the result it claims with the numbers it quotes (durations against sustain times, preconditions such as engine running); identifiers in examples exist in vehicle-defs or the code; "observed" only for something measured, with its source, otherwise "expected".
- **Run every CI step locally,** including test type-checks and build steps, not only the test command; read the repo's workflow files to see what CI runs.
- **Public results pages:** no usernames, `/Users/...` paths, hostnames, tokens or raw model answers; label synthetic data `Provenance: synthetic`.
- **Updating a doc never deletes still-true content.** Condense or move it; list every removed fact in the PR body with the reason (the code no longer does it, with the file). Copied paths, flags and rule sentences are checked against their source, never reworded into a different rule.
- **Never discard what the user chose or typed.** A timeout, auto-close, retry or navigation keeps or submits the user's choice and text; it never drops it silently.
- **Totals over the full data, each value once.** Counts are computed before a list is truncated; a quantity is not repeated as a raw field next to it; a missing input becomes a `warnings` entry, never a silent null; an unknown category is its own bucket.
- **A scripted multi-step run stops at the first failed step** (conversation, retry chain, migration) and marks the rest as not run; cleanup in `finally` never masks the original error.
- **Diagram and topology facts are checked per arrow** against the code or the DBC: who transmits on which bus, which services a node sends.

## 4. Workflow

1. Branch: `ext/<tool>-<topic>` (e.g. `ext/gemini-mobile-dashboard`), in the repo you change. Never `main`, never a `claude/` branch. One topic per branch.
2. Language: every artifact is English only, never bilingual (D-125): code, comments, docs, test results, fixtures, prompts, commits, PR texts. No Turkish text in the repos except the i18n translation resource files; user-facing text defaults to English.
3. Commits: Conventional Commits in English (`feat(mobile): ...`) with the trailer line `AI-Agent: <tool>/<model>` (e.g. `AI-Agent: gemini-cli/gemini-2.5-pro`). Claude finds your work with `git log --grep '^AI-Agent:'`.
4. Before each commit: run the repo's checks (table below) and `python3 scripts/check_zones.py <repo>`. Red → revert those paths. Commit and push only when the user asks.
5. PR (when the user asks): title in Conventional Commits form; description = summary, checks run with their result, the zone result, `needs-claude-review` if any path is yellow, and the log file name.
6. Write code that reads like the surrounding code: same naming, comment density, test style. Add or update tests for what you change.

| Repo | Checks (run from the repo root) |
|---|---|
| vehicle-defs | red: do not edit (docs only: no check) |
| vehicle-rt-core | `cmake --preset host-tests && cmake --build --preset host-tests && ctest --preset host-tests` (+ `host-tsan` preset for snapshot/alive/IMU); cppcheck as in `.github/workflows/ci.yml` |
| vehicle-connectivity-node | `scripts/native_tests.sh` (or `pio test -e native`); `pio run -e esp32-s3-devkitc-1-mock`; cppcheck as in CI |
| vehicle-mobile | `flutter pub get && flutter analyze && flutter test` (never commit a local `pubspec.lock` rewrite) |
| vehicle-server | `uv sync && uv run pytest && uv run ruff check . && uv run ruff format --check .` |
| vehicle-analyzer | `git submodule update --init && npm ci && npm test && npm run build` |
| other repos | the commands in that repo's README/CLAUDE.md "Build" section |

## 5. Session log (mandatory)

Every session writes one file: `external-ai/log/YYYY-MM-DD-<tool>-<topic>.md` in the workspace, copied from `external-ai/log/TEMPLATE.md`, with `review: pending`. Fill it while you work: what changed (repo, branch, files), why, checks and results, zone result, what you were unsure about, and *For Claude* (red-zone requests, questions, suspected rule conflicts). Without the workspace, put the same text into the PR description. Claude reviews pending logs with its `/external-review` skill, refactors where needed and sets `review: done`.

## 6. What only Claude does

Red-zone edits; signal, UDS, BLE and limit changes (`/signal-change`) and every vehicle-defs edit outside `docs/`; new or changed decisions in `DECISIONS.md`; safety reviews (`safety-reviewer`) of invariant-8 modules; vehicle-bus tester changes; releases, tags and pins; synced files (`.claude/`, `AGENTS.md`, `GEMINI.md`, `PLATFORM-RULES.md`). You may update `STATUS.md` (keep ≤ 60 lines and its sections) and add rows to `ISSUES.md`.

## 7. Platform rules (copied from PLATFORM-RULES.md; "Claude" there means any AI tool unless a rule names Claude's agents or skills)

{{PLATFORM_RULES}}
