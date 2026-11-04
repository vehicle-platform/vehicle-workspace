---
date: 2026-11-04
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-13-bringup-check
repos: [vehicle-workspace, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-13-log, vehicle-mobile:ext/opencode-mobile-bringup]
prs: [https://github.com/vehicle-platform/vehicle-mobile/pull/28]
zone: green
review: done 2026-11-05 (merge after fixes: vehicle-mobile#29 supersedes #28)
---

# Bring-up check on the phone (read-only)

## Goal
Add a read-only Bring-up check screen to vehicle-mobile that calls the existing
`GET /sessions/{id}/bringup` endpoint (vehicle-server#50) and renders the server's verdict,
checks, manual items and warnings. The phone computes nothing, sends nothing to the vehicle,
and no new server route is added. Task file:
`external-ai/tasks/2026-11-04-deepseek-long-run-13.md` (this run's copy was found only in the
`claude/lr13-task` worktree; see *Unsure about*).

## Changes
- LR13-0 (vehicle-workspace, `ext/opencode-long-run-13-log`, `3b7ea0b`): created this log first,
  before code, per the task.
- LR13-1 (vehicle-mobile, `ext/opencode-mobile-bringup`, `6b3ab23`):
  - `lib/models/bringup_result.dart`: strict `BringupCheck`/`BringupResult` parsers; `measured`
    is kept as decoded JSON and an unknown check status remains verbatim.
  - `lib/services/ride_client.dart`: added `getBringup` to the existing `RideClient` (not a new
    client file: it reuses the same `_get`, token header, timeouts and result type) and
    `RideOutcome.unsupported` for a 404 whose detail is exactly `Not Found`; existing
    `listRides`/`getSummary` behaviour is unchanged.
  - `test/bringup_result_test.dart`, `test/ride_client_test.dart`: parser, JSON-type, URL,
    token-header, 401/404/422/503/timeout and old-server cases.
- LR13-2 (vehicle-mobile, `3109939`): new `lib/ui/rides/bringup_screen.dart` with the default
  V0 gate selector, verdict and pending/warning lines, one card per server check, compact
  measured rendering, plain-language manual/unknown explanation, Settings link, retry and
  pull-to-refresh. It uses the existing `StatusPill`/tone tokens and no new colour.
- LR13-3 (vehicle-mobile, `c3f4b38`):
  - `lib/ui/record_screen.dart`: the uploaded-session card has a **Bring-up check** action
    (not shown for never-uploaded or failed sessions); it opens the screen with that id.
  - `lib/ui/rides/ride_summary_screen.dart`: an app-bar **Bring-up check** action opens the
    screen for the same session and reuses the screen's injected settings/client.
  - Tests in `test/record_ride_actions_test.dart` and `test/ride_summary_screen_test.dart`.
- LR13-4 (vehicle-mobile, `6859c55`):
  - `test/bringup_screen_test.dart`: 10 widget tests for the verdict, checks, gate change,
    warnings, unknown status verbatim, old-server 404, unknown-session 404, no settings and
    URL without a token.
  - `README.md`: a short **Bring-up check** section (B0/V0/V1, read-only server answer,
    `GET /sessions/{id}/bringup`, server#50).
  - Kept formatter-only churn out of the diff: the source and test files touched by the
    earlier commits now show only the intended changes.
  - Added runner keys `bringup-verdict` and `bringup-check-<id>` for the widget tests.
  - Opened one PR from `ext/opencode-mobile-bringup` to `main`:
    https://github.com/vehicle-platform/vehicle-mobile/pull/28 (not merged).
- LR13-5 (vehicle-workspace, `ext/opencode-long-run-13-log`, this commit): closed the log with the
  task list, commits, checks, PR link, doubts and requests. No workspace PR was opened, per the
  task.

## Result
- Task progress: LR13-0 through LR13-5 done.
- Mobile PR: https://github.com/vehicle-platform/vehicle-mobile/pull/28 (open, not merged).
- The phone renders the server answer only; no compute, no BLE, no POST, no new server route.

## Checks
- LR13-0 `python3 scripts/check_zones.py . --base origin/main`: green.
- LR13-1 `flutter test test/bringup_result_test.dart test/ride_client_test.dart`: 27 passed.
  `pubspec.lock` was rewritten by `flutter pub get` and reverted; it is not committed.
- LR13-1 `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: green.
- LR13-2 `flutter analyze --no-pub`: clean after two brace lints were fixed.
- LR13-3 `flutter test --no-pub test/record_ride_actions_test.dart test/ride_summary_screen_test.dart`:
  all passed (record action test needed `ensureVisible` for the off-screen button).
- LR13-3 `flutter analyze --no-pub`: clean.
- LR13-3 `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: green.
- LR13-4 `flutter analyze --no-pub`: no issues found.
- LR13-4 `flutter test --no-pub --reporter compact`: 320 tests passed.
- LR13-4 `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: green.
- LR13-4 `git diff --check`: clean; `pubspec.lock` not modified.

## Unsure about
- The task file was absent at the workspace path named in the task
  (`external-ai/tasks/2026-11-04-deepseek-long-run-13.md`). It exists only in the read-only
  worktree `.claude/worktrees/lr13-task/...` on branch `claude/lr13-task` (commit `867037e`).
  I read that copy; I did not edit `.claude/*`.
- Older-server 404 detection follows the analyzer precedent: the detail must trim/lowercase to
  exactly `Not Found`; every other 404 remains `notFound` with the server detail. A proxy that
  returns that exact detail for another missing route could be mistaken for an old server.
- `measured` rendering is intentionally lossless: a top-level map becomes one `key: value` line per
  entry, nested maps stay inline, lists are joined with `, `, `null` becomes `—`, and nothing is
  rounded. Very large nested values may still be long, but they wrap and the screen scrolls.
- The Record action sits in the same per-session action row as ride summary/upload/share, visible
  only when the upload state is `uploaded`. The summary app-bar action does not depend on upload
  state. The bring-up request additionally requires a non-empty API token; the summary screen only
  requires the URL, so this is deliberately stricter and is queried under *For Claude*.
- The full test suite was run with `--no-pub` to avoid rewriting `pubspec.lock`; Flutter itself was
  3.47.5 as CI expects.

## For Claude
- Please add the synced task file to `main` (or confirm the worktree copy is the intended
  source), because the workspace checkout alone does not contain it.
- Red-zone request, `vehicle-mobile/CLAUDE.md`: add one line saying the **Bring-up check**
  (Record session action and ride-summary app bar) renders vehicle-server's B0/V0/V1 answer
  from `GET /sessions/{id}/bringup` and computes nothing on the phone.
- Please confirm that requiring both a server URL and a non-empty API token before the
  bring-up request is the intended behaviour (the summary screen only requires the URL).

## Claude review
2026-11-05, Claude (/external-review):
- **Zones:** all 11 paths green (`check_zones.py vehicle-mobile --base origin/main`). CI on #28 green (flutter, build-apk).
- **architecture-guard:** no BLOCKER/MAJOR. Scope, token handling (header only), no position, no new dependency, upload code untouched, 404 "Not Found" = older server like the analyzer, unknown statuses verbatim, parser matches `BringupResult.to_dict()`.
- **Fixed by Claude (vehicle-mobile#29, on top of DeepSeek's commits; supersedes #28):** `needs_you`/`warnings` ids listed, not only counted; a generic status legend (no gate-specific text); pull-to-refresh keeps the content, a gate change clears it; the server detail in the unknown-session text (without the client's literal "not found" fallback); a fixed settings-failure text without the exception; the settings-failure message is shown and retried; the unrelated `record_screen.dart` reformat reverted; vehicle-mobile `CLAUDE.md` line (the red-zone request). 324 tests, analyze clean.
- **For Claude answers:** the task file is on workspace#163 (opened by Claude, waiting for the user's merge); the URL + non-empty token requirement is kept (the server answers 401 to an empty token on every non-/health route).
- **Lesson:** a task file must be on main before the run starts (the copy was only on the Claude worktree branch).

