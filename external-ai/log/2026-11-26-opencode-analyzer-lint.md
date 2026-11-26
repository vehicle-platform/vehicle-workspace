---
date: 2026-11-26
tool: opencode/deepseek-v4.1-flash-free
topic: analyzer-lint
repos: [vehicle-workspace, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-analyzer-lint-log, vehicle-analyzer:ext/opencode-analyzer-lint]
prs: []
zone: yellow
review: pending
---

# analyzer lint ratchet down

## Goal
Run L1-0 to L1-4 of `external-ai/tasks/2026-11-26-deepseek-analyzer-lint.md`: fix ESLint warnings in
`vehicle-analyzer` in green files only, lower `--max-warnings` to the new count and open the PR.

## Baseline (L1-0)

`npx eslint . -f json` on `main` at `2e5e779`, Node 25.2.1, `npm ci` (506 packages): **302 warnings,
0 errors** — exactly the `--max-warnings 302` ratchet.

| Rule | Count |
|---|---|
| `@typescript-eslint/no-unsafe-member-access` | 193 |
| `@typescript-eslint/no-unsafe-assignment` | 32 |
| `@typescript-eslint/no-explicit-any` | 25 |
| `@typescript-eslint/no-unsafe-call` | 12 |
| `@typescript-eslint/no-unsafe-argument` | 12 |
| `react-hooks/set-state-in-effect` | 9 |
| `react-hooks/static-components` | 8 |
| `react-hooks/refs` | 6 |
| `react-hooks/exhaustive-deps` | 4 |
| `@typescript-eslint/no-unsafe-return` | 1 |
| **Total** | **302** |

Per file: `src/defs/model.ts` has **267** warnings (yellow zone, `src/defs/*`); the remaining **35**
are in green files (`src/components/*`, `src/services/{dbcParser,sniffer}.ts`,
`src/state/{captureStore,ring}.ts`, `src/ui/{keys,useCanvas}.ts`). The red files
(`src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`) have no warnings.

## Changes
- `vehicle-workspace/external-ai/log/2026-11-26-opencode-analyzer-lint.md`: this session log (L1-0).
- (L1-1..L1-4 filled in below.)

## Result
(filled in L1-4)

## Checks
- `npx eslint . -f json`: 302 warnings, 0 errors (baseline)
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-opencode-analyzer-lint.md`: green

## Unsure about
(filled in L1-4)

## For Claude
- `src/defs/model.ts` (yellow) holds 267 of the 302 warnings. The task says green files only, so it was
  skipped; reaching the ≤ 150 goal needs a typing pass over that file (or an explicit go-ahead for
  yellow edits).

## Claude review
(Filled by Claude's /external-review: findings, fixes, PRs.)
