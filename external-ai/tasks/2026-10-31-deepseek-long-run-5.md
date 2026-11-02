# DeepSeek long run 5 — 2026-10-31 (relative ride track: server `/track` + analyzer Track view, A7a)

Written by Claude for opencode/DeepSeek. Work through the tasks **in order**, without asking
between tasks. **Commit after every task** (Conventional Commits, `AI-Agent: opencode/<model>`
trailer) and push the branch after every commit, so nothing is lost if your time runs out. If a
task is blocked, write why in the log's *For Claude* section and go on to the next one.

This run is larger than runs 1-4: two repos, Python and TypeScript, geometry, a new endpoint and a
new view. Read section 0 completely before writing code.

## 0. Before you start (read, do not skip)

- `AGENTS.md` at the workspace root: zones, branches, commit trailer, log format. Before each push
  run `python3 scripts/check_zones.py <repo> --base origin/main`. **Red = stop**, write the request
  into the log. `vehicle-server/src/vehicle_server/gps_track.py` is **yellow** (`*gps*`): the
  server PR needs the `needs-claude-review` note.
- `vehicle-server/CLAUDE.md` (Read API, Storage, Derived signals) and `vehicle-server/README.md`
  (the `/series` and `/stats` rows). Code: `src/vehicle_server/api.py` (auth, `/series`,
  `/stats`), `series.py` (t0 axis, `SessionInputs` use, name prefixes), `position.py` (the one
  position-name rule), `derived/inputs.py` (`SessionInputs`, sensor resolution, uint32 wrap
  removal), `decode.py` (GPS columns). Tests: `tests/test_series.py`, `tests/test_stats.py`,
  `tests/test_gps.py`, `tests/make_fixtures.py`, `tests/conftest.py`.
- `vehicle-analyzer/CLAUDE.md`, `docs/ROADMAP.md` (row A7), `src/services/sessionClient.ts`
  (`buildRequest`, `describeHttpError`, `parseSeriesResponse`), `src/components/SessionPanel.tsx`
  and `ComparePanel.tsx` (how a recorded session is chosen and opened), `src/services/replay.ts` +
  `src/state/` (replay transport and its current time), `src/App.tsx` + `src/ui/keys.ts` (view
  keys; `G` is free), `tests/components/`, `ui-tests/views.spec.ts`.
- Defs (read only): `external/vehicle-defs/derived/cl250_derived.yaml` sensors `gps_ground_speed`,
  `gps_heading`, `gps_fix_type`, `lean_angle` (unit, `sample_period_ms`, `stale_after_ms`);
  `external/vehicle-defs/ble/ble_schema.json` GPS `fixType` enum and `privacy` text.
- `vehicle-defs/docs/DECISIONS.md` **D-060** (GPS gives speed and heading only), **D-076** (position
  relaxation, provisional; item 3: *not implemented yet*), **D-033** (public repos), **D-081**
  (analyzer scope).

### Why "relative" (read this, it decides the design)

D-076 item 3 is not implemented: the server stores **no latitude, longitude or height**, only GNSS
ground speed, heading of motion, accuracies and fix type. So this run does **not** draw a map. It
reconstructs the ride's **shape** by dead reckoning from speed + heading, in metres relative to the
first usable sample (east = +x, north = +y), and draws it without any basemap. Absolute position
and self-hosted tiles stay for a later A7b, after D-076 item 3 lands (that needs defs, red zone).

Hard rules for the whole run:

- **No absolute position anywhere.** No field, column, query parameter or variable named like a
  position (`lat`, `lon`, `alt`, `height`, ...; see `position.py`). Use `x_m`, `y_m`.
- **No third-party request.** The analyzer view loads nothing from any host other than the
  configured vehicle-server (no tiles, CDN fonts, scripts or analytics). A test proves it (TR-6).
- **No new dependency** in either repo (the server has no numpy: use pyarrow + the standard
  library; the analyzer has no map or chart library for this: use a `<canvas>`).
- **Signals and constants from defs** (invariant 2): sensor names, units, `stale_after_ms` and the
  fix-type enum values are read from `vehicle_defs` / the pinned defs, never written as literals.
  Processing parameters (minimum speed for a trusted heading, simplification) are query
  parameters with documented defaults, not vehicle facts.
