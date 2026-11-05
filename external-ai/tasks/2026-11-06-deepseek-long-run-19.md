# DeepSeek long run 19 — 2026-11-06 (overnight continuation of long run 18)

Written by Claude for opencode/DeepSeek. **Run this file right after long run 18**
(`external-ai/tasks/2026-11-05-deepseek-long-run-18.md`) in the same night, without asking between
tasks. If long run 18 is not finished yet, finish it first. Commit after every task (Conventional
Commits, `AI-Agent: opencode/<model>` trailer) and push after every commit. If a task is blocked,
write why in the log's *For Claude* section and go on to the next one. **Never merge a PR.**

| Task | Repo | Branch (always cut from `main`, never from another `ext/` branch) | Zone |
|---|---|---|---|
| LR19-0 (first!) and LR19-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-19-log` | green |
| LR19-1 | vehicle-server | `ext/opencode-server-window-invariants` | green (red: `src/vehicle_server/derived/health_windows.py` for this run, see rule 1) |
| LR19-2 ... LR19-3 | vehicle-mobile | `ext/opencode-mobile-health-windows` | green (yellow: `pubspec.yaml`, `lib/services/session_upload*`, `lib/services/upload_client*`; red: `external/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`: do not touch) |
| LR19-4 ... LR19-5 | vehicle-server | `ext/opencode-server-demo-session` | green (yellow: any path with `gps`, `position`, `mdf4`, `pyproject.toml`, `uv.lock`; red: `*ota*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`) |

## 0. Before you start

Section 0 of long run 18 (visibility in VS Code / GitLens, `python3 scripts/vscode_workspace.py`
after each new branch and at the end, `AGENTS.md`, the zone check before each push, normal git
config) applies here unchanged. Read it again if it is not in your context any more.

### Why this run

Long run 18 stores the D-079 window instances in the `derived_summary` report block
(`health_windows`) and shows them in vehicle-analyzer. This run (a) tests the provisional window
state machine against general properties, so the user can trust the instances on the first real
rides, (b) shows the same block on the phone, and (c) gives the user a **synthetic** demo session
that exercises every window, so all cards can be checked on the desk before G1.

### Hard rules for this run

1. **No window rule changes.** `src/vehicle_server/derived/health_windows.py`,
   `health_window_summaries.py`, `summary.py` and every derived formula stay byte-identical in this
   run. A property that fails is recorded (rule in LR19-1), never "fixed".
2. **Golden vectors unchanged:** `uv run pytest tests/test_golden.py tests/test_golden_b.py` passes
   on every server branch; `tests/golden/MANIFEST.sha256` untouched.
3. **Never real data, never a position (D-033, D-076).** Everything generated in this run is
   synthetic and named so (`synthetic-demo-...`). No GPS block in the demo session, no latitude /
   longitude / altitude anywhere.
4. **No new dependency** in any repo (`pyproject.toml`, `uv.lock`, `pubspec.yaml` unchanged). Use
   the Python stdlib `random` with a fixed seed, not `hypothesis`.
5. **The phone renders what the server sent.** The mobile defs pin is old (D-089 item 3); do not
   bump it and do not copy window descriptions from defs. Window keys, times and close reasons are
   shown verbatim from the response; signal names / units from the `/summary` response as the ride
   summary screen already does.
6. **No new server route, no CLI subcommand, no change to `/summary`, `/rides`, `/series`,
   `/report` code** in this run.

## LR19-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-06-opencode-long-run-19.md` on
`ext/opencode-long-run-19-log` (cut from workspace `main`), `review: pending`, header + task list,
commit and push before any code. Update it after every later task.

## LR19-1 — Server: property tests for the window state machine

Read: `src/vehicle_server/derived/health_windows.py` (module docstring, `WindowInput`,
`WindowInstance`, `WindowResult`, `evaluate_window`, the `CLOSE_*` reasons), the README section
"D-079 health windows (provisional)", `tests/test_health_windows.py` (how specs and inputs are
built). Read only, do not edit (rule 1).

