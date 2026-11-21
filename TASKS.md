# TASKS — self-contained task cards for a Claude session

> Written 2026-11-12. One card = one session (`one session = one task`, CLAUDE.md). Each card carries its own preconditions, scope, output and verification, so a session can start from `STATUS.md` + this card alone. Status column: **ready** (nothing blocks it), **blocked: tags** (needs item T0), **blocked: user**, **blocked: hardware**. When a card is done, mark it and move the facts into `STATUS.md` via `/handoff`. Big work that is explicitly on hold stays listed so it is not forgotten.

## T0 — Release tags (done 2026-11-15)

Done 2026-11-15 by Claude on the user's order (plus defs v0.29.0). The version PRs were merged (analyzer#51, conn#47, mobile#34; defs#146-#155). Run:

```bash
gh release create v0.28.0 -R vehicle-platform/vehicle-defs --target main --title v0.28.0 --generate-notes
gh release create v0.3.0  -R vehicle-platform/vehicle-analyzer --target main --title v0.3.0 --generate-notes
gh release create v0.5.0  -R vehicle-platform/vehicle-connectivity-node --target main --title v0.5.0 --generate-notes
gh release create v0.5.0  -R vehicle-platform/vehicle-mobile --target main --title v0.5.0 --generate-notes
```

Then say "tags ready" and start T1.

## Cards

