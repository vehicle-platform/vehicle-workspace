# DeepSeek long run 11 — 2026-11-04 (vehicle-analyzer: open the conn listen-only capture)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR11-1..LR11-4 | vehicle-analyzer | `ext/opencode-analyzer-conn-capture` | green (red: `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`; yellow: `src/defs/*`, `package.json`: do not touch them) |
| LR11-5 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-11-log` | green |

Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

### Why this run

The first real data of the project will be the **Q-001 listen-only capture** on the Honda CL250
(gate G1 in `STATUS.md`): the bike ESP32 runs the build env `esp32-s3-devkitc-1-listen-only`
(vehicle-connectivity-node, D-058 item 4), receives every frame on the vehicle bus without ever
transmitting, and writes text lines to USB serial at 921600 baud. Today nothing in the platform
can open that text. This run lets vehicle-analyzer load such a saved serial log like an ASC or CSV
log, and shows whether the capture is complete and trustworthy. It is file-only: no serial port,
no live source, no transmission of any kind.

No decision is needed from the user for this run. If something here contradicts a decision
(vehicle-defs `docs/DECISIONS.md`: D-033, D-040, D-058, D-081) or vehicle-analyzer `CLAUDE.md`,
the decision text wins: write the conflict into *For Claude* and skip that part.

### Visibility (the user follows your work in VS Code / GitLens)

- Work in the main clone `vehicle-analyzer/` (not under `.claude/worktrees/`, that is Claude's area).
- First `git -C vehicle-analyzer checkout main && git -C vehicle-analyzer pull`, then
  `git checkout -b ext/opencode-analyzer-conn-capture`. Right after that, and again at the end,
  run from the workspace root: `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.

### Read

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format, the check table
  (§4). Before each push run `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`
  from the workspace root. **Red or yellow = stop and revert that path**, write the request into
  the log.
- vehicle-analyzer `CLAUDE.md` and `docs/ROADMAP.md`.
- The capture format, **the only source of truth for it**:
  `vehicle-connectivity-node/src/CanCaptureCore.h` (comment block at the top) and
  `src/CanCaptureModule.cpp` (the `#` banner lines). Read them; do not edit anything in
  vehicle-connectivity-node (its `src/CanCapture*` is red).
- vehicle-analyzer code: `src/types/can.ts` (`CanFrame`: `bus`, `timestamp` and their units),
  `src/services/logParser.ts` (`parseVectorAsc`, `parseCanCsv`: how they set `bus` and
  `timestamp`), `src/services/logIngest.ts`, `src/services/ingestProtocol.ts`
  (`ParseLogRequest['format']`), `src/services/ingest.worker.ts`, `src/services/ingestClient.ts`,
  the component that picks a log file and its format (search for `parseLogFrames` / `format`
  callers), `src/state/channels.ts`, and the existing tests in `tests/`.

### Hard rules for this run

1. **Never transmit, never open a port.** This is a file parser and a report. Do not touch the
   Web Serial / SLCAN code or the UDS composer (red).
2. **No invented signals or IDs (invariant 2).** The parser never hard-codes a CAN ID. Which IDs
   are "watched" (the OBD functional request IDs, D-040) comes from the `W` flag in the file's
   summary rows, not from a list in the analyzer. Test fixtures use generic IDs (for example
   `100`, `200`, `7FF`, an extended `00012345`), never a CL250 ID copied from the DBC.
3. **No real data in git (D-033).** Fixtures are synthetic strings written in the test. Never
   commit a real capture, a serial log from the user's desk, or anything with a VIN.
4. **No new dependency.** `package.json` is yellow; the parser is plain TypeScript.
5. Frames of a conn capture belong to the **vehicle bus**. Use the bus name the analyzer already
   uses for the vehicle bus (see how ASC/CSV frames and `channels.ts` name it); never add a new
   bus name.

## LR11-1 — Parser

1. New `src/services/connCaptureParser.ts` exporting `parseConnCapture(text: string)` that
   returns `{ frames: CanFrame[], summary: ConnCaptureSummary }`.
2. Lines (split on `\n`, strip a trailing `\r`):
   - `#...` → comment; remember whether the banner
     `# vehicle-connectivity-node CAN capture` was seen.
   - `F,<t_us>,<id hex>,<S|X>,<dlc>,<data hex>` → one frame. Validate: `t_us` a non-negative
     integer; standard id ≤ 0x7FF with `S`, extended ≤ 0x1FFFFFFF with `X`; `dlc` 0-8; the data
     hex has exactly `2 × dlc` hex digits. Convert `t_us` to the `CanFrame.timestamp` unit the
     ASC parser uses.
   - `S,...` / `FINAL,...` rows and their `S,END,...` / `FINAL,END,...`-style END line (check the
     exact END spelling in `CanCaptureCore.h` and its native test if one exists) → summary
     blocks. Keep the **last complete** block (a block is complete when its END line was read);
     prefer the last `FINAL` block if it is the last complete one, otherwise the last `S` block.
   - Anything else (serial noise at the start, a truncated last line, a boot message) → skipped
     and counted in `summary.skippedLines`; a malformed `F` line is counted in
     `summary.malformedFrames` and dropped. Never throw on bad input.
