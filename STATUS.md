# STATUS — session handoff

> Keep it short (≤60 lines). Updated by the `/handoff` skill. "Recent sessions" keeps at most 5 one-line entries; drop the oldest. The task cards live in `TASKS.md` (T0–T21); this file says where we are, the cards say how.

**Phase:** 0 hardware build (user, ESP32-only data-collection prototype; enclosure placement Q-034) · code without hardware largely complete up to the next user inputs: rt-core (49 class-A + 42 class-B derived signals, D-103/D-079/D-098; mailbox removed, D-118); safety-node Layer 1 v1 + platform-CAN link (D-118) + indicator input (D-111); server v0.7.0 + MQTT live (D-109); linux-node L0–L4 + MQTT uplink; analyzer v0.3.0; mobile v0.5.0; vehicle-mcp v0.2.0; hardware atlas + procurement v3.0; HARA/requirements scaffold (D-113, defs `safety/` + `requirements/`)
**Last updated:** 2026-11-17

## Where we are

- **12 platform repos** + `vehicle-workspace`, public (D-033), MIT. Decisions D-001..D-119 (D-108..D-116, D-119 and the D-118 addendum (e) TX-refusal rule are PROVISIONAL); open questions up to Q-038. **No open PRs**, every local checkout on a clean `main`, only the main worktree per repo.
- **D-118 (2026-11-15): two chips.** The H745/H755 boards were never in hand (out of stock). rt-core → **STM32H743ZI (NUCLEO-H743ZI2)**, single M7, full 2 MB/1 MB. Safety partition → separate **STM32G474RE (NUCLEO-G474RE**, fallback G431RB) on the platform CAN bus; HSEM mailbox retired (rt-core#76, safety-node#16, both 2 safety-reviewer rounds). Invariants 3 and 8 reworded (workspace#214, rules synced to all repos). D-119: µ_eff capped at the default until rt-core sends 0x022 (user's choice). The user still has to buy both boards.
- **D-117 (2026-11-15):** electronics CAD = **KiCad**, mechanics = **FreeCAD** + KiCad StepUp; `models/fusion-lib` → `models/kicad-lib` (generated `.kicad_sym` + `.pretty`, workspace#213; never opened in KiCad yet: first open is the format check). Fusion retired.
- **Releases:** tags created 2026-11-15: defs **v0.28.0** and **v0.29.0** (D-108 node-health names/VSS), analyzer v0.3.0, conn v0.5.0, mobile v0.5.0. `manifest.yaml` still pins the old set (defs v0.27.0, conn v0.4.0, analyzer v0.2.0, mobile v0.4.0): T1.
- **Merge policy changed (2026-11-15, user):** Claude merges its own green PRs, prunes worktrees and pulls mains without being asked; holds drafts, pending safety reviews and tag-gated PRs. Tags: Claude runs `gh release create` when the user says so in that message.
- **References outside the repos:** `~/Desktop/vehicle-refs/` (SAE J2012-2002 PDF + OCR text, CL250 owner's manual JP, CL fact book; `st/` empty: st.com blocks scripted downloads, the user downloads UM2408/RM0399 in a browser; for the H743/G474 the needed ones are now RM0433, the H743ZI datasheet, RM0440, the G474RE datasheet, UM2407 Nucleo-64). Never commit them.
- **Security audit 2026-11-17 (5 parallel audits, all fixes merged):** 0 critical. HIGH fixed: server zip bomb + missing device/operator token scope (server#72, now device = own sessions, operator/`reader` = all), workspace `check_zones.py` red-zone bypass via quoted names (workspace#216). Also fixed: MCP/ml position filters weaker than the server's (mcp#23, ml#22), MCP untrusted-text marking and result caps, linux-node plaintext MQTT/position, black-box poller, systemd sandboxing (linux-node#18, **verify on the Pi**), `worktrees.py --prune` deleting fresh worktrees/unmerged branches (workspace#216), analyzer CSV injection/SLCAN parser (analyzer#64/#65), mobile cleartext token guard + allowBackup off (mobile#38), conn RTR/DLC (conn#51), CI `permissions`, `.gitignore` secrets, defs CODEOWNERS, certifi CVE (server#73); refactors server#74, workspace#217. Invariant 1 held everywhere; no secrets or real GPS in any repo or history. **Ops notes:** server container now runs as uid 10001 (`chown` an existing `/data`, README), broker restart for `use_username_as_clientid`; git author e-mail switched to the GitHub noreply address (history not rewritten, user's choice). Reports: session scratchpad only; follow-ups T20 (E-5..E-7), T22–T24.
- **mobile CI:** the runner's default JDK became 25 (Gradle 8.14 fails); JDK 17 pinned in `build-apk` (mobile#37).
- **Procurement v3.0 CHECK:** §3.5 Deutsch counts fixed (defs#163); cable metres are estimates (defs#166, CONFIRM with M1–M16); add NUCLEO-H743ZI2 + NUCLEO-G474RE, drop the H745 line (T21).

## Roadmap (parallel tracks; G = gate)

- **S, schematics/CAD (user, KiCad):** S1–S5 sheets from the atlas figures (`models/kicad-lib/SCHEMATIC-README.md`) → T6 CubeMX `.ioc` for **both** boards → S4 FreeCAD enclosure once Q-034 is measured.
- **C, code without hardware (Claude):** T1 repin → T2–T4 → T7 consumers → T20 defs mailbox removal → T21 hardware docs; T9 with the J2012 text.
- **H, hardware (user):** buy NUCLEO-H743ZI2 + NUCLEO-G474RE · H0 Q-034 measurements + Wave 1 order → H1 Phase 0 ESP32 build → **G1** listen-only capture (Q-001) → H2 both NUCLEOs on the desk → H3 Wave 2 sensors.

## Next up (in order)

0. **Quality roadmap ready (T25 done):** `QUALITY.md` has all 40 deductions researched, the card map T26–T35 and a "User decisions" list (monorepo: research recommends NOT now; GitHub org settings; keystore; BLE pairing method; ESP32 eFuse only on a spare board; EkfLean state 0). Ask the user for these decisions; ready without them: T30 (Python gates), T27, T33 (minus CSP), T32 (minus the Pi run).
1. **Claude, T1:** repin every consumer to defs **v0.29.0** + `manifest.yaml` with the new tags (analyzer v0.3.0, conn v0.5.0, mobile v0.5.0, defs v0.29.0); rt-core and safety-node on the SAME tag; `vss-schema-guardian` on the regen; safety-reviewer for rt-core/safety-node (ISSUES E-31 (3): NODE_MODE prefixes, `vehicle_cl250.c` gate diff, server `mock_stream.py` heartbeat names).
2. **Claude:** T2 server chain (`claude/d106` first) → T3 rt-core `claude/dq-mask` + W4 residuals + golden resync → T4 linux-node Baudrate (branches were built on 0.28.0: rebase onto 0.29.0).
3. **Claude, T20 (`/signal-change`, defs next minor):** remove `mailbox/`, `gen_mailbox.py`, `platform_mailbox.h`, LAYOUT_ID; replace DTCs `SAFETY_MAILBOX_*` with a diagnostic-only SAFETY heartbeat-lost DTC + an rt-core 0x082 monitor; DBC node/message comments (D-118 item 6).
4. **Claude, T21 (docs):** H743 + G474 pin plans (replace `h755-pin-plan.md`), atlas Fig. 01/03/04/05, procurement (two boards), KiCad modules NUCLEO-H743ZI2 + NUCLEO-G474RE in `models/kicad-lib/_generator/modules.py`.
5. **Claude:** T9 fault catalog: verify the 12 defs#167 leads against `~/Desktop/vehicle-refs/sae/SAE_J2012_2002_ocr.txt` (cite "SAE J2012-2002 §x", no text copied); T19 conn parity with D-116; T7 linux-node L2 panel.
6. **Needs the user:** buy the two boards; CubeMX 6.18.0 (Apple Silicon) + `.ioc` per board (T6); open `moto-core.kicad_sym` once in KiCad and report errors; CL250 service manual (Honda dealer); IMU box product (Q-034); camera model for LDW; Q-024, Q-025, Q-028, Q-038, D-030 confirmation.

## Blockers / pending decisions

- Q-038 (platform backoff cap 30 s under D-118, availability only) before T13. Q-028 (LLM) blocks the rider `/chat` (D-115). Q-036, Q-035, Q-032, Q-031/Q-001 wait for hardware; Q-022/Q-023 (5)-(6) stay open by D-100 until the own IMU exists; Q-009 blocks the hil-bench host. The G474 FDCAN board port (red zone) needs its own safety-reviewer pass and the D-118 addendum (d) obligations.

## Recent sessions

- 2026-11-17: branch cleanup (22 remote branches deleted, 6 ext/* backed up as bundles in `~/Desktop/vehicle-refs/branch-backups/`; T2/T3 work branches kept); full security audit + fixes (16 PRs merged, see "Where we are"); T22–T24 added.
- 2026-11-15: D-117 KiCad/FreeCAD (defs#169, workspace#213 kicad-lib); D-118 H743ZI + separate G474 safety MCU, mailbox retired (defs#170/#173, workspace#214, rt-core#76, safety-node#16, 4 safety-reviewer passes), D-119 µ cap; all open PRs merged (defs#164..#173, rt-core#75, safety-node#15, server#70, linux-node#16, 11 rule-sync PRs, mobile JDK 17 fix); tags defs v0.28.0/v0.29.0, analyzer v0.3.0, conn v0.5.0, mobile v0.5.0; 16 worktrees pruned; `~/Desktop/vehicle-refs` with SAE J2012-2002.
- 2026-11-13 (provisional run): D-108..D-116 PROVISIONAL (defs#165); T7 defs side (defs#168); T8 MQTT; D-111 indicator input; E-16 (3) + D-116 (rt-core#75); fault-source leads; cable metres.
- 2026-11-13 (night run): server#69 D-077 packaging, analyzer#61 UI-test types, defs#163 §3.5 counts, defs#164 Q-006 draft; decision brief artifact.
- 2026-11-12: D-107 import-path convention, rules synced, imports refactored; TASKS.md cards T0–T16; hardware atlas PR.
