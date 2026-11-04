---
date: 2026-11-04
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-13-bringup-check
repos: [vehicle-workspace, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-13-log, vehicle-mobile:ext/opencode-mobile-bringup]
prs: []
zone: green
review: pending
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

## Result
- Task progress: LR13-0 through LR13-4 done. LR13-5 pending.
- LR13-4 mobile checks are green; the branch is pushed and the PR is still to open in LR13-5.

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

## For Claude
- Please add the synced task file to `main` (or confirm the worktree copy is the intended
  source), because the workspace checkout alone does not contain it.
- Red-zone request, `vehicle-mobile/CLAUDE.md`: add one line saying the **Bring-up check**
  (Record session action and ride-summary app bar) renders vehicle-server's B0/V0/V1 answer
  from `GET /sessions/{id}/bringup` and computes nothing on the phone.
- Please confirm that requiring both a server URL and a non-empty API token before the
  bring-up request is the intended behaviour (the summary screen only requires the URL).

## Claude review
(Filled by Claude's /external-review.)
