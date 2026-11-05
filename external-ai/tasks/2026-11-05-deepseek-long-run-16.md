# DeepSeek long run 16 — 2026-11-05 (per-gear ride summaries in the analyzer and the phone)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR16-0 (first!) and LR16-5 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-16-log` | green |
| LR16-1, LR16-2 | vehicle-analyzer | `ext/opencode-analyzer-per-gear` | green (red: `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`; yellow `src/defs/*`, `package.json`: do not touch) |
| LR16-3, LR16-4 | vehicle-mobile | `ext/opencode-mobile-per-gear` | green (yellow: `lib/services/session_upload*`, `lib/services/upload_client*`, `pubspec.yaml`; red: `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`: do not touch) |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

vehicle-server#52 (defs v0.24.0, D-103) added the first **per-gear** class-B ride summary:
`ride_final_drive_ratio`, one value per gear. `GET /sessions/{id}/summary` now returns, for such a
signal, a third kind next to `scalar` and `binned`:

```json
{"name": "ride_final_drive_ratio", "status": "computed", "unit": "ratio", "range": [2.0, 3.5],
 "kind": "per_gear", "gears": [{"gear": 1, "value": 2.64, "flag": null},
                               {"gear": 4, "value": null, "flag": "no_steady_samples"}]}
```

Only the gears that have a stored row are listed (sorted by gear), `value` may be `null` with a
`flag`. `/rides` does not carry per-gear signals. Today vehicle-analyzer shows such an entry as
"malformed" (its parser knows only `scalar` and `binned`) and vehicle-mobile as "unsupported kind".
This run renders it in both front ends. Read-only: nothing is computed, no new server route.

No decision is needed from the user. If something here contradicts a decision (vehicle-defs
`docs/DECISIONS.md`: D-033, D-085, D-098, D-103) or a repo's `CLAUDE.md`, the decision text wins:
write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clones `vehicle-analyzer/`, `vehicle-mobile/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area).
- For each repo: `git -C <repo> checkout main && git -C <repo> pull && git -C <repo> submodule
  update --init`, then `git -C <repo> checkout -b <branch from the table>`. In the workspace:
  `git checkout main && git pull && git checkout -b ext/opencode-long-run-16-log`. Right after
  creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root (zones, branches, trailer, log format, the check table §4).
  Before each push run `python3 scripts/check_zones.py <repo> --base origin/main` from the
  workspace root. **Red or yellow = stop and revert that path**, write the request into the log.
- The server contract (read only): vehicle-server `src/vehicle_server/ride_summary.py`
  (`_per_gear_entry`, `_signal_entry`) and the README section on per-gear summaries.
- vehicle-analyzer: `src/services/sessionClient.ts` (the summary parser: `scalar`, `binned`,
  `malformedSummary`), `src/components/RideSummary.tsx` (the card in view E), the Compare view
  (key A) A/B summary table and `src/services/rideSummaryLayout.ts`; their tests.
- vehicle-mobile: `lib/models/ride_summary.dart` (the `kind` switch with the unsupported-kind
  fallback), `lib/ui/rides/ride_summary_screen.dart`, `lib/ui/rides/ride_widgets.dart`,
  `ride_format.dart`; `test/ride_summary_model_test.dart`, `test/ride_summary_screen_test.dart`.

### Hard rules for this run

1. **Render, never compute.** Show the server's gears, values and flags. No averaging across gears,
   no gear inferred, no value derived. A missing gear is simply not listed.
2. **Unit and precision from the response / defs as the existing scalar rows do** (the same
   formatting helper; E-27 precision rule). Never a hand-written unit or signal name.
3. **Forward compatible.** Unknown future kinds keep the existing fallback (analyzer "malformed" or
   a dedicated "unsupported kind" row; phone "unsupported kind"); a malformed `gears` list (not a
   list, a non-integer gear, a non-number value) becomes that one entry's malformed/unavailable row,
   never a failed card or screen.
4. **No position, no real data in git, no new dependency.**

## LR16-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-05-opencode-long-run-16.md` on
`ext/opencode-long-run-16-log`, `review: pending`, fill the header and the task list, commit and
push before any code. Update it after every later task.

## LR16-1 — Analyzer: parser and card

1. `sessionClient.ts`: a `PerGearSummary` type (`kind: 'per_gear'`, `unit`, `range`, `gears:
   {gear, value, flag}[]`) and its parser with the rules above; tests for a valid entry, `null`
   values with flags, an empty `gears` list, and each malformed case.
2. `RideSummary.tsx` (view E card): a per-gear entry renders as a small table or row group "gear n:
   value unit (flag)", in gear order, with the existing styles. Component test.

## LR16-2 — Analyzer: Compare and checks

1. Compare (key A): a per-gear signal shows one row per gear present in A or B; a gear present on
   one side only shows "—" on the other; the difference column (if the table has one) only where
   both values are numbers. Component test.
2. `docs/ROADMAP.md`: add the item (next free id) and mark it done with the PR link.
3. Run the analyzer checks of `AGENTS.md` §4 (`npm test`, `npm run build`, Playwright if you
   changed a covered view), the zone check, and open **one** PR from
   `ext/opencode-analyzer-per-gear` to `main`; do not merge it.

## LR16-3 — Phone: model and screen

1. `ride_summary.dart`: a `PerGearSummary` with `fromJson` (strict like the other kinds; a malformed
   entry becomes the existing unavailable row with a reason) and the `kind` switch entry; model
   tests.
2. `ride_summary_screen.dart`: a per-gear entry renders as one line per gear ("Gear n" + value with
   the unit + flag), with the existing widgets; widget test at a phone size (360×690) without
   overflow.

## LR16-4 — Phone: checks and PR

`flutter analyze` and `flutter test` (Flutter 3.47.5 like CI), the zone check, and **one** PR from
`ext/opencode-mobile-per-gear` to `main`; do not merge it. `pubspec.lock` must not change (revert
it if `flutter pub get` rewrites it).

## LR16-5 — Close the log

Finish the log: every task, commit, check result (test counts), both zone results, both PR links,
every doubt (*Unsure about*) and every request (*For Claude*). Keep `review: pending`. Push the
branch; no PR needed.
