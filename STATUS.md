# STATUS — session handoff

> Keep it short (≤60 lines). Updated by the `/handoff` skill. "Recent sessions" keeps at most 5 one-line entries; drop the oldest. The task cards live in `TASKS.md` (T0–T21); this file says where we are, the cards say how.

**Phase:** 0 hardware build (user, ESP32-only data-collection prototype; enclosure placement Q-034) · code without hardware largely complete up to the next user inputs: rt-core (49 class-A + 42 class-B derived signals, D-103/D-079/D-098; mailbox removed, D-118); safety-node Layer 1 v1 + platform-CAN link (D-118) + indicator input (D-111); server main: D-104/D-105/D-106, nrc78, `GET /faults` (D-109 MQTT live); linux-node L0–L4 + MQTT uplink; analyzer v0.3.0; mobile v0.5.0; vehicle-mcp v0.2.0; hardware atlas + procurement v3.0; HARA/requirements scaffold (D-113, defs `safety/` + `requirements/`)
**Last updated:** 2026-11-20

## Where we are

- **12 platform repos** + `vehicle-workspace`, public (D-033), MIT. Decisions D-001..D-119 (D-108..D-116, D-119 and the D-118 addendum (e) are PROVISIONAL); open questions up to Q-038.
- **All consumers pin defs v0.29.0** (T1, 2026-11-19); `manifest.yaml` pins defs v0.29.0, analyzer v0.3.0, conn v0.5.0, mobile v0.5.0.
- **defs main = v0.30.0 content, UNTAGGED** (CHANGELOG `[0.30.0] — unreleased`): mailbox codegen removed, DTC `SAFETY_HEARTBEAT_LOST` U0167-00 (diagnostic only, `*_DIAGNOSTIC_ONLY` flags), E2E wrappers return `WRONG_LENGTH`, `unpack_checked`/`encode_checked`, HARA/requirements rewritten for D-118 (defs#178, safety-reviewer APPROVE), one position rule `vehicle_defs.position` + vectors (defs#179, T22). Consumers wait for the tag (T20, T22).
- **D-118 hardware docs done (T21):** `docs/h743-pin-plan.md`, `docs/g474-pin-plan.md` v0.1 (from ST open pin data; every header/solder-bridge/DMA/BOOT0 line marked VERIFY for T6), procurement v3.1, atlas figures, KiCad modules NUCLEO-H743ZI2 + NUCLEO-G474RE. The user still has to buy both boards.
- **Done 2026-11-19/20 (all merged):** T2 server chain (server#76–#80), T3 rt-core D-104/D-106 + golden resync (rt-core#79/#80), T4/T7 linux-node Baudrate + node-health panel (#20/#21), T9 J2012 leads (defs#176), T19 conn D-116 quiet window (conn#53), T23 conn module split (conn#54), T27 rt-core lizard ratchet + derived_core split + vector manifest (rt-core#81–#83), T30 Python gates mcp/ml/linux-node, T32 systemd exposure gate + digest pins (linux-node#23/#24), T33 analyzer lint/coverage/zod/App split (analyzer#67–#71).
- **Merge policy (2026-11-15, user):** Claude merges its own green PRs and prunes; holds drafts, pending safety reviews and tag-gated PRs. Tags only when the user says so in that message.
- **References outside the repos:** `~/Desktop/vehicle-refs/` (SAE J2012-2002 PDF + OCR, CL250 manuals; ST PDFs RM0433, H743ZI datasheet, RM0440, G474RE datasheet, UM2407, UM2505 still to download by the user in a browser). Never commit them.

## Next up (in order)

1. **User:** say "tag defs v0.30.0" (then Claude runs `gh release create v0.30.0 -R vehicle-platform/vehicle-defs ...`). Unblocks T20 consumers (rt-core/safety-node/conn, safety-reviewer) and T22 consumers (server, ml, linux-node, mcp vendored).
2. **User:** confirm the vehicle-server T30 commit (prepared in `vehicle-server/.claude/worktrees/t30-gates`; the permission system refused the subagent's push).
3. **Claude, ready now:** T36 heartbeat wire vectors, T24 CI supply chain (template part), T31 adversarial tests (after server T30), T27 remaining splits (derived_windows/d103/ride), conn D-116 item 2, analyzer leftovers (REST clients to zod, >600-line files).
4. **User, hardware:** buy NUCLEO-H743ZI2 + NUCLEO-G474RE; CubeMX `.ioc` per board → T6 checks the VERIFY lines; open `moto-core.kicad_sym`/`moto-safety` in KiCad once; Pi run for T7/T32 (`vehicle-linux-node/deploy/README.md`); Q-034 measurements; CL250 service manual.
5. **User decisions:** QUALITY.md list (monorepo, org settings, keystore, BLE pairing, eFuse, EkfLean state 0, Analyzer CSP), Q-024, Q-025, Q-028, Q-038, D-030.

## Blockers / pending decisions

- Q-038 (platform backoff cap 30 s under D-118) before T13. Q-028 (LLM) blocks the rider `/chat` (D-115). Q-036, Q-035, Q-032, Q-031/Q-001 wait for hardware; Q-022/Q-023 (5)-(6) stay open by D-100; Q-009 blocks the hil-bench host. The G474 FDCAN board port (red zone) needs its own safety-reviewer pass.

## Recent sessions
- 2026-11-19/20 (autonomous run): T1 repin (8 repos + manifest), T21 + follow-up docs, T9, T2, T4/T7, T19, T23, T3, T20 defs v0.30.0 (2 safety-reviewer rounds), T22 defs, T27, T30 (3 repos), T32, T33; ~40 PRs merged; network/rate-limit interruptions resumed.
- 2026-11-17: branch cleanup (22 remote branches deleted, 6 ext/* backed up as bundles in `~/Desktop/vehicle-refs/branch-backups/`; T2/T3 work branches kept); full security audit + fixes (16 PRs merged, see "Where we are"); T22–T24 added.
- 2026-11-15: D-117 KiCad/FreeCAD (defs#169, workspace#213 kicad-lib); D-118 H743ZI + separate G474 safety MCU, mailbox retired (defs#170/#173, workspace#214, rt-core#76, safety-node#16, 4 safety-reviewer passes), D-119 µ cap; all open PRs merged (defs#164..#173, rt-core#75, safety-node#15, server#70, linux-node#16, 11 rule-sync PRs, mobile JDK 17 fix); tags defs v0.28.0/v0.29.0, analyzer v0.3.0, conn v0.5.0, mobile v0.5.0; 16 worktrees pruned; `~/Desktop/vehicle-refs` with SAE J2012-2002.
- 2026-11-13 (provisional run): D-108..D-116 PROVISIONAL (defs#165); T7 defs side (defs#168); T8 MQTT; D-111 indicator input; E-16 (3) + D-116 (rt-core#75); fault-source leads; cable metres.
- 2026-11-13 (night run): server#69 D-077 packaging, analyzer#61 UI-test types, defs#163 §3.5 counts, defs#164 Q-006 draft; decision brief artifact.