- All test data is **synthetic** (D-033). Never commit a real session, a real route or anything
  derived from one.

Branches (one PR per repo, each opened against `main`):

| Part | Repo | Branch | Tasks |
|---|---|---|---|
| A | vehicle-server | `ext/opencode-server-track` | TR-1 .. TR-3 |
| B | vehicle-analyzer | `ext/opencode-analyzer-track` | TR-4 .. TR-8 |
| Log | vehicle-workspace | `ext/opencode-long-run-5-log` | the session log |

One session log for the whole run: `external-ai/log/2026-10-31-opencode-long-run-5.md` (copy
`TEMPLATE.md`; `review: pending`; a result row per task with code `file:line`, test names, status).
Create and push the log branch **first**, with the Result table rows marked `todo`, and update it
as tasks finish.

## Part A — vehicle-server

### TR-1 Dead-reckoned track (`src/vehicle_server/gps_track.py`, pure functions)

A pure module, no FastAPI import, unit-testable without a stored session.

Input: the full-resolution series of `sensor.gps_ground_speed`, `sensor.gps_heading` and
`sensor.gps_fix_type`, resolved through `SessionInputs` exactly as `series.py` does (same time
axis, wrap removed). Output: a list of segments, each with `t_ms`, `x_m`, `y_m`, `speed_mps`,
`heading_deg` (equal-length lists) and `gap_before_ms` (`null` for the first segment).

Rules:
1. **Usable sample:** a fix type whose defs enum **name** is `fix2d`, `fix3d` or
   `gnssDeadReckoning` (look the values up by name in the defs BLE schema; never write `2`, `3`,
   `4`). `noFix`, `deadReckoningOnly` and `timeOnly` are not usable. Speed and heading are
   aligned to fix type by the latest fix-type sample at or before the speed sample, and only if
   that fix-type sample is not older than the sensor's `stale_after_ms`.
2. **Heading trust:** below `min_heading_speed_mps` (query parameter, default 1.0, documented as a
   processing default) the heading of motion is noise: hold the last trusted heading. Before the
   first trusted heading of a segment, the segment does not start (those samples are counted as
   `excluded.untrusted_heading`).
3. **Integration:** between two consecutive usable samples, distance = trapezoid of speed over
   `dt`; direction = the **circular** mean of the two headings (359° and 1° average to 0°, not
   180°); heading is clockwise from north, so `dx = d·sin(h)`, `dy = d·cos(h)`.
4. **Segments:** a new segment starts when `dt` between two usable samples exceeds the
   `stale_after_ms` of `gps_ground_speed` from defs, or when unusable samples interrupt the run.
   The new segment continues from the last point of the previous one (the movement during the gap
   is unknown, so nothing is invented for it) and records `gap_before_ms`. No line is ever drawn
   across a gap.
5. **Path length:** `path_length_m` = the sum of the integrated distances at full resolution
   (before simplification).
6. **Simplification to `max_points`** (10..20000, default 2000, the same range as `/series`):
   Ramer-Douglas-Peucker on (`x_m`, `y_m`) per segment, with the tolerance found by bisection so
   the total point count is ≤ `max_points`; the first and last point of every segment are always
   kept; deterministic (same input → same output). If the segments' endpoints alone exceed
   `max_points`, return 422 with a clear message instead of dropping segments.
7. **Counters:** `excluded` = `{no_fix, stale_fix, untrusted_heading}` sample counts, and
   `segments_total`.

Tests (`tests/test_gps_track.py`, synthetic series built in the test):
- straight line north at constant speed: `x_m` ≈ 0, `y_m` and `path_length_m` = v·t;
- a full circle at constant speed and yaw rate: path length = 2πr within 1 %, closure (distance
  from last point to first) small relative to r;
- heading wrap: a straight run due north with headings alternating 359.5° / 0.5° stays on the
  y axis and its length is v·t (a naive arithmetic mean gives 180° and runs it south);
- a gap longer than `stale_after_ms` splits into two segments with `gap_before_ms` set and the
  second starting at the first's last point;
