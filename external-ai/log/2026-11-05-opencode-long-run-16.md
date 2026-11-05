---
date: 2026-11-05
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-16-per-gear-summaries
repos: [vehicle-workspace, vehicle-analyzer, vehicle-mobile]
branches: [vehicle-workspace:ext/opencode-long-run-16-log, vehicle-analyzer:ext/opencode-analyzer-per-gear, vehicle-mobile:ext/opencode-mobile-per-gear]
prs: [vehicle-analyzer#46, vehicle-mobile#30]
zone: green
review: pending
---

# Per-gear ride summaries in the analyzer and the phone

## Goal
Render the server's `per_gear` class-A ride summary (`ride_final_drive_ratio`, D-103) in
vehicle-analyzer (view E card and Compare A) and vehicle-mobile, using the server's gears,
values and flags verbatim. Read-only: no computation, no new route, no new dependency.

Task file: `external-ai/tasks/2026-11-05-deepseek-long-run-16.md`.

## Changes
- LR16-0 (vehicle-workspace, `ext/opencode-long-run-16-log`): created this log first, before code.
  Commit `b0ebd82`.
- LR16-1 (vehicle-analyzer, `ext/opencode-analyzer-per-gear`): added `PerGearSummary` and its
  strict parser to `src/services/sessionClient.ts`; a malformed `gears` list becomes that one
  signal's `error` row instead of failing the card. View E (`RideSummary.tsx`) renders a per-gear
  table (`gear n`, value, unit, flag) in gear order with the response range precision. Tests:
  valid/null/empty/malformed parse cases and a component test for order, unit, flag, precision and
  the malformed-entry fallback. Commit `baab380`.
- LR16-2 (vehicle-analyzer, `ext/opencode-analyzer-per-gear`): Compare A now emits one row per
  gear present in A or B (`<signal> gear n`), leaves `–` for a missing gear and computes only the
  B − A difference when both values are numbers. Added ROADMAP A14; component/unit tests and a
  Playwright per-gear assertion. Commits `baab380`, `50badbe`, `66fb9e2`; PR #46.
- LR16-3 (vehicle-mobile, `ext/opencode-mobile-per-gear`): added `PerGearSummary`/`PerGearValue`
  with strict JSON parsing and the `per_gear` switch case; a malformed entry becomes the existing
  `UnavailableSummary` row with status `malformed per_gear` and the reason. The ride summary screen
  renders one line per stored gear (`Gear n`, value with the response unit and flag), sorted by
  gear, and shows an empty-state line for an empty list. Model tests cover valid/null/empty/
  malformed lists; the widget test uses 360×690 and asserts no overflow. Commit `120c64c`.
- LR16-4 (vehicle-mobile, `ext/opencode-mobile-per-gear`): `flutter analyze --no-pub` and
  `flutter test --no-pub` passed; `pubspec.lock` was reverted after the local `flutter pub get`
  rewrite. PR #30.
- LR16-5 (vehicle-workspace, `ext/opencode-long-run-16-log`): finished this log with the commits,
  test counts, both zone results, both PR links, doubts and requests; branch pushed, no PR needed.

## Result
- Task progress: LR16-0..LR16-5 done. PRs: [vehicle-analyzer#46](https://github.com/vehicle-platform/vehicle-analyzer/pull/46)
  and [vehicle-mobile#30](https://github.com/vehicle-platform/vehicle-mobile/pull/30); both are open
  and not merged.

## Checks
- LR16-0 `python3 scripts/check_zones.py . --base origin/main`: GREEN (log path only).
- LR16-1 `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: GREEN (four changed
  files). `npm test`: 42 files, 328 tests passed. `npm run build`: passed.
- LR16-2 `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: GREEN (all changed
  files, including ROADMAP). `npm test`: 42 files, 330 tests passed. `npm run build`: passed.
  `npx playwright test ui-tests/ride-summary.spec.ts`: 2 tests passed.
- LR16-3/4 `python3 scripts/check_zones.py vehicle-mobile --base origin/main`: GREEN (four changed
  files). `flutter analyze --no-pub`: no issues. `flutter test --no-pub`: 327 tests passed.
  `pubspec.lock` is unchanged.
- LR16-5 `python3 scripts/check_zones.py . --base origin/main`: GREEN (this log only).
  `python3 scripts/vscode_workspace.py`: run after branch creation and again at close; the workspace
  file did not change.

## Unsure about
- The only installed local Flutter SDK is 3.44.8; CI and the task pin 3.47.5. The code uses no
  version-specific API, but the 3.47.5 CI run is the authoritative check.

## For Claude
- None: all changed paths are green, no red/yellow request, no decision conflict found.

## Claude review
(Filled by Claude's /external-review.)