1. New `tests/test_health_windows_properties.py`. For each window of `vehicle_derived.WINDOWS` and
   **200 seeded random synthetic input sets** each (`random.Random(seed)`, seeds 0..199, all
   reproducible; inputs built like the existing tests: piecewise-constant values that cross the
   window's own condition / stable thresholds read from the spec, random gaps longer and shorter
   than the inputs' staleness, random session lengths), check:
   - instances are in time order and do not overlap (`end` of one <= `start` of the next);
   - `start_ms <= end_ms` and `duration_ms == end_ms - start_ms` for every instance;
   - every `close_reason` is one of the `CLOSE_*` constants;
   - `first_qualifying` is `None` exactly when no instance qualifies, otherwise it is the earliest
     qualifying instance;
   - every qualifying instance respects the window's min / max duration from the spec (as the code
     and README state the qualifying rule; quote the rule in the test docstring);
   - determinism: evaluating the same inputs twice gives equal results;
   - time shift: adding the same constant (e.g. 1 000 000 ms) to every timestamp shifts every
     instance by exactly that constant and changes nothing else;
   - no inputs / all inputs stale: no qualifying instance.
2. **When a property fails:** do not touch the state machine. Find the smallest failing seed,
   keep the test with `pytest.mark.xfail(strict=True, reason="<what fails, seed N>")`, and write
   into *For Claude*: the window, the property, the seed, the input series, the instances you got
   and what you expected. That is the most valuable output of this task.
3. Keep the file under ~10 s run time (`uv run pytest tests/test_health_windows_properties.py
   --durations=5`); lower the seed count if needed and say so in the log.
