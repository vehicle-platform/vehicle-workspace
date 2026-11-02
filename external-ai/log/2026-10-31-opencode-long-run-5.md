---
date: 2026-10-31
tool: opencode/deepseek-v4.1-flash-free
topic: long-run-5-relative-track
repos: [vehicle-server, vehicle-analyzer, vehicle-workspace]
branches: [vehicle-server:ext/opencode-server-track, vehicle-analyzer:ext/opencode-analyzer-track, vehicle-workspace:ext/opencode-long-run-5-log]
prs: [vehicle-server#42, vehicle-analyzer#37, vehicle-workspace#136; review: vehicle-server#43, vehicle-analyzer#38]
zone: yellow
review: done 2026-11-02 (no zone breach, no blocker; TR-1..TR-8 conform; Claude fixed RDP cost (60+ full RDP passes -> one significance pass, exact), a candidate-DID colour KeyError (500), per-keystroke refetches, a Compare stale-response race and aspect, lost zoom on refetch/resize, seek into another session's replay, passive wheel, CI-flaky seek test; server#43 supersedes #42, analyzer#38 supersedes #37, both merged, server CLAUDE.md #44; follow-ups ISSUES E-26)
---

# DeepSeek long run 5 — relative ride track

## Goal
Add a relative dead-reckoned GNSS track to the server (`GET /sessions/{id}/track`) and a
Track view (key `G`) to the analyzer, without storing or exposing absolute position.

## Changes
- `vehicle-server/src/vehicle_server/gps_track.py`: pure module. `build_track` at line 327
  filters fix types by defs enum name (`fix2d`, `fix3d`, `gnssDeadReckoning`), aligns speed and
  heading to the latest fix-type sample, holds the last trusted heading below
  `min_heading_speed_mps`, integrates the speed trapezoid with a circular heading mean, splits
  at stale gaps/excluded samples, keeps `gap_before_ms`, and RDP-simplifies per segment with a
  bisection tolerance. `sample_series` (line 369) gives colour samples with the defs staleness.
- `vehicle-server/src/vehicle_server/api.py`: `GET /sessions/{id}/track` at line 152. Query
  `max_points` (10..20000), `min_heading_speed_mps` (0..10), optional `color`, `from_ms`,
  `to_ms`; response is relative ENU from the first usable fix and never contains position.
  `TrackTooManyPoints` maps to 422; unknown session/no GPS/unknown or position-looking colour
  map to 404.
- `vehicle-server/README.md`: `/track` row with the contract, the colour staleness rule and the
  privacy caveat.
- `vehicle-server/tests/test_gps_track.py`: 20 pure cases (straight, circle, heading wrap, gaps,
  no-fix/stale fix, defs enum lookup by name with shifted values, low-speed heading hold, no
  segment before a trusted heading, heading trust restarting after a gap, RDP bounds, too many
  segments, colour staleness, single sample, all no-fix, non-finite input, short session,
  non-finite `min_heading_speed_mps`).
- `vehicle-server/tests/test_track_api.py`: 16 API cases (auth, unknown/malformed session, no
  GPS, t0 equality with `/series`, max_points, defs colour unit and staleness, position/unknown
  colour refusal, window before integration, 422 bounds, single sample, all no-fix, empty and
  inverted windows, max_points upper bound).
- `vehicle-server/tests/test_track_crosscheck.py`: 2 cases comparing `path_length_m` with
  `derived.ride_distance_gps` on the stored `v4_gps_session` and at constant speed.
- `vehicle-analyzer/src/services/trackGeometry.ts`: pure geometry — `fitView` (line 94, north
  up, aspect preserved, zero-size guard), `worldToScreen`/`screenToWorld`, `zoomAt` (line 122),
  `panView`, `nearestByTime` (line 134), `nearestByScreen` (line 173), `colorScale` (line 228,
  finite bins, neutral nulls, constant series), `scaleBar` (line 271) and `formatDistance`.
- `vehicle-analyzer/src/services/trackClient.ts`: strict `parseTrackResponse` (line 75),
  `trackRequest` (line 65, token only in `Authorization`), `TrackClient` (line 174), and
  `NoGpsInSessionError` (line 51) for the 404 `session has no GPS` state.
- `vehicle-analyzer/src/components/TrackPanel.tsx`: Track view at line 178. One canvas with
  one `Path2D` per colour bin, gap-aware segments, start/end markers, north arrow, scale bar,
  legend, speed or any offered session series as colour, replay cursor, click-to-seek, wheel
  zoom, drag pan and Fit. Caption: "Dead-reckoned from GNSS speed and heading. Approximate
  shape, not a map."
- `vehicle-analyzer/src/App.tsx` (line 477): lifts `recordedSessionId` and adds `seekToTime`;
  `src/components/Header.tsx` (line 47): `Ride track` tab with key `G`; `src/ui/keys.ts`:
  global `G`; `src/types/can.ts`: the `track` view id.
- `vehicle-analyzer/src/components/ComparePanel.tsx` (line 77): stretch TR-7 `Tracks` toggle
  draws both relative tracks on one canvas with two colours, each from its own origin.
- `vehicle-analyzer/tests/trackGeometry.test.ts` (12), `tests/trackClient.test.ts` (10),
  `tests/components/TrackPanel.test.tsx` (7), `tests/components/ComparePanel.test.tsx` (2).
- `vehicle-analyzer/ui-tests/track.spec.ts`: records every request, loads the track, zooms,
  changes colour and asserts only the app and configured server origins; `ui-tests/views.spec.ts`
  includes the G view smoke case.
- `vehicle-analyzer/README.md`, `docs/ROADMAP.md`: Track view (G) and A7a done / A7b blocked.

## Result
| Task | Code | Tests | Status |
|---|---|---|---|
| TR-1 | `vehicle-server/src/vehicle_server/gps_track.py:335` (`build_track`), `:140` (`_usable_samples`), `:239` (`_build_segments_with_positions`), `:290` (`simplify_segments`) | `tests/test_gps_track.py` (20) | done |
| TR-2 | `vehicle-server/src/vehicle_server/api.py:152` (`get_session_track`), `vehicle-server/README.md` | `tests/test_track_api.py` (16) | done |
| TR-3 | `vehicle-server/tests/test_track_crosscheck.py:36` and `:53` | 2 cases | done |
| TR-4 | `vehicle-analyzer/src/services/trackGeometry.ts:94`, `trackClient.ts:65`/`:179` | `tests/trackGeometry.test.ts` (12), `tests/trackClient.test.ts` (10) | done |
| TR-5 | `vehicle-analyzer/src/components/TrackPanel.tsx:178`, `src/App.tsx:477`, `src/components/Header.tsx:47` | `tests/components/TrackPanel.test.tsx` (7), `ui-tests/views.spec.ts` | done |
| TR-6 | `vehicle-analyzer/ui-tests/track.spec.ts` | Playwright request-origin test | done |
| TR-7 | `vehicle-analyzer/src/components/ComparePanel.tsx:77` | `tests/components/ComparePanel.test.tsx:48` | done (stretch) |
| TR-8 | `vehicle-analyzer/README.md`, `docs/ROADMAP.md` | docs only | done |

Commits: server `18d2107`, `8ac9b60`, `60d5935`, `ae30cb5`, `9f60fff`; analyzer `fc1dacd`,
`654d9dc`, `bbb339e`, `c7f03fd`, `4b192ec`, `a5bbc0b`, `83dc737`; log branch starts at
`c519d60`.

### TR-3 finding
`derived.ride_distance_gps` is implemented, but its `_integral` only integrates the speed
series; the declared `gps_fix_type` input is not read by the summary. On `v4_gps_session` the
derived value is `0.0055783 km` and the track is `0.00559665 km`; the difference is
`0.00001835 km` (0.01835 m), the expected trapezoid endpoint correction, inside the defs
`0.01 km` resolution. The cross-check test records this rather than hiding it.

## Checks
- `cd vehicle-server && uv run ruff check .`: pass.
- `cd vehicle-server && uv run ruff format --check .`: pass (71 files already formatted).
- `cd vehicle-server && uv run pytest -q`: `406 passed, 1 warning in 13.63s`.
- `python3 scripts/check_zones.py vehicle-server --base origin/main`: YELLOW for
  `src/vehicle_server/gps_track.py` and `tests/test_gps_track.py`; the other changed files GREEN.
- `cd vehicle-analyzer && npm test`: `203 passed` (30 files).
- `cd vehicle-analyzer && npm run build`: pass (`tsc -b && vite build`; only the existing
  chunk-size warning).
- `cd vehicle-analyzer && npm run test:ui`: `14 passed` (Playwright Chromium).
- `python3 scripts/check_zones.py vehicle-analyzer --base origin/main`: GREEN for every changed
  analyzer path.
- `python3 scripts/check_zones.py . --base origin/main --path external-ai/log/2026-10-31-opencode-long-run-5.md`:
  GREEN. The untracked task file is reported RED by the whole-repo check and is not committed.

## Unsure about
- The `/track` window currently windows only `sensor.gps_ground_speed`; heading and fix type
  stay full-resolution so alignment still works at the window edges. This matches the TR-1
  alignment rule but is worth a hidden-test check.
- `points_total` counts full-resolution usable samples, including the synthetic start point
  that continues at the previous position after a gap. `segments_total` and `gap_before_ms`
  describe the same split.
- A session with no usable samples returns 404 `session has no GPS` only when no window was
  requested; with `from_ms`/`to_ms` it returns 200 with empty `segments`, zero length and zero
  counters. An inverted window (`from_ms > to_ms`) also returns that empty 200 rather than 422.
  I chose consistency with `/series` windowing; hidden tests may prefer a 422.
- `sensor.lean_angle` is deliberately not stored by real sessions, although defs has it. The
  API colour test monkeypatches `series.load_all`; a real `color=sensor.lean_angle` request
  returns 404. The test now takes the unit from `vehicle_derived.SENSORS`.
- Heading trust is reset at a segment boundary (gap or excluded sample): a new segment must
  start with a trustworthy heading rather than holding the previous segment's heading. This
  follows the "first trusted heading of a segment" wording, but it is a behavioural choice
  worth confirming.
- A colour series may have a `null` unit; `TrackClient` now accepts it and the legend shows
  `-` instead of inventing `m/s`. The server currently returns strings for the defs units.
- `G` was already used by local shortcuts: Sessions/Compare refresh used `g` and Sync used
  `g`. I rebound them to `r` (Refresh, buttons show `R`) and `i` (log, button shows `I`) so
  global `G` is unambiguous. This changes existing muscle memory and should be reviewed.
- TR-7's canvas is a fixed `900x220` bitmap scaled by CSS; it has no DPR/resize handling like
  the main TrackPanel because it is a stretch comparison view. If a track has no GPS, the
  overlay shows "Track overlay unavailable" and leaves the compare plots intact.
- The analyzer still lists colour choices from `GET /series?maxPoints=10` and filters
  position-looking names; it does not hard-code a series list.
- No new dependency was added. The Playwright test needs the already-configured Chromium.
- I added a minimal replay seek (`seekToTime`) because clicking the track needs it; it maps
  milliseconds to the nearest replay frame.

## For Claude
- Review the yellow `vehicle-server/src/vehicle_server/gps_track.py` and
  `vehicle-server/tests/test_gps_track.py` (position-adjacent code, D-076 provisional). The
  server PR is marked `needs-claude-review`.
- Decide whether `ride_distance_gps` should read its declared `gps_fix_type` input; the TR-3
  finding shows the current summary ignores it. If that is a bug, it is a server/derived change
  outside this task's scope.
- Confirm the empty/inverted window behaviour (200 empty vs 422) and the `points_total`
  gap-start semantics against the platform contract.
- If the server or analyzer `CLAUDE.md` should mention `/track` or the `G` view, that wording
  belongs in Claude's red-zone edit; I did not touch those files.
- Review the local shortcut rebinds (`g` -> `r`/`i`) and the `Compare` Tracks toggle for UI
  consistency.
- Confirm that resetting the held heading at every segment boundary is what the safety/telemetry
  contract wants; if the heading should be held across a gap, revert
  `_usable_samples` to a run-global `last_heading`.
- Consider whether `sensor.lean_angle` should be stored for colouring; currently real sessions
  cannot offer it and the test injects it.

## Claude review
Reviewed 2026-11-02 by Claude (architecture-guard + a sonnet correctness review of the analyzer + Claude on the yellow `gps_track.py`). Zones: no red path; `gps_track.py` and its test yellow, the rest green. No BLOCKER: no absolute position anywhere, `position.py` reused, fix types by defs enum name, staleness from defs, synthetic data only, no new dependency, no third-party request (the Playwright origin test does fail on one).

Fixed by Claude (DeepSeek's commits kept, Claude's on top):
- MAJOR server: the `max_points` search reran RDP over every point at each of 60+ bisection steps (2.65 s for one hour at 10 Hz). Now one RDP pass gives each point its significance (smallest squared distance on its split chain); keeping the points above the (max_points + 1)-th value is exactly RDP at that tolerance (test against a textbook RDP at five tolerances); 0.14 s, with a timing test.
- MAJOR server: `color=did.<candidate>` raised KeyError (HTTP 500): candidate catalog DIDs have no poll-plan `stale_after_ms`; now held, documented.
- MAJOR analyzer: every URL/token keystroke fetched `/series` + `/track` (partial URLs, view wiped); now on session/colour change and Refresh only, in Track and Compare.
- MAJOR analyzer: Compare overlay had no stale-response guard and a fixed 900x220 bitmap stretched by CSS (aspect broken); now guarded, CSS size x DPR, drawn through the shared `src/ui/trackDraw.ts`.
- MAJOR analyzer: zoom/pan was lost on a colour refetch and on resize; now kept (`resizeView`), refit only on a new session or Fit.
- MINOR analyzer: click-to-seek used whatever replay was loaded (another session or an .asc/.csv log); now only when the replay is the same recorded session, with a hint otherwise. Native non-passive wheel listener, pan with the primary button only, redraw on DPR change, `fitView` padding clamp, `isRecord`/`FetchLike`/`getJson` reused from `sessionClient.ts`. A seek test clicked before the view was fitted and failed on CI; it now retries.

Answers to *For Claude*: empty/inverted window 200 with no segments is accepted (same as `/series` windowing); `points_total` semantics accepted; the heading-trust reset at a segment boundary is right (a held heading must not cross unknown movement); the `g` -> `r`/`i` rebinds are accepted. `ride_distance_gps` ignoring its `gps_fix_type` input, `lean_angle` not stored in phase-0 sessions and A7b are ISSUES E-26. CLAUDE.md: server `/track` line added by Claude (vehicle-server#44); the analyzer CLAUDE.md lists no views, so nothing was added there.
