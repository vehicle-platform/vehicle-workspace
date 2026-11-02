---
date: 2026-11-02
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-7-mobile-ride-history
repos: [vehicle-mobile, vehicle-workspace]
branches: [vehicle-mobile:ext/opencode-mobile-ride-history, vehicle-workspace:ext/opencode-long-run-7-log]
prs: []
zone: green
review: pending
---

# long-run-7 mobile ride history

## Goal
Add read-only ride history and ride summary views to vehicle-mobile, using the existing vehicle-server `GET /rides` and `GET /sessions/{id}/summary` routes. No new summary, formula, signal, dependency or server route.

## Changes
- `vehicle-mobile/lib/models/ride_summary.dart`: strict models for both responses (MR-1).
- `vehicle-mobile/lib/services/ride_client.dart`: read-only GET client (MR-2).
- `vehicle-mobile/lib/ui/rides/ride_format.dart`: shared precision/formatting helpers (MR-3).
- `vehicle-mobile/lib/ui/rides/ride_history_screen.dart`: cross-session ride history (MR-4).
- `vehicle-mobile/lib/ui/rides/ride_summary_screen.dart`: one-session ride summary (MR-5).
- `vehicle-mobile/lib/ui/record_screen.dart`, `README.md`: Record-screen link and docs (MR-6).
- MR-6 verified that `vehicle-server/src/vehicle_server/ingest.py` stores the `session_id` from `meta.json`, and `session_recorder.dart` writes the same generated id into the session directory name and `meta.json`; an uploaded local session therefore uses the server's stored id.

## Result

| Task | Status | Evidence |
|---|---|---|
| MR-1 Models + strict parsing | done | `vehicle-mobile/lib/models/ride_summary.dart`; `test/ride_summary_model_test.dart`; commit `67202a6` |
| MR-2 Read client | done | `vehicle-mobile/lib/services/ride_client.dart`, `lib/services/http_message.dart`; `test/ride_client_test.dart`; commit `4e111bd` |
| MR-3 Formatting helpers | done | `vehicle-mobile/lib/ui/rides/ride_format.dart`; `test/ride_format_test.dart`; commit `9781f7c` |
| MR-4 Ride history screen | done | `vehicle-mobile/lib/ui/rides/ride_history_screen.dart`, `ride_widgets.dart`; `test/ride_history_screen_test.dart`; commit `8cb9645` |
| MR-5 Ride summary screen | done | `vehicle-mobile/lib/ui/rides/ride_summary_screen.dart`; `test/ride_summary_screen_test.dart`; commit `310787d` |
| MR-6 Record link + docs | done | `vehicle-mobile/lib/ui/record_screen.dart`, `README.md`; `test/record_ride_actions_test.dart`; commit `4eb401e` |

## Checks
- Local Flutter found at `~/development/flutter/bin/flutter` (3.44.8, Dart 3.12.2): `flutter analyze` clean and `flutter test` 293 passing after MR-6. `pubspec.lock` was restored after each run (no lock rewrite committed).
- Zone check: `GREEN` for every changed path.

## Unsure about
- `GET /rides` `skipped` is an `int` count of sessions inside the requested range whose `derived_summary` block is missing or errored, not a list. MR-1 models it as `int`.
- The server rejects names that are not class-B scalars; the app renders only the response columns.
- `GET /rides` columns carry no per-signal range, so history rows use the observed min/max of that column in the current response for the MR-3 precision rule; the summary screen uses the response range.
- MR-1 strict-field tests expected labels that were not in the model's field-path messages; commit `5ebbed4` aligns the expectations with `axes[0].unit`, `cells[0].axes`, `signals[3].name`/`status`.
- MR-5 orientation follows the task text literally (rows = `axes[1]`, columns = `axes[0]`), so the cell lookup is `[column, row]`; the analyzer `RideSummary.tsx` currently draws `axes[0]` as rows. The task text was treated as authoritative.

## For Claude
- No red-zone or yellow-zone change. `pubspec.yaml` unchanged.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
