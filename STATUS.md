# STATUS — session handoff

> Keep it short (≤60 lines). Updated by the `/handoff` skill. "Recent sessions" keeps at most 5 one-line entries; drop the oldest. The task cards live in `TASKS.md` (T0–T16); this file says where we are, the cards say how.

**Phase:** 0 hardware build (user, ESP32-only data-collection prototype; enclosure placement Q-034) · code without hardware largely complete up to the next user inputs: rt-core v0.13.0 computes 49 class-A + 42 class-B derived signals (D-103, D-079 windows, D-098 records), M7 mailbox + DTCs; safety-node Layer 1 v1 + M4 mailbox; server v0.7.0 reference (derived, health windows, bring-up gates, ride summaries, MDF4); linux-node L0–L4 (Kuksa 0.7.1 + kuksa-can-provider 0.5.1 receive-only, LDW offline, black box, systemd); analyzer v0.3.0 (A1–A15, A6 Tauri shell + listen-only HAL + bundles); mobile ride history/summaries; vehicle-mcp v0.2.0 (D-102, fault-catalog read tools on main); **hardware integration atlas** (13 figures, cable plan, Main Box layout, measurement sheet M1–M16, defs#161) and procurement list v3.0 (defs#162) on defs main
**Last updated:** 2026-11-13 (night run)

## Where we are

- **12 platform repos** + `vehicle-workspace`, public (D-033), MIT. Decisions D-001..D-107; open questions up to Q-037 (25 still open). Architecture D-072/D-073: one STM32H755 (prototype board NUCLEO-H745ZI-Q bought, D-094): M7 = rt-core, M4 = safety partition; bike ESP32 + helmet ESP32; Pi 5 edge. Boards per D-082 (A power/CAN, B Scale 1B, C1-IO + C1-IMU, C2). The user merges PRs unless they say otherwise for the session.
- **Releases pinned in `manifest.yaml`:** defs v0.27.0, rt-core v0.13.0, server v0.7.0, vehicle-mcp v0.2.0, conn v0.4.0, analyzer v0.2.0, mobile v0.4.0. **Bumped on main, tags pending (T0):** defs v0.28.0 (D-104..D-106, fault catalog D-084, `tester_rtt_did`, `Baudrate`), analyzer v0.3.0, conn v0.5.0, mobile v0.5.0.
- **Branches waiting for the v0.28.0 tag (T1–T4):** server `claude/d106` → `claude/dq-mask` → `claude/coast-down` → `claude/nrc78` → `claude/faults-api` (`GET /faults`); rt-core `claude/dq-mask` (+ W4 cruise residuals + golden resync, `INPUT_MAX` 7); linux-node reads `Baudrate` from `platform.dbc`.
- **Decision brief for the user (2026-11-13):** https://claude.ai/artifact/DA3tDXvrD2mJ9cm6uZc9L6 — Q-016, D-077 live transport, Q-029, Q-033, Q-004, Q-006, Q-027, Q-037 with Claude's recommendations (A + DBC node ids + `*_VALID` now; MQTT; yes; (a) own GPIO; platform bus instead of a UART/SPI bridge; `vehicle-defs/safety/` + `requirements/` YAML; vehicle-mcp read-only for good; rider layer = vehicle-mobile over the server API). Answers arrive as pasted text; record them in DECISIONS.md (resolved Q → D-1xx) before coding.
- **Kuksa/VSS scope:** databroker + provider deployed and CI-replayed; not done: node-health paths (Q-016), `*_VALID` leaves, 35 catalog signals and the derived/ride-summary signals without VSS paths, L3 live source (D-077 transport), vehicle-mcp live tools (D-092 item 2), Velocitas (Phase 2).
- **Analyzer:** main green (the VS Code red file was `ui-tests/import.spec.ts`: three `setInputFiles` fixtures without `mimeType`, fixed in analyzer#61) (tsc, vitest 356, build, Playwright 21, CI type-checks `tests/` since analyzer#60; `npm audit` 0 since analyzer#59, vitest 4). The 2026-11-12 "analyzer does not work" was a missing `npm install` after A6 added `@tauri-apps/api`; after any dependency PR run `npm install` in the checkout. The user mentioned another analyzer error on 2026-11-13; nothing found, ask for the exact text.
- **Procurement v3.0 CHECK (defs#162):** `hardware-integration.md` §3.5 closing line says "about 12" Deutsch pairs, the rows add up to 25 incl. G6f (Scale 1B); fix the sentence or scope it to Wave 1 before ordering. 22 AWG and 6-core LiYCY have no metres in §3.5.
- **Local checkouts:** rt-core main has a stray uncommitted diff (one blank line in `src/services/mailbox_core.c`, submodule pointer drift) and defs main a whitespace-only `gen/c/rt_core/platform.c` diff; both safe to `git checkout --`.

## Open PRs

- **defs#164 (DRAFT, awaiting Q-006):** `safety/` HARA (5 items, 18 hazards, 8 goals, S/E/C/ASIL all TBD) + `requirements/` (40 REQs in 6 domains, 27 implemented / 13 planned, every one citing a D-xxx or invariant) + `scripts/check_requirements.py` in CI. Review the "unsure" list in the PR body before accepting; it becomes the Q-006 decision. Merged in the night run: server#69 (D-077 item 3: per-device tokens `VEHICLE_DEVICE_TOKENS_FILE`, operator token kept, `device_id` on sessions, compose `remote` profile with Caddy TLS, `.env.example`, README "Deployment"), analyzer#61 (UI-test fixtures typed, `ui-tests/tsconfig.json` in CI; this was the red file in VS Code), defs#163 (§3.5 Deutsch counts by wave). Merged earlier this session: defs#161 (atlas), defs#162 (procurement v3.0), analyzer#58/#59/#60, workspace#208 (TASKS.md), workspace#209 (SCHEMATIC-README sheet→figure table).

## Roadmap (parallel tracks; G = gate)

- **S, schematics/CAD (user):** S1–S5 Fusion sheets from the atlas figures (`models/fusion-lib/SCHEMATIC-README.md` table) → S2 CubeMX pin plan check (`docs/h755-pin-plan.md` v0.1, T6) → S4 Fusion once Q-034 is measured.
- **C, code without hardware (Claude):** T1–T4 after the tags; Q-029 clamp cross-check and Q-006 HARA/requirements scaffold after the brief; T7 (Q-016) and T8 (D-077 MQTT) after their decisions; fault catalog T9 after sources.
- **H, hardware (user):** H0 Q-034 measurements (M1–M16) + Wave 1 order (procurement v3.0) → H1 Phase 0 ESP32 build → **G1** listen-only capture (Q-001), V0/V1 via `vehicle-server bringup` → H2 NUCLEO on the desk (flash, Renode, FDCAN) → H3 Wave 2 sensors.

## Next up (in order)

1. **User:** four release tags (`TASKS.md` T0, commands there) and the brief answers.
2. **Claude after the tags (one session each, `TASKS.md` cards):** T1 repin + manifest → T2 server chain (`claude/d106` first) → T3 rt-core `claude/dq-mask` + W4 residuals + golden resync (safety-reviewer not needed; vss-schema-guardian on the regen) → T4 linux-node Baudrate.
3. **Claude after the brief:** DECISIONS entries; Q-029 in safety-node `features/cornering` (`/feature-module`, safety-reviewer); Q-006 `safety/` + `requirements/` scaffold in defs with a CI traceability grep; T7 via `/signal-change` (heartbeat renames, 16 VSS leaves, regen rt-core/safety-node, linux-node L2); T8 MQTT live source (linux-node + server compose).
4. **Docs follow-ups (small):** `hardware-integration.md` 22 AWG / 6-core metres once decided; Q-029 is already implemented in safety-node cornering (README "Q-029 on raw integers"), the brief answer only closes the DECISIONS row; ISSUES E-16 (3) ISO-TP NIT (dropped FFs must not hold) needs a daytime single-task session, it changes when the sole tester stays silent.
5. **Needs the user:** CubeMX `.ioc` export for T6; IMU box product (Q-034); CL250 service manual + SAE J2012 for T9; camera model for LDW; Q-024, Q-025, D-030 confirmation.

## Blockers / pending decisions

- Everything hardware-free is blocked on T0 (tags) or the brief (Q-016, D-077 transport, Q-029, Q-033, Q-004, Q-006, Q-027, Q-037). Q-036, Q-035, Q-032, Q-031/Q-001 wait for hardware or their trigger; Q-022/Q-023 (5)-(6) stay open by D-100 until the C1-IMU exists; Q-009 blocks the hil-bench host.

## Recent sessions

- 2026-11-13 (night run, user asleep, merges authorised): server#69 D-077 packaging, analyzer#61 UI-test types (the red file), defs#163 §3.5 counts, defs#164 Q-006 draft; earlier: analyzer npm install fix, audit 0 (#59), T15 (#60), T5 (defs#162, workspace#209), atlas and TASKS merged, decision brief artifact, ISSUES E-30 (5) closed.
- 2026-11-12: D-107 import-path convention recorded, rules synced to all 12 repos, analyzer/mobile/conn imports refactored; TASKS.md cards T0–T16; hardware atlas PR.
- 2026-11-11: Raspi track L0–L4 + deploy (linux-node#10–#14), analyzer A6 shell/HAL/bundles, defs#157 §5b.8; night run D-104..D-106 + fault catalog D-084 in untagged defs 0.28.0.
- 2026-11-10: defs v0.27.0 (scan `sensitive` flag), consumers repinned, release bumps analyzer/conn/mobile.
- 2026-11-06: D-079 health-window instances in server/analyzer/mobile; seeded property tests.
