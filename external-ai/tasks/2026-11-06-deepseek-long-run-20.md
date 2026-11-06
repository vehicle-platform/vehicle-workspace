# DeepSeek long run 20 — 2026-11-06 (finish long run 19 + two small follow-ups)

Written by Claude for opencode/DeepSeek. Run the tasks in order without asking between them.
Commit after every task (Conventional Commits, `AI-Agent: opencode/<model>` trailer) and push
after every commit. If a task is blocked, write why in the log's *For Claude* section and go on to
the next one. **Never merge a PR.**

| Task | Repo | Branch | Zone |
|---|---|---|---|
| LR20-0 (first!) and LR20-6 | vehicle-workspace `external-ai/log/` | `ext/opencode-long-run-20-log` (from `main`) | green |
| LR20-1 | vehicle-server | `ext/opencode-server-demo-session` (**exists locally**, see LR20-1) | green (yellow: any path with `gps`, `position`, `mdf4`, `pyproject.toml`, `uv.lock`; red: `*ota*`, `.github/*`, `external/*`, `CLAUDE.md`, `AGENTS.md`) |
| LR20-2 ... LR20-3 | vehicle-server | `ext/opencode-server-demo-session` | same |
| LR20-4 | vehicle-server | `ext/opencode-server-summary-window` (from `main`) | green (same yellow/red list) |
| LR20-5 | vehicle-server | `ext/opencode-server-window-engine-zero` (from `main`) | green; `src/vehicle_server/derived/*` is **red for this run** (rule 1) |

## 0. Before you start (read, do not skip)

### Why this run

