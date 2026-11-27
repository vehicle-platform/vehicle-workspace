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
| T19 | conn parity with D-116 | **done 2026-11-21** (conn#53 quiet window, #56 item 2 non-0x62 FF ends the read, #57 item 3 invalid FFs never hold) | vehicle-connectivity-node |
| T20 | defs v0.30.0 + consumers | **done 2026-11-22**: defs#178 (tag v0.30.0), rt-core#89 `features/safety_hb` 0x082 monitor → SAFETY_HEARTBEAT_LOST (NO_NEW_DATA only, grace from the first pass), generated DIAGNOSTIC_ONLY flags, checked 0x020 pack; rt-core#90 CI confinement greps + hostile-stream test; safety-node#23/#24; safety-reviewer APPROVE on all. Open: HIL `safety_hb_boot_race`, `platform_0x082_babble` (Q-009) | rt-core, safety-node |
| T21 | Hardware docs for D-118 | **done 2026-11-19** (defs#175, #177; workspace#225 KiCad modules). Every VERIFY line (header positions, solder bridges, DMA, G474 BOOT0 option bytes, G431 fallback, G474 morpho table) goes to T6 | vehicle-defs, workspace |
| T22 | One position rule (D-076) | **done 2026-11-22** (defs#179; server#84, ml#27, mcp#27 vendored + sha256 pin, linux-node#28 canonical rule + its stricter local altitude-change filter; no repo less strict) | defs, server, mcp, ml, linux-node |
| T23 | conn: split `HondaCANModule.cpp` | **done 2026-11-19** (conn#54, pure moves verified by line multiset; SF check deduped; 296/296 native tests) | vehicle-connectivity-node |
| T24 | CI supply chain + org settings | **done 2026-11-22**: SHA pins, gitleaks, pin-check, Renovate config (10 repos + defs#181), `ci-ok` aggregate + CI-5 weekly audits (11 PRs), rulesets + secret scanning/push protection on all public repos (D-120, `scripts/rulesets/`). **User:** install the Renovate GitHub App; vehicle-server/vehicle-ml are private, so no rulesets/secret scanning on the free plan (make public per D-033 or buy a plan) | all repos |
| T25 | Quality research pass for every deduction in `QUALITY.md` | done 2026-11-17 (R1–R4 folded into QUALITY.md, cards T26–T35) | vehicle-workspace |
| T26 | On-target verification layer (IWDG/WWDG, MPU, stack HWM, DWT WCET) on H743 + G474, QUALITY FW-1 | blocked: hardware | rt-core, safety-node |
| T27 | rt-core module split + lizard ratchet; vector manifest | **done 2026-11-21** (rt-core#81–#86: lizard gate, derived_core/windows/d103/ride split by verified moves, vector manifest; only `uds_client_core.c` (967 lines) left in the size baseline). Open: FW-3 vector compaction | vehicle-rt-core |
| T28 | BLE LESC passkey + bonding, per-device AP password + token, QUALITY CONN-2/3, MOB-4 | blocked: user (pairing method) | conn, mobile, defs |
| T29 | conn security tiers on a spare DevKit (no eFuse burns on the tester), QUALITY CONN-4 | blocked: user (spare board, IDF 5.x) | vehicle-connectivity-node |
| T30 | Python gates | **done 2026-11-21** (mcp#24, ml#24, linux-node#22, server#82) | server, mcp, ml, linux-node |
| T31 | Adversarial tests | **done 2026-11-22** (server#85/#86, mcp#28, analyzer#75/#76): ASVS auth matrix, upload cases, Hypothesis, Schemathesis, fast-check; 12 real bugs fixed (server 500s → 422, regex newline/Unicode digits, deep-JSON recursion, MCP fence escape, SLCAN 29-bit ids, unbounded buffer, CSV extended flag). Mutation (opt-in): server 473/589, analyzer 80.4 %. Open: CSV cell with a newline (`it.fails`), server 4xx bodies vs OpenAPI | server, mcp, analyzer |
| T32 | Edge hardening | **done 2026-11-20** (linux-node#23 systemd exposure gate, #24 digest-pinned Kuksa/provider + container hardening). Open: Pi run (user, steps in `deploy/README.md`) | vehicle-linux-node |
| T33 | Analyzer quality (WEB-1..4) | **done 2026-11-20** minus CSP (analyzer#67–#71; lint ratchet 302 warnings, coverage floors, zod streams, App.tsx 633→250). Open: CSP (user), REST clients to zod, sessionClient/UdsPanel >600 lines, cargo-deny | vehicle-analyzer |
| T34 | Mobile: file splits, fvm, release signing, cleartext policy, QUALITY MOB-1/2/3/5 | blocked: user (keystore, applicationId) | vehicle-mobile |
| T35 | ADR template fields + monorepo decision with revisit trigger, QUALITY ARCH-1/3 | blocked: user (monorepo yes/no) | vehicle-workspace, vehicle-defs |
| T40 | Assistant run (2026-11-25, user: "start every optimisation that makes the LLM and the MCP layer work properly and connect them; don't stop, resume when tokens renew"): see the T40-T50 block under Card details. Defs v0.32.0 complaints (defs#197) + tag + repin server/mcp/manifest | **done 2026-11-26** (defs#197 → v0.32.0, defs#199/#200 → v0.33.0; server#100 repin + `/faults` complaints; workspace#242 manifest) | defs, server, mcp, workspace |
| T41 | Chat eval harness + baseline run (tool-choice accuracy, guard pass, latency p50/p95, local model) | **done 2026-11-26** (server#99 `vehicle-server chat-eval`, 44 questions per locale; baseline defs#201) | vehicle-server, defs `docs/test-results/` |
| T42 | MCP/LLM efficiency: MCP session pool, compact router menu, stable cached prefix, per-ride tool cache, template-first, llama `-np 1`/`cache_prompt`, Anthropic `cache_control` | **done 2026-11-26** (server#101: router, template-first answers + output filter, MCP session pool, per-user tool cache, compact prompt, Anthropic cache_control; tool accuracy 45 % → 100 % en / 43 % → 100 % tr, forbidden patterns 19/14 → 0, p95 21-29 s → ~2 s; same-author question set, held-out set open) | vehicle-server, vehicle-linux-node |
| T43 | vehicle-mcp: labelled compact results, small-model tool descriptions, `get_data_card`, `check_symptom` (D-127) | **done 2026-11-26** (mcp#30 specs −49 %, labelled results, `get_data_card`, `check_symptom`; mcp#31 multilingual IDF matcher; data-only unconfirmed matches in progress, D-127 addendum defs#202) | vehicle-mcp |
| T44 | Conversations + memory (D-128 items 1-3, 6): store, API, carried state, follow-up resolution, budgets, user memory, FTS search | **done 2026-11-26** (server#103: conversations, memory, follow-ups 10/10, chips, budgets, symptom fallback) | vehicle-server |
| T45 | No-dead-end ladder + follow-up chips (D-128 item 5) | after T43, T44 | vehicle-server |
| T46 | Streaming answers (`/chat` SSE) | after T44 | vehicle-server |
| T47 | Mobile: chat list, temporary chat, chips, memory settings, streaming (functional only; look waits for Q-039) | after T44-T46 | vehicle-mobile |
| T48 | D-129 alert rules in defs (schema + codegen Python/Dart) | **done 2026-11-26** (defs#199, 5 PROVISIONAL rules, Python + Dart) | vehicle-defs |
| T49 | D-129 evaluator on vehicle-server live stream + `/alerts/stream` + `anomaly` notifications; mobile banner + P1 voice | **done 2026-11-26** (server#102 engine + SSE + replay; mobile#54 banner + P1 voice + mutes; verified end to end) | vehicle-server, vehicle-mobile |
| T50 | After-run eval vs T41 baseline, `docs/test-results/` write-up, STATUS handoff | last | defs, workspace |
| T51 | D-130 redesign PR 2 (assistant logbook transcript, data cards, chips, Logbook/Garage/Ride screens, AlertBanner) | **done 2026-11-26** (mobile#50-#54); banner overlays the header → Gemini G2-3 | vehicle-mobile |
| T52 | Router/phraser model split benchmark: tiny router (Qwen2.5-0.5B, Gemma 3 1B, Llama 3.2 1B) vs phraser (Qwen2.5-1.5B/3B, Gemma 3 4B, Qwen3 1.7B), measured with the T41 harness on the Mac (Pi when reachable) | after T42 | vehicle-server, linux-node, defs `docs/test-results/` |
| T53 | GBNF grammar + few-shot examples in the stable prefix for tool choice; multilingual embedding intent router (small embedding model via llama-server `/embedding`) before the LLM | after T42 | vehicle-server |
| T54 | Answer cache for repeated questions per ride; llama-server KV slot save/restore per conversation; speculative decoding with a draft model (`-md`) | after T44 | vehicle-server, linux-node |
| T55 | Eval set growth (follow-ups after T44, symptoms after v0.32.0 repin) + a CI regression gate with a recorded fake LLM | after T44 | vehicle-server |
| T56 | Repin defs v0.32.0/v0.33.0 in server (+ `/faults` serves `complaints` and `complaints_i18n`), mobile (alert rules Dart), manifest | server + manifest **done 2026-11-26** (server#100, workspace#242); mobile repin goes with T49 | server, mobile, workspace |
| T57 | D-131 explain mode, server side: "why/is it normal" intent + follow-ups, compact `explain_context` (≤ 500 tokens for the local model), template explanation on the small model, LLM prose on ≥ 4B/cloud, cited web research via the provider's own search with consent; defs + server expose per-signal reference values with status/source for `explain_context.references` | after T44 | defs, server, mcp, mobile |
| T58 | Ride LLM stage 0 (D-132): eval hardening (≥ 300 generated + ~100 frozen human en/tr cases, red-team "safe to ride" set, bootstrap CIs, CI gate guard failures = 0) + base-model bake-off Qwen2.5-1.5B / Qwen3-1.7B / Qwen3-4B on the Mac and the Pi | ready | server, ml, defs test-results |
| T59 | Ride LLM stage 1: grammar-constrained (GBNF) tool choice in llama.cpp | after T58 | server |
| T60 | Ride LLM stage 2: hybrid retrieval (SQLite FTS5 + sqlite-vec, multilingual-e5-small, RRF) over catalog phrases and repo docs with citations; local-only indexer for the rider's own manuals (git-ignored, CI check against committed PDFs/quotes) | **done 2026-11-26** (mcp#34 hybrid RAG); quality pass → Gemini G2-2 | mcp, server |
| T61 | Ride LLM stage 3: knowledge-graph tables + tools (signal ↔ subsystem ↔ fault ↔ symptom ↔ check) over defs | after T58 | defs, mcp |
| T62 | Ride LLM stage 4: synthetic data pipeline with verifiers (templates + open-weight teacher by default; Q-040 decides any frontier role); contamination control vs the eval set | after T58; Q-040 | ml |
| T63 | Ride LLM stage 5: LoRA SFT (MLX on the Mac) → GGUF + adapter, quantisation comparison F16/Q8/Q5/Q4 on the harness, Pi latency | after T62 | ml, linux-node |
| T64 | Ride LLM stage 6: preference tuning (KTO/DPO) against invention and unsafe claims | after T63 | ml |
| T65 | ML ↔ LLM tools (D-132 item 1a): `get_anomalies`, subsystem drill-down, rider feedback → structured weak labels (consented) | after the D-083 stage 1 models exist | ml, mcp, server |
| T66 | CV prototype with the user's DJI Osmo Action 4: (1) USB webcam mode on the Mac/Pi 5 — list formats (`v4l2-ctl --list-formats-ext`; third-party sources say 1080p30 MJPG), measure glass-to-glass latency with an on-screen stopwatch, USB power draw and heat over 30 min; (2) dataset protocol: 4K stabilised ride recordings synced to telemetry by a visible clap/flash marker, stored git-ignored under `local/` (never committed, D-033); (3) lane-keeping classic CV developed offline on the recordings; production camera stays Pi Camera Module 3 (procurement 3B) | user: "later, let's try it" | linux-node |
| T67 | Renode boot test of the CubeMX-generated images (H743 + G474) in CI: boot, FreeRTOS tasks (rt-core), watchdog kick, FDCAN frames on a virtual bus; catches first-boot failures before the boards arrive | after T6 | rt-core, safety-node |
| T68 | Ride event marking in the mobile app ("misfire here", "ramp", "traffic"): timestamped rider marks stored with the ride as consented weak labels for the anomaly model (early part of T65) | ready | mobile, server, defs |
| T69 | Multi-node SIL design note: the rt-core host SIL (existing decision) plus a safety-node host build and the server on one virtual bus (`vcan` / in-process on macOS) to test the E2E platform-bus contract, own-IMU fallback and the alert flow end to end; placement needs the user (independent of Q-009) | user: placement | workspace, rt-core, safety-node |
| T70 | CubeMX CLI reference (headless `-q` scripts: `popupwrapper set` first, `loadboard <board> nomode`, `get mode available <IP>`, `config saveas`, `csv pinout`, kill guard) as a shared reference or skill so later sessions do not re-probe | after T6 | workspace |
| T71 | CI pre-checks on `ext/` branches (zones, lint, tests, `AI-Agent:` trailer, log present) so the Claude review starts from a green baseline | ready | workspace, all repos |
| T72 | llama.cpp prompt/KV cache reuse for the fixed system prompt + tool specs; measure time to first token on the 1.5B model before/after with chat-eval | with T59 | server, linux-node |
| T73 | Parked (key-off) current budget: sleep modes of Pi 5, ESP32-S3, H743, G474 vs the CL250 battery; design review now, measurement when the boards arrive | design ready; measurement blocked: hardware | rt-core, conn, linux-node, defs |
| T74 | Upstream contributions (Kuksa / COVESA), drafts only until the user approves each submission (publishing is outward-facing): (1) COVESA VSS issue proposing a generic two-wheeler branch from our `Vehicle.Motorcycle` overlay — lean angle + quality/state, side stand, friction and mass estimates — after checking the current VSS release for existing equivalents and the CONTRIBUTING rules; platform-specific signals (node health, validity flags) and CL250 DIDs/CAN IDs stay out; (2) Kuksa docs/example: running databroker + kuksa-can-provider replay on macOS without CAN hardware (colima, `--dumpfile`, host-network note), verified in vehicle-linux-node#35; (3) a generic motorcycle example config for kuksa-can-provider (example DBC + mapping, no reverse-engineered OEM IDs). Thesis value: documented standard gap + proposal | ready (drafts); submission needs the user | linux-node, defs, workspace |
| T75 | Edge deployment manager comparison on the Raspberry Pi 5 (D-136): Docker Compose (today), Eclipse Kanto (container-management + update-manager), Podman with systemd Quadlets, and k3s as a heavier reference; run the same Kuksa databroker + kuksa-can-provider pair under each and report idle/peak RAM and CPU, startup time, the update flow (desired state, rollback, how it fits our signed OTA packages), and maintenance status (last release, commit activity, security fixes; Kanto's last release is v1.0.0 from 2024-06). Output: `docs/test-results/edge-deployment/` (measured) + a recommendation; the switch decision follows the report | blocked: hardware (Pi on the desk) | linux-node, defs |
| T76 | Repository visibility split (D-135): inventory what in the public repos is vehicle-specific or commercially sensitive (reverse-engineered CL250 CAN IDs and DIDs in `vehicle-defs/dbc/cl250.dbc` and `uds/vehicle_cl250.yaml`, the legacy `HondaCl250_Telemetry`, anything model- or customer-specific), design the split (a private per-vehicle pack consumed by the public codegen; the public repo keeps the generic catalog and a synthetic example vehicle), keep CI light in private repos (Free plan: 2,000 Actions minutes/month, no rulesets on private repos), then move with the user's approval. Note: content already public stays in clones and forks; history rewriting only on the user's explicit decision | next; moving needs the user | defs, all consumers, workspace |
| T36 | Heartbeat golden wire vectors | **done 2026-11-21** (defs#180, safety-node#20); HIL scenario blocked: Q-009 | defs, safety-node |

## Card details

### T40-T50 — Assistant LLM + MCP run (D-127, D-128, D-129)

Measured 2026-11-25 on the Mac (local Qwen2.5-1.5B, 5 synthetic rides): answers 2-14 s, two LLM calls per question (tool choice + phrasing); vehicle-mcp is spawned per request (~0.4 s spawn + initialize + list); the 10 tool specs are ~6.3k characters (~1.6k tokens) in the router prompt of a 4k-context model; failures seen: catalog listed as if faults were active, "duration as speed" unit swap, overheating/idle/symptom questions unsupported. Local run: `local/run-llama.sh` + `local/run-server.sh` (git-ignored `local/`, data in `local/server-data`, logins in `local/secrets/`).
- Order: T40 + T48 in parallel with T41; T42 after server#98; T43 in parallel (mcp repo); T44 → T45 → T46 in vehicle-server (same files, never stacked); T47 after the server API; T49 after T48; T50 last.
- Every optimisation lands with a before/after number from the T41 harness (same question set, same model, same machine).
- Continuous run (2026-11-26, user: "keep developing, one next task after another, until I say stop; if there is nothing else, work on optimising this LLM infrastructure"; "record these and do them"; "you will also do the releases"; "don't stop until I say, I'll leave it open while I sleep"): after T50 continue with T51-T56, then further measured LLM/MCP optimisation. Claude creates the release tags too.
- Resume rule: a new session reads STATUS.md, this block and `gh pr list` for open `claude/*` PRs, then continues with the first card not marked done in the table.

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
- **Boards (D-118):** NUCLEO-H743ZI2 (rt-core, STM32H743ZIT6) and NUCLEO-G474RE (safety-node, STM32G474RET6). Plans: `vehicle-defs/docs/h743-pin-plan.md` and `g474-pin-plan.md` (the old `h755-pin-plan.md` is retired).
- **Claude:** generate one `.ioc` per board with the CubeMX CLI (headless script mode, board loaded with `nomode`, pins, peripheral modes, DMA, toolchain CMake), export the pinout CSV and run the diff script (every planned pin and AF present, no pin assigned twice, no board-reserved pin reused). Work files live in git-ignored `local/cubemx/`. Where the CLI cannot set something, the `.ioc` text is edited and reloaded so CubeMX validates it.
- **User:** open each `.ioc` in the CubeMX GUI and confirm the pinout/conflict view and the Clock tab (no clock tree is invented by Claude; board defaults stay until the user sets it), plus the UM2407/UM2505 header and solder-bridge check. Firmware packages (STM32Cube_FW_H7, STM32Cube_FW_G4) come from Help > Manage embedded software packages if the CLI cannot install them.
- **Then:** user approval before the D-xxx is recorded; update Fig. 4, SCHEMATIC §7 and hardware-integration §10 item 10. The `.ioc` and the generated code may be committed to rt-core / safety-node before the boards arrive, marked "unverified on hardware" (user's wish); red zone, so `safety-reviewer` first for safety-node.

### T15 — Analyzer test types in CI
- **Scope:** add `npx tsc -p tests/tsconfig.json --noEmit` as a non-blocking CI step (the three `src/` errors it reports come from vite defines and Tauri types; either give the tests tsconfig the `vite-env.d.ts` types or filter to `tests/`).
- **Verify:** CI job output shows 0 errors under `tests/`.

## Not tasks (recorded so they are not re-opened)
- D-057 intentionally unused. ML work paused until real ride data (user, 2026-11-04). vehicle-io-node retired (D-072). Meshy bike meshes stay local (licence unclear, D-033).
