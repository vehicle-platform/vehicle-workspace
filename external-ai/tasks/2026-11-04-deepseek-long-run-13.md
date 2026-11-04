# DeepSeek long run 13 — 2026-11-04 (bring-up gate check on the phone)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR13-0 (first!) and LR13-5 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-13-log` | green |
| LR13-1..LR13-4 | vehicle-mobile | `ext/opencode-mobile-bringup` | green (yellow: `lib/services/session_upload*`, `lib/services/upload_client*`, `pubspec.yaml`; red: `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`: do not touch them) |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

The first sessions on the real Honda CL250 are close (gate G1 in `STATUS.md`). vehicle-server
already answers "does this session pass gate B0 / V0 / V1?" (`GET /sessions/{id}/bringup`,
server#50) and vehicle-analyzer shows it on the laptop (analyzer#43). At the bike the user has
**only the phone**: record a session, upload it, and today they cannot see the verdict without a
laptop. This run adds a read-only **Bring-up check** screen to vehicle-mobile that calls the
existing endpoint and renders its answer. Nothing is computed on the phone, nothing is sent to
the vehicle, no new server route.

No decision is needed from the user. If something here contradicts a decision (vehicle-defs
`docs/DECISIONS.md`: D-022, D-033, D-063, D-076, D-077) or vehicle-mobile `CLAUDE.md`, the
decision text wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-mobile/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area).
- `git -C vehicle-mobile checkout main && git -C vehicle-mobile pull`, then
  `git -C vehicle-mobile checkout -b ext/opencode-mobile-bringup`. In the workspace:
  `git checkout main && git pull && git checkout -b ext/opencode-long-run-13-log`. Right after
  creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format, the check table
  (§4). Before each push run `python3 scripts/check_zones.py <repo> --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- vehicle-mobile `CLAUDE.md` (rules: nothing safety-critical, no hand-written signal names) and
  `README.md`.
- The server contract, **the only source for the response shape**: vehicle-server
  `src/vehicle_server/bringup.py` (`Check`, `BringupResult.to_dict()`, `STATUSES`, `GATES`,
  `format_text`) and the route in `src/vehicle_server/api.py` (`get_session_bringup`: 404
  `unknown session: <id>`, 422 for a missing/unknown gate, bearer token). Read, do not edit.
- How the analyzer already does it (same contract, reuse the ideas, not the code):
  vehicle-analyzer `src/services/sessionClient.ts` (search `BringupUnsupportedError`: a 404 whose
  detail is exactly "Not Found" = an older server without the route; any other 404 = unknown
  session) and its Bring-up card component.
- vehicle-mobile code: `lib/services/ride_client.dart` (the read-only GET client with
  `RideResult`/`RideOutcome`, token in the header, timeouts), `lib/services/http_message.dart`,
  `lib/services/app_settings.dart` (server URL + token), `lib/ui/record_screen.dart` (the local
  session list with per-session upload status and actions; the "Server rides" button),
  `lib/ui/rides/` (history and summary screens, `ride_widgets.dart`, `ride_format.dart`),
  `lib/ui/theme/app_theme.dart`, `lib/ui/widgets/common.dart` (`StatusPill`). Tests: `test/ride_client_test.dart`, `test/ride_summary_screen_test.dart`,
  `test/ride_history_screen_test.dart`, `test/record_ride_actions_test.dart`.

### Hard rules for this run

1. **Read-only GET.** Only `GET /sessions/{id}/bringup?gate=…` is added. No POST, no write to the
   server, nothing over BLE, no change to the upload code (`session_upload*`, `upload_client*`
   are yellow: do not touch them).
2. **Render, never compute.** The phone shows `verdict`, `checks`, `needs_you`, `warnings`
   exactly as the server returns them. No threshold, no re-derived verdict, no number of your own.
   Unknown `status` strings are shown verbatim with a neutral style (forward compatible), never
   dropped and never turned into "pass".
3. **Token only in the `Authorization` header**, never in a URL, a log line or a snackbar.
4. **No position (D-076).** Do not read or show anything from `gps*` files; the endpoint has no
   position anyway.
5. **No real data in git (D-033).** Test JSON is synthetic and written in the test.
6. **No new dependency** (`pubspec.yaml` is yellow). `package:http` and `MockClient` are already
   there.
7. Signal names (e.g. `ENGINE_SPEED` inside `measured`) are shown as the server sends them; do
   not add a name table on the phone.

## LR13-0 — Log first

Before any code: copy `external-ai/log/TEMPLATE.md` to
`external-ai/log/2026-11-04-opencode-long-run-13.md` on `ext/opencode-long-run-13-log`,
`review: pending`, fill the header and the task list, commit and push. Update it after every
later task (commit + push each time), so the log is never behind the code.

## LR13-1 — Model and client

1. New `lib/models/bringup_result.dart`: `BringupCheck` (`id`, `status`, `measured` as the raw
   decoded JSON value, `expected`, `source`, `note`) and `BringupResult` (`sessionId`, `gate`,
   `verdict`, `checks` in server order, `needsYou`, `warnings`), each with `fromJson` that throws
   `FormatException` on a missing or wrongly typed required field (follow the style of
   `ride_summary.dart`). `measured` may be `null`, a number, a string, a bool, a list or a map.
2. In `ride_client.dart` (or a new `bringup_client.dart` beside it if you think it reads better;
   say which in the log), add `getBringup({baseUrl, apiToken, sessionId, gate})` using the same
   `_get` path, `Uri.encodeComponent` for the id and `gate` as a query parameter. Add an outcome
   for **an older server without the route**: a 404 whose detail is exactly `Not Found`
   (case-insensitive, trimmed) → e.g. `RideOutcome.unsupported`; a 404 with any other detail stays
   `notFound` (unknown session). Do not change the behaviour of `listRides`/`getSummary`
   (existing tests must pass unchanged).
3. Tests (`test/bringup_result_test.dart`, `test/ride_client_test.dart` or a new client test):
   parse a pass, a fail and an incomplete result; every `measured` JSON type; a missing field →
   `FormatException`; an unknown status string is kept; the request URL (path, encoded id,
   `gate=V0`), the header carries `Bearer <token>` and the URL never contains the token; 401,
   404 unknown session, 404 "Not Found" → unsupported, 422 with the server detail, 503, timeout.

## LR13-2 — Bring-up check screen

1. New `lib/ui/rides/bringup_screen.dart`: title "Bring-up check", the session id, a gate
   selector **B0 / V0 / V1, default V0** (segmented button or chips in the app's existing style),
   loads on open and on every gate change, pull-to-refresh or a retry button.
2. Content, top to bottom: the verdict (`pass` / `fail` / `incomplete`) as a large status pill;
   below it "N manual check(s) pending" when `needsYou` is not empty and "N warning(s)" when
   `warnings` is not empty; then one card or tile per check in server order: status, `id`,
   `measured` (a compact readable rendering: numbers as is, maps as `key: value` lines, lists
   joined; long values wrap, never overflow), `expected`, `source`, `note`.
3. Colours: use the existing status colours of `lib/ui/theme/app_theme.dart` and the existing
   `StatusPill` (`lib/ui/widgets/common.dart`):
   pass = the existing "ok" colour, fail = the existing error colour, warn = the existing warning
   colour, manual and unknown = neutral or info styles that already exist. Do not add a palette.
   Status must also be readable without colour (text label or icon, accessibility).
4. Explain the statuses in one line under the verdict, in plain words: `manual` = "you judge this
   one at the bike" (V1 throttle blip, B0 at rest), `unknown` = "the session has no data for it".
5. Errors: unsupported → the text "this server has no bring-up check (needs vehicle-server with
   the bring-up route, server#50)"; unauthorized → point to the token in Settings; unknown
   session → "the server does not have this session (upload it first)"; 422 → the server's
   message; network/timeout → the message plus retry. No server URL/token configured → say so
   and link to Settings, do not send a request.

## LR13-3 — Entry points

1. **Record screen, local session list:** for a session whose upload status is "uploaded",
   add a "Bring-up check" action next to the existing actions (same pattern as the existing
   per-session actions; keep the list layout). It opens the screen with that session id. Not
   shown for a session that was never uploaded or whose upload failed.
2. **Ride summary screen** (`lib/ui/rides/ride_summary_screen.dart`): an app-bar action
   "Bring-up check" that opens the screen for the same session.
3. Tests: widget tests that the action appears only for uploaded sessions, opens the screen with
   the right id, and that the summary-screen action opens it. Use the existing test helpers and
   an injected `MockClient`; no real network in tests.

## LR13-4 — Widget tests, docs, checks, PR

1. `test/bringup_screen_test.dart`: pass; fail with one failing check; incomplete with two
   manual checks (the "2 manual check(s) pending" line); warnings shown; unknown status string
   shown verbatim; gate change sends a new request with the new gate; unsupported-server text;
   unknown-session text; no settings → no request. Pump at a phone size (e.g. 360×690 logical)
   and assert no overflow.
2. `README.md`: a short *Bring-up check* paragraph (where it is, what B0/V0/V1 mean in one line
   each with a pointer to vehicle-defs `docs/hardware-integration.md` §6, that the phone only
   shows the server's answer, and the minimum server: the one with server#50).
3. `CLAUDE.md` is red: write in *For Claude* the one line Claude should add.
4. Run `flutter analyze` and `flutter test` (both clean; Flutter 3.47.5 like CI), the zone check,
   and open **one** PR from `ext/opencode-mobile-bringup` to `main`; do not merge it.

## LR13-5 — Close the log

Finish `external-ai/log/2026-11-04-opencode-long-run-13.md`: every task, commit, check result
(`flutter analyze`, `flutter test` counts), the zone result, the PR link, every doubt (*Unsure
about*: especially how you detect the older-server 404, how `measured` maps are rendered, and
where the Record action sits) and every request (*For Claude*). Keep `review: pending`. Push
the branch; no PR needed.