3. **Board restart:** the node clock restarts at 0 after a reset. When `t_us` goes backwards by
   more than one second relative to the previous frame, count a restart in `summary.restarts` and
   offset every later frame so that timestamps stay monotonic in file order (`parseLogFrames`
   sorts by timestamp, so without the offset two segments would interleave). Document the rule in
   the code comment.
4. `ConnCaptureSummary` holds: `bannerSeen`, `frames` (parsed), `skippedLines`,
   `malformedFrames`, `restarts`, `durationS` (from the first to the last frame, restarts
   included), and from the chosen summary block (or `null` if there is none): `final` (boolean),
   per-ID rows `{ id, extended, count, minGapMs, maxGapMs (null for '-'), watched }` and the END
   counters `{ frames, ids, overflow, lost, dropped }`.
5. Tests `tests/connCaptureParser.test.ts` (synthetic strings only): a clean capture with a
   banner, frames and one complete summary; CRLF line ends; noise before the banner and a
   truncated last line; each malformed-frame case of item 2; an incomplete last summary block
   (the previous complete one wins); a FINAL block; a restart with monotonic output; an extended
   ID; an empty file.

## LR11-2 — Load it like any other log

1. Add a `conn` (or similarly named, consistent with the existing values) format to
   `ParseLogRequest['format']` and route it in `parseLogFrames` / `runLogIngest`, so the Web
   Worker and the main-thread fallback both use `parseConnCapture` and produce identical frames.
2. Format choice: keep the existing ones unchanged. A file whose first non-empty lines contain the
   banner, or whose first parseable line is an `F,` line, is detected as `conn`; `.log` and
   `.txt` files are accepted by the file picker next to `.asc` and `.csv`. If the UI has an
   explicit format selector, add the option there too.
3. The summary must reach the UI: carry it through the ingest messages (for example on the
   `done` message) without breaking the ASC/CSV paths.
4. Tests: the worker/fallback path gives the same frames for a conn fixture; ASC and CSV tests
   still pass unchanged; detection picks `conn` for the banner and for a bare `F,` file and not
   for an ASC or CSV text.

## LR11-3 — Capture-quality report

Show the summary where the analyzer already shows information about a loaded log (find the
existing place; do not add a new top-level view key unless there is none, then say so in the
log):

- counts: frames, IDs, duration, restarts, skipped and malformed lines;
- **warnings**, each with one plain sentence:
  - `lost > 0` or `dropped > 0` or `overflow > 0` → "the capture is incomplete" (lost = driver
    lost frames, dropped = serial buffer full, overflow = more IDs than the node's table);
  - a watched row (`W`) with `count > 0` → "another tester was on the bus during the capture
    (D-040); this capture is not a clean listen-only baseline";
  - no summary block at all, or no `FINAL` block → "shorter than the 300 s capture window" (the
    node prints FINAL after 300 s);
  - `restarts > 0` → "the node restarted during the capture";
  - file frames ≠ END `frames` of the chosen block (beyond the frames received after that block)
    is **not** a warning: the END line counts only up to its own time. Do not invent a check here.
- the per-ID table (id, S/X, count, min/max gap ms, watched), sorted by id.

Tests: a component or unit test for each warning and for "no warning" on a clean capture. If the
analyzer has Playwright UI smoke tests that cover log loading, add one conn-file case.

## LR11-4 — Docs

1. `README.md` of vehicle-analyzer: a short *Opening a conn listen-only capture* section: what
   the file is (env `esp32-s3-devkitc-1-listen-only`, 921600 baud, text lines), that the file is
   saved by any serial terminal that writes the raw serial output to a file, and how to load it.
   Only write a concrete recording command if you verified it in the PlatformIO or tool
   documentation; otherwise describe it in words. State that a real capture stays on the user's
   machine and is never committed (D-033).
2. `docs/ROADMAP.md`: add the item (next free id, or under the log-import item if one exists)
   and mark it done with the PR link at the end.

## LR11-5 — Checks and log

1. Run the analyzer checks of `AGENTS.md` §4 (at least `npm test`, `npm run build`; the
   Playwright tests if you changed UI that they cover) and record each result.
2. `python3 scripts/check_zones.py vehicle-analyzer --base origin/main` → all green.
3. Open **one** PR from `ext/opencode-analyzer-conn-capture` to `main`; do not merge it.
4. Log: copy `external-ai/log/TEMPLATE.md` to
   `external-ai/log/2026-11-04-opencode-long-run-11.md` on branch `ext/opencode-long-run-11-log`
   in the workspace, `review: pending`, with every task, commit, check result, the zone result,
   every doubt (*Unsure about*) and every request (*For Claude*). Push the branch; no PR needed.