Long run 19 stopped in LR19-4: the synthetic demo session script
`vehicle-server/scripts/make_demo_session.py` (274 lines) sits **untracked and untested** in the
server main clone on branch `ext/opencode-server-demo-session`. Claude reviewed and merged
LR19-1..3 (server#58, mobile#32). This run (a) finishes LR19-4/5 so the user can check every card
(analyzer E, Health windows, phone) on the desk before G1, (b) adds the `window` key to each
`/summary` entry so the phone (mobile#32 already reads an optional `window` field) can show the
window signal rows, and (c) covers the one close reason the property tests never reach
(`engine_zero`).

No decision is needed from the user. If something here contradicts a decision (D-033, D-069,
D-075, D-076, D-079, D-089) or a repo `CLAUDE.md`, the decision text wins: write the conflict into
*For Claude* and skip that part.

### Visibility and git (unchanged from long run 18 §0)

- Work in the main clones `vehicle-server/` and the workspace root (not under
  `.claude/worktrees/`, that is Claude's area).
- After creating each branch, and again at the end, run from the workspace root:
  `python3 scripts/vscode_workspace.py`.
- Commit with the normal git config; do not set `user.name`/`user.email` yourself.
- Before every push: `python3 scripts/check_zones.py vehicle-server --base origin/main` (from the
  workspace root). Red → do not push, revert that path, write it into *For Claude*.

### Read

- `AGENTS.md` at the workspace root (zones, branches, trailer, log format, the check table §4).
- `vehicle-server/CLAUDE.md` (read only, red) and the README sections "D-079 health windows
  (provisional)" and "Derived signals".
- `external-ai/tasks/2026-11-06-deepseek-long-run-19.md` sections LR19-4 and LR19-5: **their
  requirements still hold**, this file only adds to them.
- `external-ai/log/2026-11-06-opencode-long-run-19.md` *Claude review* (what was fixed and why).

### Hard rules for this run

1. **No window or derived rule changes.** Everything under `src/vehicle_server/derived/` stays
   byte-identical (`health_windows.py`, `health_window_summaries.py`, `summary.py`, formulas). If
   the demo series does not open a window, change the **series**, never the rule. A property that
   fails is recorded with its seed (`xfail(strict=True)` + *For Claude*), never "fixed".
2. **Golden vectors unchanged:** `uv run pytest tests/test_golden.py tests/test_golden_b.py`
   passes on every branch; `tests/golden/MANIFEST.sha256` untouched.
3. **Never real data, never a position (D-033, D-076).** Everything generated is synthetic and
   named so (`synthetic-demo-...`). No GPS block, no latitude / longitude / altitude anywhere.
4. **No new dependency** (`pyproject.toml`, `uv.lock` unchanged). stdlib `random` with a fixed
   seed, no `hypothesis`, no `numpy` in the script unless the server already imports it.
5. **Signals, DIDs, scales, window keys and conditions come from `vehicle_server.defs`**
   (`vehicle_derived`, `vehicle_catalog`, `vehicle_cl250` constants), never hand-written literals.
   Thresholds the demo series must cross are read from the spec at run time (e.g. "warm" = the W3
   condition's threshold + a margin), so the script survives a D-103 value change.
6. **No new route, no new CLI subcommand.** LR20-4 adds one optional key to existing `/summary`
   entries; nothing else in the API changes.
7. Never touch `vehicle-mobile` in this run (the phone already reads `window`; Claude checks it).

## LR20-0 — Log first

Copy `external-ai/log/TEMPLATE.md` to `external-ai/log/2026-11-06-opencode-long-run-20.md` on
`ext/opencode-long-run-20-log` (cut from workspace `main` after `git pull`), `review: pending`,
header + task list, commit and push before any code. Update it after every later task.

## LR20-1 — Server: rescue the long run 19 work in progress

The server main clone is on `ext/opencode-server-demo-session` (cut from an old `main`, 418b660)
with the untracked `scripts/make_demo_session.py`.

1. `git -C vehicle-server status` — confirm it is exactly that one untracked file (if anything else
   is dirty, stop and write it into *For Claude*; do not discard anything).
2. Commit it as is: `wip(scripts): add the long run 19 demo session generator (untested)` with the
   trailer, so it can never be lost again.
3. `git fetch origin && git rebase origin/main` (main gained server#57 + #58: the
   `health_windows` report block and the property tests). Resolve nothing by deleting the
   script. `git submodule update --init`, `uv sync`.
4. Push the branch (`git push -u origin ext/opencode-server-demo-session`, force-with-lease only if
   it was pushed before the rebase).

## LR20-2 — Server: finish the demo session generator (= LR19-4)

Review the script against LR19-4 item 1 and rule 5 before adding to it; rewrite parts that
hand-write DIDs, scales, offsets or thresholds. Then make it complete:

1. `--out <dir> [--zip] [--date YYYY-MM-DD]`. **The default date is fixed (`2026-01-01`), never
   `today()`**, so two runs are byte-identical; the session name is `synthetic-demo-<YYYYMMDD>`
   from that date. Every timestamp derives from it.
2. About 20 minutes, in this order, each phase long enough for its window per the defs conditions
   / stable bands / minimum durations (read them from `vehicle_derived.WINDOWS`):
   key-on rest (W1) → crank and cold start (W2) → warm-up → warm idle that qualifies (W3) → a short
   warm idle that does **not** qualify → cruise in at least three gears (W4, `per_gear`) → decel to
   a stop (W5, first D-075 stop epoch) → ride again → second stop → **an engine stop (engine speed
   0) while a W3 warm idle is open**, so one instance closes with `engine_zero` → session end.
3. One input gap longer than that input's `stale_after_ms` inside an open window (the instance
   must close as `unknown` at the stale instant, the D-079 rule the README describes).
4. Every value inside the DBC / DID ranges; `synthetic: true` in the session metadata wherever the
   meta format allows it.
5. No generated output committed; if the script has a default output folder, `.gitignore` it.
6. Module docstring: what each phase is for (which window / summary it exercises).

## LR20-3 — Server: test, README, PR (= LR19-5, extended)

1. `tests/test_demo_session.py`: generate into `tmp_path`, import it through the same function the
   `vehicle-server import` CLI uses, then assert:
   - no `derived.error` / `derived_summary.error` in the report;
   - every window W1-W5 has at least one non-null `window_*` scalar in `derived_summary`, except
     signals that are `not_implemented` (the two W4 residuals) — read the status, do not list names;
   - the `health_windows` block (server#57) has, for every window key in `vehicle_derived.WINDOWS`,
     at least one instance and at least one qualifying instance;
   - across all instances the close reasons include `engine_zero` and `unknown`;
   - the `per_gear` summary has at least three gear rows; at least two stop epochs;
   - no GPS / position column or file anywhere in the stored session (reuse
     `vehicle_server.position` for the name check, do not write a second rule);
   - determinism: two generations (folder and `--zip`) are byte-identical to themselves.
   If a window does not qualify although the series was meant to open it, adjust the series; if you
   cannot, `xfail(strict=True)` + *For Claude* with the reason.
2. README: a short "Synthetic demo session" paragraph: the command, `vehicle-server import`, then
   view it in vehicle-analyzer E (summary, Health windows card) and on the phone (Server rides);
   "synthetic, never a real ride".
3. `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, the golden tests
   (rule 2), the zone check. Squash nothing (Claude reviews the commits). Open **one** PR to
   `main`; do not merge.

## LR20-4 — Server: `window` key in `/summary` entries

New branch from an up-to-date `main` (stash nothing: the demo branch is pushed).

1. In `src/vehicle_server/ride_summary.py`, every `/summary` signal entry whose defs spec
   (`vehicle_derived.SIGNALS[name]`) has a `window` gets `"window": <that key>` (a string such as
   `W1_KEY_ON`), **for every status** (computed and not computed), so a client can group rows by
   window. Entries without a `window` in defs get no key (not `null`). Read the key from defs, no
   literal. Additive only: no other field changes, order unchanged.
2. Tests (extend the existing `/summary` tests, API and function level): a computed window scalar
   carries its key; a `not_implemented` window signal carries it too; a non-window signal has no
   `window` key; every `window` value in a full response is a key of `vehicle_derived.WINDOWS`.
3. README / API section: one sentence on the new optional key. `/rides` unchanged.
4. Checks as in LR20-3 item 3. Open **one** PR to `main`; do not merge. PR body: "mobile#32 already
   reads this optional field; no phone change needed".

## LR20-5 — Server: property tests reach `engine_zero`

New branch from an up-to-date `main`. Rule 1: `src/vehicle_server/derived/` is red for this run.

1. In `tests/test_health_windows_properties.py` (server#58), extend the seeded generator so that,
   for windows whose spec lets the trigger input end an open instance, some seeds drop the D-069
   engine-speed trigger input to exactly `0` while an instance is open. Use the production trigger
   source the file already uses (`summary._window_trigger`), not a literal DID.
2. New assertions: an instance closed by `engine_zero` ends at the first sample where the trigger
   is 0 (not later); no instance opens while the trigger is 0 unless the window's own opener allows
   it (read the spec; if unsure, assert nothing and say so in *Unsure about*); across the 200 seeds
   every close reason in `health_windows.py` that the spec makes reachable for that window occurs
   at least once (a coverage assertion, per window).
3. A failure is a finding, not a fix: `xfail(strict=True)` with the seed + *For Claude*.
4. Runtime stays under ~15 s for the file (`pytest --durations=5` in the log). Checks as in
   LR20-3 item 3. Open **one** PR to `main`; do not merge.

## LR20-6 — Close the log

Finish the log: every task, commit, check result (test counts, durations), the zone results, the
three PR links (demo session, summary window, engine_zero properties), every xfail with its seed,
every doubt (*Unsure about*) and every request (*For Claude*). Keep `review: pending`. Run
`python3 scripts/vscode_workspace.py` one last time. Push the branch; no PR needed.