- no-fix and stale-fix samples are excluded and counted; fix-type values come from the defs enum
  (a test that fails if a literal is used, e.g. by checking against `vehicle_defs` names);
- low-speed heading hold;
- simplification: `≤ max_points`, endpoints kept, a 90° corner survives, determinism, the 422
  case.

### TR-2 `GET /sessions/{id}/track` (`api.py`, README)

Auth exactly like `/series` (bearer token; 503 if unset). Query: `max_points`,
`min_heading_speed_mps` (0..10), `color` (optional, one series name with the `/series` prefixes),
`from_ms`/`to_ms` (inclusive window on the `/series` t0 axis, applied before integration).

Response:
```
{session_id, t0_device_ms, method: "dead_reckoning", frame: "relative_enu_from_first_fix",
 max_points, points_total, downsampled, path_length_m, segments_total,
 excluded: {no_fix, stale_fix, untrusted_heading},
 color: {name, unit} | null,
 segments: [{t_ms, x_m, y_m, speed_mps, heading_deg, color_v?, gap_before_ms}]}
```
- `t0_device_ms` is **the same t0 as `/series`** for that session (reuse its computation; a test
  checks a `/series` call and a `/track` call return the same value).
- `color_v`: the colour series sampled at each **kept** track point from its full-resolution
  points by the latest sample at or before the point time; `null` when that sample is older than
  the series' `stale_after_ms` (DIDs and sensors from defs; for `derived.*` use the defs derived
  table's staleness or, if it has none, the signal's `period_ms` × 3 and say which in the README).
  A position-looking `color` is refused through `position.is_position_name` with the same status
  and wording as `/stats`; an unknown name likewise.
- 404 unknown session; 404 with the detail `session has no GPS` when the session has no usable GPS
  series (the analyzer shows this state).
- README: a `/track` row in the endpoint table next to `/series` and `/stats`, the dead-reckoning
  caveat (error grows with distance; the shape is approximate; not a map), the processing
  defaults, and that it never contains an absolute position.

Tests (`tests/test_track_api.py`, synthetic fixture sessions only; extend `make_fixtures.py` /
`conftest.py` the way the `/series` tests do): auth required; unknown session 404; session
without GPS 404; same t0 as `/series`; `max_points` respected; `color=sensor.lean_angle`
returns its unit from defs and nulls after staleness; `color=` a position-looking name is
refused; `from_ms`/`to_ms` window.

### TR-3 Cross-check with the derived GPS distance

