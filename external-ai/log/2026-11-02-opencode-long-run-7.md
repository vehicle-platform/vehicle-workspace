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

## Result

| Task | Status | Evidence |
|---|---|---|
| MR-1 Models + strict parsing | done | `vehicle-mobile/lib/models/ride_summary.dart`; `test/ride_summary_model_test.dart`; commit `67202a6` |
| MR-2 Read client | todo | |
| MR-3 Formatting helpers | todo | |
| MR-4 Ride history screen | todo | |
| MR-5 Ride summary screen | todo | |
| MR-6 Record link + docs | todo | |

## Checks
- Local Flutter toolchain: not installed in this session (`flutter` not found); CI runs `flutter analyze` and `flutter test`.

## Unsure about
- `GET /rides` `skipped` is an `int` count of sessions inside the requested range whose `derived_summary` block is missing or errored, not a list. MR-1 models it as `int`.
- The server rejects names that are not class-B scalars; the app renders only the response columns.

## For Claude
- Flutter is not installed locally; only CI can run analyze/tests for this run.

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