4. `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the golden tests (rule
   2), the zone check. Open **one** PR to `main`; do not merge. PR body: the property list, the
   xfail list (or "none").

## LR19-2 — Mobile: read the block

Read: vehicle-mobile `CLAUDE.md`, `lib/services/ride_client.dart` (`_get`, `getSummary`,
`RideResult`), `lib/models/ride_summary.dart` (defensive parsing style), `lib/models/bringup_result.dart`,
`test/ride_client_test.dart`, `test/ride_summary_model_test.dart`, and the `health_windows` block
format in long run 18 task LR18-2.

1. `RideClient.getReport({...})`: `GET /sessions/{id}/report` (JSON, token in the `Authorization`
   header exactly like `getSummary`), returning the decoded JSON object through the same
   `RideResult` error handling. GET only.
2. New `lib/models/health_windows.dart`: a pure parser of `report["derived_summary"]["health_windows"]`
   in the defensive style of `ride_summary.dart`: a model `{rule, t0DeviceMs, windows (in response
   order): key, qualifyingCount, instances (startMs, endMs, durationMs, closeReason, qualifies,
   firstQualifying)}` or a reason (`not in report` when the block or key is missing,
   `malformed: <what>` otherwise). Reject (never guess) an instance with `end_ms < start_ms`,
   `duration_ms != end_ms - start_ms`, a non-integer time, or more than one `first_qualifying`.
3. Tests: `test/health_windows_model_test.dart` (valid, missing, each malformed case, order kept)
   and `getReport` cases in `test/ride_client_test.dart` (header, 401/404/timeout like the existing
   cases). `flutter analyze` and `flutter test` green.

## LR19-3 — Mobile: health windows on the ride summary screen

Read: `lib/ui/rides/ride_summary_screen.dart`, `ride_widgets.dart`, `ride_format.dart`,
`test/ride_summary_screen_test.dart`.

1. On the ride summary screen, below the existing summary content, a **Health windows** section
   loaded with `getReport` for the same session (one request, after the summary; a failure there
   never hides the summary):
   - a "provisional" chip with the `rule` text;
   - per window (response order): key, `N instances, M qualifying`, a thin timeline bar
     (`CustomPaint`, no new package) with one segment per instance on a 0..last-instance-end axis,
     qualifying segments filled, the first qualifying one marked; below it a compact table
     (start s, end s, duration s, close reason, qualifies) with times formatted by the existing
     `ride_format.dart` helpers;
   - the window's signals: rows of the `/summary` response whose name starts with `window_`
     **and** whose response entry carries that window key, if the response has such a field;
     otherwise show no signal rows and write into *For Claude* that the phone cannot map signals to
     windows without a newer defs pin (do not guess from names);
   - block missing: "No window instances in this report (older server, or run
     `vehicle-server derive <id>` on the server)."; malformed: the reason text.
2. Widget tests: the three states, segment count = instance count, first-qualifying marking, a
   failing `getReport` with a working summary.
3. `flutter analyze`, `flutter test`, the zone check (`pubspec.yaml` untouched). Open **one** PR
   to `main`; do not merge. PR body: "needs vehicle-server LR18 PR <n> (the report block); merge
   the server PR first".

## LR19-4 — Server: a synthetic demo session

Read: `tests/make_fixtures.py` (how fixture sessions are built from the schema, never from byte
offsets), `tests/fixtures/` layout, `ingest.py` (what `vehicle-server import` accepts: folder or
zip), `tests/test_health_windows_ingest.py` (the synthetic ride that already opens windows) and the
`vehicle_derived.WINDOWS` conditions.

1. New `scripts/make_demo_session.py` (run as `uv run python scripts/make_demo_session.py --out
   <dir> [--zip]`): writes **one synthetic session** named `synthetic-demo-<YYYYMMDD>` in the format
   `vehicle-server import` accepts, built with the same helpers / schema path as
   `tests/make_fixtures.py` (import or reuse them; no hand-written byte offsets, no copied schema).
   About 20 minutes of ride time, no GPS block (rule 3), with:
   - a cold start that warms up (W1/W2 per their defs conditions), warm idles (W3: one qualifying,
     one too short), cruise segments in at least three gears (W4 and the `per_gear` summary), a
     decel / stop (W5 and at least two D-075 stop epochs), and one input gap longer than its
     staleness inside a window;
   - every value inside the DBC / DID ranges of `vehicle_defs`; the session metadata says
     `synthetic: true` wherever the meta format allows it, and the README says so too.
   Deterministic: two runs give byte-identical output (fixed seed, fixed timestamps).
2. Do **not** commit the generated session (the script is the artifact; `.gitignore` the default
   output folder if one is used).

## LR19-5 — Server: test, README, PR

1. `tests/test_demo_session.py`: generate into `tmp_path`, `vehicle-server import` it through the
   same function the CLI uses, then assert: ingest has no `derived.error` / `derived_summary.error`;
   every window W1-W5 has at least one non-null `window_*` scalar in `derived_summary`; the
   `per_gear` summary has at least three gear rows; at least two stop epochs; no GPS / position
   column anywhere in the stored session; determinism (two generations byte-identical). If a
   window does not qualify although the series was meant to open it, adjust the **series**, never
   the rule; if you cannot make it qualify, `xfail(strict=True)` + *For Claude* with the reason.
2. README: a short "Synthetic demo session" paragraph: the command, `vehicle-server import`, then
   view it in vehicle-analyzer E (and, once LR18 is merged, the Health windows card) and on the
   phone; "synthetic, never a real ride".
3. `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the golden tests (rule
   2), the zone check. Open **one** PR to `main`; do not merge.

## LR19-6 — Close the log

Finish the log: every task, commit, check result (test counts, property-test run time), the zone
results, the three PR links (server invariants, mobile, server demo), every xfail with its seed,
every doubt (*Unsure about*) and every request (*For Claude*). Keep `review: pending`. Run
`python3 scripts/vscode_workspace.py` one last time. Push the branch; no PR needed.