defs has `derived.ride_distance_gps` (class B, "distance of the ride from the integral of the GNSS
speed", in km, inputs `sensor.gps_ground_speed` + `sensor.gps_fix_type`). Find out whether the
server's derived reference implements it (`derived/summary.py`). If yes: a test on a synthetic
session that `/track`'s `path_length_m` / 1000 agrees with it within its `resolution` plus the
difference explained by rule 1 (state the expected difference in the test). If not implemented:
do **not** implement it here (that is a D-070 part, yellow/red review); write in *For Claude* what
you found and test `path_length_m` against an independent trapezoid of the usable speed samples
instead.

Checks for Part A (all must pass before each push): `cd vehicle-server && uv run pytest -q`,
`uv run ruff check .`, `uv run ruff format --check .`.

## Part B — vehicle-analyzer

The analyzer talks to the server through the existing session settings (base URL + token).
Develop against a mocked server response; the contract is the TR-2 response above. If Part A is
not finished, keep going with the mock.

### TR-4 Track client and geometry (`src/services/trackClient.ts`, `src/services/trackGeometry.ts`)

- `trackClient.ts`: `buildRequest` reuse; `parseTrackResponse(json)` validates strictly (equal
  list lengths per segment, finite numbers except `color_v` nulls, `method`/`frame` values known)
  and throws a readable error otherwise; `describeHttpError` reuse, with the 404 `session has no
  GPS` mapped to a "no GPS in this session" state, not an error.
- `trackGeometry.ts`, pure and unit-tested:
  - `fitView(bounds, width, height, padding)`: aspect-preserving (1 m east = 1 m north on screen),
    y axis flipped (north up), centred;
  - zoom about a screen point and pan, as pure transforms (zoom keeps the point under the cursor
    fixed); clamp zoom to a sane range;
  - `nearestByTime(segments, t_ms)` (binary search, returns segment + index, or none in a gap) and
    `nearestByScreen(segments, view, px, py, maxPx)`;
  - `colorScale(values)`: sequential scale over the finite `color_v` range (or `speed_mps` when no
    colour series), N bins (default 16); nulls map to a neutral "no data" colour; a constant
    series does not divide by zero;
  - `scaleBar(view)`: a round length (1/2/5 × 10^k m) between ~60 and ~150 px.

Tests: `tests/trackGeometry.test.ts`, `tests/trackClient.test.ts` (aspect ratio, north up, zoom
fixed point, nearest across a gap, bins, constant series, scale bar values, malformed responses).

### TR-5 Track view (`src/components/TrackPanel.tsx`, key `G`)

A new view like the others (key bar entry `G` "Ride track", help text, layout persistence as the
other views do):
- uses the recorded session the user selected/opened in the Recorded sessions view (`E`); with
  none selected it says so;
- states: no server configured, no session, loading, no GPS in this session, error, loaded;
- draws on one `<canvas>`: the segments (one `Path2D` per colour bin, not one stroke per point),
  no line across a gap, start and end markers, a north arrow, the scale bar, a colour legend with
  the colour series' name and unit from the response;
- colour selector: speed (default) or any series name the session offers (reuse the names the
  Recorded sessions view already lists; never a hard-coded list); changing it refetches with
  `color=`;
- mouse wheel zoom about the cursor, drag to pan, a "fit" button;
- **cursor sync with replay:** while a recorded session is replayed (A3 Open), a marker follows the
  replay time (`nearestByTime`); clicking on the track seeks the replay to the nearest point's
  time. If the replay transport has no seek, add a minimal one without changing its playback
  semantics, and say so in the log;
- a visible caption: "Dead-reckoned from GNSS speed and heading. Approximate shape, not a map."
- handles device pixel ratio and resize; redraws only on change (no animation loop when idle).

Tests: component tests in `tests/components/` for the states and the legend/caption; the drawing
logic stays in pure functions so it is testable without a real canvas.

### TR-6 No third-party requests + UI smoke (`ui-tests/`)

In Playwright: route the vehicle-server URL to a fixture `/track` (and whatever `/sessions` calls
the view needs), open view `G`, load the track, zoom and change colour; record **every** request
the page makes and assert each one goes to the app's own origin or the configured server origin
(fail on anything else). Add the `G` view to the existing views smoke test.

### TR-7 Compare overlay (stretch: only if TR-4..TR-6 are done and green)

In the Compare view (`A`), an optional "tracks" toggle that draws both sessions' tracks in one
canvas with two colours (no colour series), each starting at its own origin. Reuse
`trackGeometry`; one test.

### TR-8 Docs

- `docs/ROADMAP.md`: split A7 into **A7a** (this run: relative dead-reckoned track, done) and
  **A7b** (absolute position + self-hosted tiles, blocked by D-076 item 3 / defs).
- `README.md`: the Track view, key `G`, what it shows and what it does not (no map, no position).

Checks for Part B (all must pass before each push): `cd vehicle-analyzer && npm ci`,
`npm run build`, `npm test`, `npm run test:ui` (after `npx playwright install chromium` once).

## Finish

- Open the vehicle-server PR (`needs-claude-review`, yellow `gps_track.py`) and the
  vehicle-analyzer PR (body: task list, checks), then the workspace PR for the log. Fill the log:
  Result table, Checks, Unsure about, For Claude.
- Do not merge anything. Do not edit `STATUS.md`, `ISSUES.md`, `DECISIONS.md`, any `CLAUDE.md`
  (if the server or analyzer CLAUDE.md should mention `/track` or the `G` view, write the wording
  into *For Claude*).
- Put into *For Claude*: every place where the rules above were ambiguous and the choice you made,
  the TR-3 finding, whether you had to add a replay seek, and any dependency you wanted (with
  licence).