| # | Task | Status | Repo(s) |
|---|---|---|---|
| T1 | Repin defs **v0.29.0** everywhere + `manifest.yaml` | **done 2026-11-19** (server#75, ml#23, linux-node#19, analyzer#66, mobile#39, conn#52, rt-core#78, safety-node#19 with safety-reviewer APPROVE; workspace#224) | — |
| T2 | Server branch chain d106 → dq-mask → coast-down → nrc78 → faults-api | **done 2026-11-19** (server#76–#80; mcp `list_fault_catalog` verified against a local server) | vehicle-server |
| T3 | rt-core dq-mask merge-up + W4 residuals + golden resync | **done 2026-11-20** (rt-core#79, #80; golden 0 mismatches; M7 +1.8 KB flash, +2.9 KB RAM) | vehicle-rt-core |
| T4 | linux-node reads `Baudrate` from `platform.dbc` | **done 2026-11-19** (linux-node#20, `--platform-bitrate` removed) | vehicle-linux-node |
| T5 | Hardware Integration Atlas follow-ups: KiCad S1–S5 sheets from the figures (D-117, `models/kicad-lib/SCHEMATIC-README.md`) | S-sheets: user in KiCad; first open of the generated libraries is the format check | workspace `models/kicad-lib` |
| T6 | Pin plans → decision: Claude pre-checks the H743 and G474 plans against the CubeMX `.ioc` the user exports for **each** board (NUCLEO-H743ZI2, NUCLEO-G474RE); writes the D-xxx draft | blocked: user (boards + CubeMX exports); plans themselves: T21 | vehicle-defs |
| T7 | Q-016 node-health (D-108) | **done 2026-11-19**: rt-core/safety-node regen with T1; linux-node#21 `vehicle-linux-node-nodehealth` panel. Open: Pi/databroker run confirms a fresh timestamp per 100 ms heartbeat | rt-core, safety-node, linux-node |
| T8 | L3 live source Kuksa → vehicle-server over MQTT (D-109 provisional) | merged (server#70, linux-node#16); real-broker smoke test open (ISSUES E-31 (6)) | vehicle-linux-node, vehicle-server |
| T9 | Fault catalog quality pass | J2012 part **done 2026-11-19** (defs#176: 12 leads confirmed, cited by section, confidence stays low). Honda numbers still need the CL250 service manual (user) | vehicle-defs `faults/` |
| T10 | Analyzer A6 first run on a real SLCAN adapter; A7b real live source under D-077 | blocked: hardware | vehicle-analyzer |
| T11 | hil-bench host (Q-009 schema) + the D-020 forbidden-request silence scenario (ISSUES C-9 (3)) | blocked: user (Q-009) | vehicle-hil-bench |
| T12 | safety-node: own-IMU estimator (Q-022/Q-023 (5)-(6)) once the C1-IMU hardware exists; D-100 Layer 1 v2 | blocked: hardware | vehicle-safety-node |
| T13 | rt-core on the H743 (D-118): CubeMX red-zone image, FDCAN port, Renode, on-target budgets, Q-036 burst ADC; Q-038 backoff cap first | blocked: hardware (board on the desk) + T6 | vehicle-rt-core |
| T14 | D-083 ML stage 3 with real ride data | blocked: hardware (G1 capture) | vehicle-ml |
| T15 | Analyzer tests in CI | **done** (analyzer `ci(test)` T15 + ui-tests) | vehicle-analyzer |
| T16 | Q-001 listen-only capture → `/signal-change` promotion of the verified DIDs, Q-031 | blocked: hardware (G1) | conn, vehicle-defs |
| T17 | D-111 indicator input layer (merged safety-node#15) → blind-spot consumer once the radar exists, with the README consumer requirements and safety-reviewer | consumer blocked: hardware (radar) | vehicle-safety-node |
| T18 | ~~Mailbox lockstep check~~ | moot: mailbox retired by D-118 | — |
| T19 | conn parity with D-116 | **done 2026-11-19** (conn#53, quiet-window part). Open: D-116 item 2 (a non-0x62 FF ends a pending read without DID consequence) | vehicle-connectivity-node |
| T20 | defs v0.30.0: mailbox removal, SAFETY_HEARTBEAT_LOST U0167-00 (diagnostic only, NO_NEW_DATA), E-5/E-6/E-7, HARA/requirements under D-118 | defs part **done 2026-11-20** (defs#178, safety-reviewer APPROVE after 2 rounds). **blocked: tag v0.30.0 (user)** → consumers: rt-core uses `PLATFORM_UDS_DTC_*_DIAGNOSTIC_ONLY` instead of the `diag.c` index list, adds the 0x082 monitor, `pack_checked`/`encode_checked` for 0x020; safety-node/conn/hil-bench handle `WRONG_LENGTH`; safety-reviewer | rt-core, safety-node, conn |
| T21 | Hardware docs for D-118 | **done 2026-11-19** (defs#175, #177; workspace#225 KiCad modules). Every VERIFY line (header positions, solder bridges, DMA, G474 BOOT0 option bytes, G431 fallback, G474 morpho table) goes to T6 | vehicle-defs, workspace |
| T22 | One position rule (D-076) | defs part **done 2026-11-20** (defs#179, `vehicle_defs.position` + `privacy/position_vectors.json`, in v0.30.0). **blocked: tag v0.30.0** → server, ml, linux-node import it; mcp vendors it (CHANGELOG 0.30.0) | defs, server, mcp, ml, linux-node |
| T23 | conn: split `HondaCANModule.cpp` | **done 2026-11-19** (conn#54, pure moves verified by line multiset; SF check deduped; 296/296 native tests) | vehicle-connectivity-node |
| T24 | CI supply chain: gitleaks step in every repo, third-party actions pinned to SHAs via a synced workflow template, `persist-credentials: false`; turn on "Require review from Code Owners" for defs (CODEOWNERS added, defs#174)  (scope widened by QUALITY CI-1..5, DEFS-2, X-2, X-3, ARCH-4: Renovate, rulesets, OSV/Scorecard, Brewfile)| ready (template), user (branch protection) | all repos |
| T25 | Quality research pass for every deduction in `QUALITY.md` | done 2026-11-17 (R1–R4 folded into QUALITY.md, cards T26–T35) | vehicle-workspace |
| T26 | On-target verification layer (IWDG/WWDG, MPU, stack HWM, DWT WCET) on H743 + G474, QUALITY FW-1 | blocked: hardware | rt-core, safety-node |
| T27 | rt-core module split + lizard ratchet; vector manifest | partly **done 2026-11-20**: rt-core#81 lizard gate (CCN 15, 100-line functions, 600-line files, shrinking baseline of 32), #82 `derived_core.c` 1589 → 4 units, #83 `tests/host/vectors/MANIFEST.sha256` + `tools/check_vectors.py`. Open: split `derived_windows.c` (1219), `derived_d103.c` (860), `derived_ride.c` (723), one PR each; FW-3 vector compaction | vehicle-rt-core |
| T28 | BLE LESC passkey + bonding, per-device AP password + token, QUALITY CONN-2/3, MOB-4 | blocked: user (pairing method) | conn, mobile, defs |
| T29 | conn security tiers on a spare DevKit (no eFuse burns on the tester), QUALITY CONN-4 | blocked: user (spare board, IDF 5.x) | vehicle-connectivity-node |
| T30 | Python gates (mypy, coverage ratchet, ruff complexity, pip-audit) | **done** for mcp#24, ml#24, linux-node#22. vehicle-server prepared in `vehicle-server/.claude/worktrees/t30-gates` (uncommitted; the permission system refused the subagent's commit/push): **user** confirms, then commit + CI edit + PR | server |
| T31 | Adversarial tests: ASVS matrix, Hypothesis, Schemathesis, fast-check, mutmut, QUALITY PY-3, X-1 | ready after T30 | server, mcp, analyzer |
| T32 | Edge hardening | **done 2026-11-20** (linux-node#23 systemd exposure gate, #24 digest-pinned Kuksa/provider + container hardening). Open: Pi run (user, steps in `deploy/README.md`) | vehicle-linux-node |
| T33 | Analyzer quality (WEB-1..4) | **done 2026-11-20** minus CSP (analyzer#67–#71; lint ratchet 302 warnings, coverage floors, zod streams, App.tsx 633→250). Open: CSP (user), REST clients to zod, sessionClient/UdsPanel >600 lines, cargo-deny | vehicle-analyzer |
| T34 | Mobile: file splits, fvm, release signing, cleartext policy, QUALITY MOB-1/2/3/5 | blocked: user (keystore, applicationId) | vehicle-mobile |
| T35 | ADR template fields + monorepo decision with revisit trigger, QUALITY ARCH-1/3 | blocked: user (monorepo yes/no) | vehicle-workspace, vehicle-defs |
| T36 | Heartbeat golden wire vectors (safety-reviewer 2026-11-19): byte-exact 0x081/0x082 frames shared from defs; safety-node test that NODE_MODE 3/4/5/15 never selects the EKF; HIL scenario for rt-core NORMAL→DEGRADED→silent | ready (vectors), HIL blocked: Q-009 | defs, rt-core, safety-node |

## Card details

### T1 — Repin defs v0.28.0 (after T0)
- **Scope:** `manifest.yaml` pins (defs v0.28.0, analyzer v0.3.0, conn v0.5.0, mobile v0.5.0); each consumer's `external/vehicle-defs` submodule to v0.28.0, one PR per repo, merge main between dependents.
- **Order:** server first (T2's `claude/d106` reads `throttle_torque_lag_min_samples`; without the repin `test_summary_inputs` fails), then rt-core, linux-node, mobile, conn, analyzer, safety-node (safety-reviewer on the regen), ml, hil-bench. mcp has no submodule.
- **Verify:** each repo's CI green (`defs tag check` step), `python3 scripts/worktrees.py` clean after merges.

### T2 — Server branch chain
- **Preconditions:** T1 server merged. Branches exist in `vehicle-server/.claude/worktrees/` or as remote `claude/*` branches; check with `gh pr list` and `git branch -r`.
- **Scope, in order, merging main between each:** `claude/d106` (W4 cruise residuals per D-106), `claude/dq-mask` (D-104 `data_quality_mask`), `claude/coast-down` (D-105), `claude/nrc78`, `claude/faults-api` (`GET /faults`, displayable only by default; mcp#20 is already on main and answers "not available" until this lands).
- **Verify:** `uv run pytest` per PR; golden vectors unchanged unless the PR says otherwise; vehicle-mcp `list_fault_catalog` returns entries against a local server.

### T3 — rt-core dq-mask + W4 residuals
- **Preconditions:** T1 rt-core merged; rt-core#73 is on main (mailbox aged-frame drop).
- **Scope:** merge main into `claude/dq-mask`, check `VEHICLE_CL250_DERIVED_INPUT_MAX` 7 and `SENSOR_COUNT` 19 against the generated headers; implement the two W4 residuals (`throttle_torque_lag` NA when polls are too slow, D-106) in `features/derived`; resync golden vectors from the server reference (server#52+ selection). D-088 RAM budget: report the delta.
- **Verify:** host tests, cppcheck/MISRA + `gcc -pedantic` locally before push (memory: local-ci-before-push), golden 100 % exact; safety-reviewer not needed unless a safety module is touched.

### T4 — linux-node Baudrate
- **Scope:** `vehicle-linux-node-can platform` reads the `Baudrate` DBC attribute (defs#158) instead of `--platform-bitrate`; drop the note in `deploy/README.md` and CLAUDE.md.
- **Verify:** `uv run pytest`, CI `kuksa-replay` job.

### T5 — Atlas follow-ups
- **Done 2026-11-12:** 13 figures in `vehicle-defs/docs/img/hardware/`, `hardware-integration.md` §0 index, §3.5 connector/cable plan, §4.1 measurement sheet M1–M16, §4.2 Main Box layout (defs PR `claude/hw-atlas`).
- **Next (Claude):** procurement list v3.0: gland, Deutsch and cable counts from §3.5; a `SCHEMATIC-README` S1–S4 cross-reference to the figure numbers.
- **Next (user, Fusion):** draw S1 (Fig. 2), S2/S4 (Fig. 4, 7, 9, 10), S5 (Fig. 11) with the figure as the reference; fill M1–M16 on the bike.

### T6 — Pin plan to decision
- **Input from the user:** the CubeMX `.ioc` for STM32H745ZITx with the NUCLEO-H745ZI-Q selector, or a screenshot of the conflicts view, plus the UM2408 header check.
- **Scope:** diff the `.ioc` against `h755-pin-plan.md` v0.1, resolve conflicts (pin, AF, DMA request, runtime context), write the DECISIONS item draft and update Fig. 4, SCHEMATIC §7, hardware-integration §10 item 10.
- **Verify:** script check that no pin is assigned twice and none is board-reserved (the v0.1 check), user approval before the D-xxx is recorded.

### T15 — Analyzer test types in CI
- **Scope:** add `npx tsc -p tests/tsconfig.json --noEmit` as a non-blocking CI step (the three `src/` errors it reports come from vite defines and Tauri types; either give the tests tsconfig the `vite-env.d.ts` types or filter to `tests/`).
- **Verify:** CI job output shows 0 errors under `tests/`.

## Not tasks (recorded so they are not re-opened)
- D-057 intentionally unused. ML work paused until real ride data (user, 2026-11-04). vehicle-io-node retired (D-072). Meshy bike meshes stay local (licence unclear, D-033).
