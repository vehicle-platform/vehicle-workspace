---
date: 2026-11-26
tool: opencode/deepseek-v4.1-flash-free
topic: analyzer-lint
repos: [vehicle-workspace, vehicle-analyzer]
branches: [vehicle-workspace:ext/opencode-analyzer-lint-log, vehicle-analyzer:ext/opencode-analyzer-lint]
prs: []
zone: yellow
review: done 2026-11-26 (merge; analyzer#80 commits merged via analyzer#81 with Claude's model.ts typing, warnings 302 → 0)
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
- vehicle-analyzer `ext/opencode-analyzer-lint` (5 commits, PR #80): typed arrays, ref writes into effects, static components hoisted, async state derived by request key, TracePanel scroll/viewport derived, `useElementSize` `active` flag, SyncPanel cancellation keyed on source change, `--max-warnings` 302 → 267.

## Result
302 → 267 warnings in green files (all react-hooks warnings cleared); the run stopped before L1-4 when DeepSeek's usage ran out, so Claude filled this log.

## Checks
- `npx eslint . -f json`: 302 warnings, 0 errors (baseline)
- `python3 scripts/check_zones.py . --path external-ai/log/2026-11-26-opencode-analyzer-lint.md`: green

## Unsure about
(not filled: run ended early)

## For Claude
- `src/defs/model.ts` (yellow) holds 267 of the 302 warnings. The task says green files only, so it was
  skipped; reaching the ≤ 150 goal needs a typing pass over that file (or an explicit go-ahead for
  yellow edits).

## Claude review
2026-11-26, Claude:
- Zones: all changed source files green; `package.json` yellow (ratchet tightening only). No red path.
- `architecture-guard`: **merge**, no blocking finding. Notes: SyncPanel's cancellation effect now re-runs on every import progress tick (harmless, guarded by the previous-source ref); TracePanel follow mode derives `scrollTop` from row count and a ResizeObserver height (fine while the ring is full; worth one manual scroll-mode check). No `eslint-disable`, no rule change, no transmit path, red paths untouched (D-081).
- Fix on top (analyzer#81, branch `claude/analyzer-lint-finish`, DeepSeek's commits kept): `src/defs/model.ts` typed with narrow `unknown` guards, malformed defs now throw a `defs:` error (8 new tests); warnings 267 → **0**, `--max-warnings 0`. CI green (unit + coverage, UI tests, desktop, hal-linux).
- *For Claude* request (model.ts) done by analyzer#81. Open: a manual TracePanel follow/scroll check on the next analyzer session.
