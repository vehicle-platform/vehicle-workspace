# DeepSeek long run 7 — 2026-11-02 (vehicle-mobile: server ride history + ride summaries)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

One repo (Flutter/Dart), a **green** zone except `pubspec.yaml` (yellow, and it must stay
unchanged in this run). Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

Long run 6 gave vehicle-server two read-only routes for the D-070 class-B per-ride summaries:
`GET /rides` (one row per session, class-B scalars) and `GET /sessions/{id}/summary` (scalars and
binned summaries of one session). The analyzer shows them; the phone does not. vehicle-mobile's
scope includes "ride history/reports ... the `vehicle-server` API for historical data", but today
it only **uploads** (`POST /sessions`). This run adds a read-only ride history and a ride summary
view to the phone. It adds **no new summary, no new formula, no new signal and no new server
route**.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py vehicle-mobile --base origin/main` from the workspace root.
  **Red = stop**, write the request into the log.
- `vehicle-mobile/CLAUDE.md` and `README.md`. Code: `lib/services/upload_client.dart` (injectable
  `http.Client`, timeouts, `Authorization: Bearer`, error-message extraction: copy this style),
  `lib/services/app_settings.dart` (`AppSettings`, `AppSettingsStore`, `isServerConfigured`,
  `sendsTokenInCleartext`, `isCleartextRemoteUrl`), `lib/services/session_upload.dart`
  (`SessionUploadState`), `lib/ui/record_screen.dart` (local session list, upload status, how it
  reacts to `settingsChanged`), `lib/ui/app_shell.dart` (five tabs), `lib/ui/settings_screen.dart`,
  `lib/ui/theme/app_theme.dart`, `lib/ui/widgets/common.dart`. Tests: `test/upload_client_test.dart`
  (`MockClient` pattern), `test/record_settings_screen_test.dart` (widget-test pattern).
- vehicle-server (read only, do not change it): `README.md` rows `GET /rides` and
  `GET /sessions/{id}/summary` and the two example responses under the route table;
  `src/vehicle_server/ride_summary.py` (exact shapes, statuses `computed` / `not_ready` /
  `not_implemented` / `missing_inputs` / `error`, `defs_mismatch`, `skipped`);
  `src/vehicle_server/api.py` (`/rides` query `from`/`to`/`names`, the 404/422 cases);
  `src/vehicle_server/ingest.py` (where the stored `session_id` comes from).
- vehicle-analyzer (read only, for consistency): `src/services/rideSummaryLayout.ts`
  (`precisionForRange`, `formatRideValue`, bar scaling, heat opacity) and
  `src/components/RideSummary.tsx`. The phone must format a value with the **same precision rule**
  as the analyzer, so the same ride reads the same on both.
- `vehicle-defs/docs/DECISIONS.md` **D-070** (derived signals), **D-087** (one session = one ride),
  **D-063** / **D-076** (position, upload targets), **D-033** (public repos).
- `ISSUES.md` row **E-26 (1)**: `ride_distance_gps` ignores `gps_fix_type`. That needs a user
  decision; show the value exactly as the server returns it.

### Hard rules for the whole run

- **Read-only.** The new client only sends `GET`. Nothing is written, recomputed or deleted on the
  server. `upload_client.dart` and the upload flow keep their behaviour; their tests must pass
  unchanged.
- **Names, units, ranges and bin edges from the response, never literals** (invariant 2). The app
  never hard-codes a summary name, unit, bin edge, column or display order; it renders what the
  response says, in response order. Tests may of course use names in their fixtures.
- **No position.** The responses contain none; do not add any. Never put the token in a URL; only
  the `Authorization: Bearer` header, read from `AppSettingsStore` like the upload.
- **Cleartext:** reuse the existing rule. If `settings.sendsTokenInCleartext` is true, show the same
  kind of warning the app already shows for it (find where; do not invent a new policy, do not
  block a request the upload would allow).
- **No new dependency.** `pubspec.yaml` and `pubspec.lock` stay unchanged. Charts are plain widgets
  or `CustomPainter`; dates are formatted by hand (there is no `intl` dependency).
- **Do not touch** `external/` (the defs submodule pin), `.github/`, `CLAUDE.md`, `AGENTS.md`,
  `GEMINI.md`, `.claude/`, `docs/session-format.md`, the BLE code, any other repo.
- **UI text in English**, like the rest of the app.
- All test data is **synthetic** (D-033): invented session ids and values, never a real ride.
- `flutter analyze` must report no issues and `flutter test` must pass before every push.

Branches (one PR for the code, one for the log, each opened against `main`):

| Part | Repo | Branch | Tasks |
|---|---|---|---|
| A | vehicle-mobile | `ext/opencode-mobile-ride-history` | MR-1 .. MR-6 |
| Log | vehicle-workspace | `ext/opencode-long-run-7-log` | the session log |

One session log for the whole run: `external-ai/log/2026-11-02-opencode-long-run-7.md` (copy
`TEMPLATE.md`; `review: pending`; a result row per task with code `file:line`, test names, status).
Create and push the log branch **first**, with the Result table rows marked `todo`, and update it
as tasks finish.

## Part A — vehicle-mobile

### MR-1 Models + strict parsing (`lib/models/ride_summary.dart`)

Immutable Dart classes for both responses, each with a `fromJson` that is **strict**: a missing or
wrongly typed required field throws a `FormatException` naming the field; unknown extra fields are
ignored.

- `/rides`: `RidesTable { columns: List<RideColumn{name, unit}>, rows: List<RideRow{sessionId,
  createdUtc (DateTime, UTC), values: Map<String, double?>, flags: Map<String, String?>}>,
  skipped: int }`. Check what `skipped` really is in `ride_summary.py` (count or list) and model
  that; write the finding into the log.
- `/sessions/{id}/summary`: `RideSummary { sessionId, rideDefinition, defsVersion, signals }`, with
  `signals` a sealed hierarchy: `ScalarSummary {name, unit, range(min,max), value?, flag?}`,
  `BinnedSummary {name, unit, range, axes: List<{input, unit, edges: List<(lo, hi)>}>, cells:
  List<{index, axes: List<int>, value?, flag?}>, totalS, outsideS, defsMismatch}`,
  `UnavailableSummary {name, status, reason?, pendingInputs, missing, message?}`. Keep the response
  order. Take every field name from `ride_summary.py`, not from this text, if they differ.

Tests (`test/ride_summary_model_test.dart`): a full `/rides` fixture, a summary fixture with one
scalar, one 1-axis and one 2-axis binned signal and two non-computed entries, `defs_mismatch`,
null values, every required-field-missing case throws, extra fields ignored.

### MR-2 Read client (`lib/services/ride_client.dart`)

`RideClient` in the style of `UploadClient`: injectable `http.Client`, connect timeout 10 s, total
timeout 30 s, `Authorization: Bearer <token>`, base URL with or without a trailing slash.

- `Future<RideResult<RidesTable>> listRides({required baseUrl, required apiToken, DateTime? from,
  DateTime? to, List<String>? names})` → `GET {base}/rides`; `from`/`to` sent as date-only
  `YYYY-MM-DD` (the server treats a date as the whole UTC day, inclusive), `names` comma-joined,
  all query values URL-encoded by `Uri`.
- `Future<RideResult<RideSummary>> getSummary({required baseUrl, required apiToken, required
  sessionId})` → `GET {base}/sessions/{sessionId}/summary`, the id as one encoded path segment.
- `RideResult<T>`: an outcome enum `ok`, `unauthorized` (401), `notFound` (404, keep the server's
  message, e.g. `session has no ride summary`), `invalid` (422), `unavailable` (503: server has no
  token configured), `failed` (other status, network error, timeout, a `FormatException` from
  MR-1), plus `data`, `statusCode`, `message`. Share the message extraction with `UploadClient`
  only if you move it into a small helper and `test/upload_client_test.dart` passes unchanged.

Tests (`test/ride_client_test.dart`, `MockClient`): exact URL and header for both calls, query
encoding (dates, names with commas), trailing slash, each status above, timeout, a socket error,
malformed JSON, a 200 with a missing field → `failed` with the field name in the message. Assert
that no request is ever anything but `GET`.

### MR-3 Pure formatting helpers (`lib/ui/rides/ride_format.dart`)

- `precisionForRange(min, max)` and `formatRideValue(value, min, max)`: port the analyzer's rule
  from `rideSummaryLayout.ts` exactly (null → `—`), with the analyzer's own test cases ported to
  Dart.
- `formatDurationS(seconds)` for `total_s`/`outside_s` (e.g. `0 s`, `42 s`, `3 min 05 s`,
  `1 h 02 min`), `formatUtc(DateTime)` → `YYYY-MM-DD HH:MM UTC` (deterministic in tests, no
  locale), bar heights scaled to the largest non-null value, heat-cell opacity like the analyzer.

Tests: `test/ride_format_test.dart`, including null, zero, negative ranges and an all-null bar set.

### MR-4 Ride history screen (`lib/ui/rides/ride_history_screen.dart`)

Reached from the **Record** screen's app bar (an icon button "Server rides" that pushes the screen);
**do not add a sixth navigation tab**. The screen loads settings through `AppSettingsStore`
(injectable for tests) and a `RideClient` (injectable).

- States: server not configured (text pointing to Settings, no request made), loading, error (the
  outcome's message + Retry), empty (no rides in range; show `skipped` if > 0), loaded.
- Loaded: rides **newest first** (the server sorts ascending), each row shows `formatUtc(created)`,
  the session id, and the values of up to **two** chosen columns with their units and the flag when
  not null. The column chooser lists the response `columns`; default = the first two. A date-range
  button (`showDateRangePicker`) sets `from`/`to` and reloads; a clear button removes the range.
  Pull-to-refresh reloads.
- One request per load; a response that arrives after the range changed or the screen closed is
  ignored (no `setState` after `dispose`).
- Tapping a row opens MR-5 for that session.

Widget tests (`test/ride_history_screen_test.dart`): every state, newest-first order, the column
chooser built from the response, null values with their flag, a date range reaching the request
URL, a stale response ignored, tap opens the summary screen.

### MR-5 Ride summary screen (`lib/ui/rides/ride_summary_screen.dart`)

For one session id. States: loading, not found (show the server's message, e.g. no ride summary),
error + Retry, loaded.

- Header: session id, `ride_definition`, `defs_version`. If any signal has `defs_mismatch`, a
  visible warning banner naming those signals ("decoded with other defs bin edges").
- Scalars: a list `name | value unit | flag`, value from `formatRideValue`.
- Binned, one axis: a small bar chart (one bar per bin, label from the edges `lo–hi` + axis unit,
  height from MR-3), with `total_s` and `outside_s` under it via `formatDurationS`.
- Binned, two axes: a heat grid (rows = second axis, columns = first axis), opacity from MR-3,
  axis labels from `axes[].input` + unit + edges; tapping a cell shows its value and flag.
- Non-computed signals in a collapsed `ExpansionTile` "Not available (n)" with status and
  reason/pending inputs/missing/message.
- Wide grids scroll horizontally; nothing overflows on a 360 dp wide screen (test it with a
  360×640 surface).

Widget tests (`test/ride_summary_screen_test.dart`): each state, scalar formatting, a 1-axis and a
2-axis signal, the mismatch banner, the collapsed list, no overflow at 360 dp.

### MR-6 Record screen link + docs

- Record screen: for a local session whose upload state is `uploaded`, add a "Ride summary" action
  that opens MR-5 with the server's session id. First check in `vehicle-server/src/vehicle_server/
  ingest.py` that the stored session id equals the phone's local session id (the archive is
  `<session_id>.zip`; confirm what the server actually uses). If they can differ, **do not add the
  action**; write the finding into *For Claude*.
- Widget test: the action appears only for `uploaded` sessions and only when a server is
  configured.
- `README.md`: a short "Ride history" section (where it is, what it reads, read-only, needs the
  server URL + token from Settings). No version bump, no CHANGELOG release entry: releases are
  Claude's and the user's (D-036).

Checks (all must pass before each push), from `vehicle-mobile/`: `git submodule update --init`,
`flutter pub get`, `flutter analyze` (no issues), `flutter test`. If Flutter is not installed or
CI is the only place it runs, say so in the log and push anyway; the PR CI runs both.

## Finish

- Open the vehicle-mobile PR (body: task list, checks, screenshots optional), then the workspace PR
  for the log. Fill the log: Result table, Checks, Unsure about, For Claude.
- Do not merge anything.
- Put into *For Claude*: every place where the rules above were ambiguous and the choice you made,
  the real type of `skipped`, whether the server session id equals the local one (MR-6), where the
  cleartext warning lives and how you reused it, and any field of `ride_summary.py` that differed
  from this text.
