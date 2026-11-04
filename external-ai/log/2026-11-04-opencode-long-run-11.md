---
date: 2026-11-04
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-11-conn-capture
repos: [vehicle-analyzer, vehicle-workspace]
branches: [vehicle-analyzer:ext/opencode-analyzer-conn-capture, vehicle-workspace:ext/opencode-long-run-11-log]
prs: [vehicle-analyzer#41]
zone: green
review: pending
---

# vehicle-analyzer: open the conn listen-only capture

## Goal
Let vehicle-analyzer load a saved vehicle-connectivity-node listen-only serial capture as a
file-only log and report whether the capture is complete and trustworthy. No serial port, no
live source and no transmission.

## Changes
- `vehicle-analyzer/src/services/connCaptureParser.ts`: new parser for `F,`, `S,`, `FINAL,` and
  `S,END`/`FINAL,END` lines. It validates frames, drops malformed frames, counts skipped lines,
  records the banner, handles node restarts with a monotonic offset, and keeps the last complete
  summary block. Frames use the vehicle bus and ASC-compatible seconds.
- `vehicle-analyzer/src/services/ingestProtocol.ts`, `logIngest.ts`, `ingestClient.ts`:
  added `conn` to `IngestFormat`; route it through `parseConnCapture` in both the worker and the
  synchronous fallback; carry `ConnCaptureSummary` on the `done` message. Added detection from the
  banner or an `F,` line in the first 100 non-empty lines.
- `vehicle-analyzer/src/components/SyncPanel.tsx`, `Header.tsx`: accept `.asc`, `.csv`, `.log` and
  `.txt`; detect conn after reading; clear stale summaries; show the quality report in the existing
  Defs & logs view. No new top-level view.
- `vehicle-analyzer/src/components/CaptureQuality.tsx`, `src/services/captureQuality.ts`: counts
  (frames, IDs, duration, restarts, skipped/malformed), the four requested warnings, and the
  per-ID table sorted by id.
- `vehicle-analyzer/tests/connCaptureParser.test.ts`, `tests/captureQuality.test.ts`,
  `tests/components/CaptureQuality.test.tsx`, `tests/ingest.test.ts`: synthetic coverage for the
  parser, CRLF, noise/truncated lines, malformed frames, incomplete/FINAL blocks, restart,
  extended IDs, empty input, all warnings, clean capture, format detection and fallback ingest.
- `vehicle-analyzer/ui-tests/import.spec.ts`: conn file case and updated file-picker locator.
- `vehicle-analyzer/README.md`, `docs/ROADMAP.md`: document the capture workflow/lines and add
  A11 marked done with analyzer#41.
- `vehicle-workspace/external-ai/log/2026-11-04-opencode-long-run-11.md`: this log.

Commits on `ext/opencode-analyzer-conn-capture`:
- `015c944` feat(analyzer): parse conn listen-only capture logs
- `3f620ea` feat(analyzer): load conn listen-only captures as logs
- `5f1e3cf` feat(analyzer): report conn capture quality
- `016bf14` docs(analyzer): document opening a conn listen-only capture
- `f60654f` docs(analyzer): link the conn capture PR from the roadmap
- `94473fb` fix(analyzer): detect a conn banner after boot noise

## Result
- PR https://github.com/vehicle-platform/vehicle-analyzer/pull/41 is open, MERGEABLE and not merged.
- CI `test`: SUCCESS.
- The analyzer imports a synthetic conn capture, shows its quality report, and keeps ASC/CSV
  behavior unchanged. A real Q-001 capture was not available in this session.

## Checks
- `git submodule update --init && npm ci`: pass. `npm ci` reports 5 existing audit vulnerabilities
  (3 moderate, 2 critical); no dependency or lockfile change was made by this run.
- `npm test`: 285 tests passed (39 files).
- `npm run build`: pass (`tsc -b && vite build`); only the existing Vite chunk-size warning.
- `npm run test:ui`: 18 tests passed.
- After the last detection change, `npm run test:ui -- ui-tests/import.spec.ts`: 3 tests passed.
- `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: all changed paths GREEN.
- PR CI `test`: SUCCESS.

## Unsure about
- No real capture was tested; parser behavior is checked against synthetic strings and the
  vehicle-connectivity-node source/native test only.
- Detection scans the first 100 non-empty lines for the banner or an `F,` line. A very long
  non-conn preamble beyond that would not be detected; this was raised from 20 after boot-noise
  testing.
- Restart handling preserves monotonic order by placing the next frame one microsecond after the
  previous adjusted timestamp. It does not model the real boot delay after a reset.
- The chosen block is the last complete block. If periodic `S` summaries continue after `FINAL`,
  that later `S` block wins; this follows the task wording but is worth checking against a real
  capture.
- The quality report is inside the existing Defs & logs view and disappears when leaving that tab,
  like the existing import status. No new tab was added.
- `npm ci` reports 5 vulnerabilities in the locked dependency tree; they are not introduced here
  and were not changed.
- Commit `94473fb` has the trailer `AI-Agent: opencode/deepseek-v4-flash-free` instead of
  `opencode/deepseek-v4.1-flash-free`. It was not amended because force-pushing is not allowed.

## For Claude
- No red-zone requests and no changes in `src/services/webSerialCan*`,
  `src/services/udsComposer*`, `src-tauri/*`, `src/defs/*` or `package.json`.
- Please review the parser against a real Q-001 capture when one exists, especially boot-noise
  length, summary-line interleaving and the `FINAL` versus later `S` block choice.
- Consider whether the quality report should persist across tab changes (currently tied to the
  Defs & logs view) and whether the warning wording/placement is acceptable.
- PR #41 is open and must not be merged by an external tool; Claude/user reviews it.
