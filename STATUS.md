# STATUS — session handoff

> Keep it short (≤60 lines). Updated by the `/handoff` skill. "Recent sessions" keeps at most 5 one-line entries; drop the oldest. The task cards live in `TASKS.md`; this file says where we are, the cards say how.

**Phase:** 0 hardware build (user) · rider assistant + Ride LLM run (T40-T66, continuous mode: Claude merges, prunes and tags; usage kept ≤ 85 %: ≤ 2 parallel agents)
**Last updated:** 2026-11-27

## Where we are

- **12 platform repos** + `vehicle-workspace`, public (D-033). Decisions up to **D-133** (D-127..D-133 PROVISIONAL, 2026-11-25/27; D-133 ride event marks); open questions up to **Q-040**. defs **v0.33.0** released (complaints + `faults/i18n/tr.yaml` + `engine_mechanical` ENG-001/002, alert rules ALR-001..005); server + manifest pin v0.33.0; other consumers still v0.31.0 (no need yet).
- **Rider assistant (server main):** deterministic router + template-first answers + output filter + vehicle-mcp session pool + per-user tool cache (server#101; chat-eval 44 q/locale: tool accuracy 45 → 100 %, forbidden 19 → 0, p95 ~2 s; same-author set = optimistic); stored conversations, memory facts, deterministic follow-ups, chips, token budgets, symptom fallback (server#103, follow-ups 10/10); `/chat` reports the answering model (server#98); demo scenarios `tests/make_demo_session.py --scenario` (baseline, highway, city-hot, weak-charging, cold-start).
- **vehicle-mcp main:** small specs, labelled `{name,unit,value,label}` results, `get_data_card`, `check_symptom` (multilingual IDF matcher, data-only for unconfirmed entries, D-127 addendum), `explain_context` (D-131 context: reading, conditions, history, catalog), `search_knowledge` hybrid RAG (FTS5 + sqlite-vec + multilingual-e5-small ONNX, RRF; extra `rag`; retrieval quality moderate).
- **In-ride alerts (D-129):** server#102 engine + `GET /alerts/stream` SSE + `/ws/live` `alert` + `anomaly` notifications + replay on ingest; mobile#54 banner + P1 voice + mutes. Verified end to end on the Mac (overheat mock: alert ~30 s, clear ~60 s).
- **Rider UI redesign (D-130):** mobile#50-#54 (Instrument Sans + Barlow Semi Condensed, Garage/Logbook/Assistant, rail + Cmd+K on web, ARB en/tr, locale-aware numbers/dates/voice). Known: the alert banner overlays the page header (fix in Gemini G2-3).
- **Ride LLM (D-132):** anomaly ML detects, LLM interprets, they interact via tools (item 1a). Research brief `docs/ideas/ride-llm.md`; stages T58-T65; Q-040 (training-data teacher) open, default = templates + Apache-2.0 open-weight teacher.
- **External tools:** Gemini runs 1-4 reviewed and merged (run 4: parked-current + SIL-inventory notes, 3-model bake-off page `docs/test-results/ride-llm-bakeoff/2026-11-27-stage0-3models/`, prompt-cache timings, ride marks server#108 + mobile#58, RAG eval tune/test split mcp#37, analyzer coverage 74 → 85 %). Review lessons are hard rules in `external-ai/AGENTS.base.md` §3. No brief queued.
- **Local Mac stack (git-ignored `local/`):** `local/run-llama.sh` (Qwen2.5-1.5B, `-np 1`), `local/run-server.sh` (chat on, mock live, `VEHICLE_LIVE_MOCK_SCENARIO`), data `local/server-data` (8 synthetic rides), logins in `local/secrets/`, RAG index `local/knowledge/live.sqlite`, web build at http://127.0.0.1:8000/app/. Pi `vehiclepi.local` was unreachable this session.

## Next up (in order)

Roadmap agreed 2026-11-26: the software is ahead of the hardware and everything is validated on synthetic data only, so the priority is the hardware critical path (T6 → T13 → G1 capture/T16 → first rides → T14) and checking existing work before the boards arrive; T62-T64 wait for real data.

1. **T6, user:** install STM32Cube FW_H7 V1.13.0 (local zip `local/cubemx/dl/`) + FW_G4 V1.6.3 in the CubeMX GUI (license dialog), open both `.ioc` (`local/cubemx/{rt-core,safety-node}/`; pin diff 0 mismatches), set the H743 clock tree and the VCP UART; then Claude generates code, commits it "unverified on hardware", writes the D-xxx draft, T67 Renode boot test.
2. **T58 decision:** bake-off (synthetic): held-out tool accuracy ~48-54 % for all three models, qwen3-4b slower, larger and with more forbidden hits → choose the base model; fix the Turkish `labels.stop` vs the dev `advice` forbidden pattern; check `search_knowledge`/`explain_context` templates for snake_case echoes; Turkish guard recall (ECU-flash phrasing).
3. **T57 explain mode, server side** (template on the 1.5B model, prose on ≥ 4B/cloud, per-signal reference values with status/source).
4. **RAG into `/chat`** with citations; first a tune-only pass on Turkish→English doc retrieval and the `faults/unconfirmed` chunk ranking first (test split: en R@5 0.92, tr 0.42). Then T59 GBNF; T72 multi-turn cache measurement.
5. **Small, in parallel:** T69 multi-node SIL design from `docs/ideas/sil-inventory.md`, T70 CubeMX CLI reference, T71 CI pre-checks on `ext/` branches, T73 option choice from `docs/ideas/parked-current.md` (A/B/C, needs the user).
6. **Before the boards arrive:** settle Q-008 (time sync).
7. **When the boards arrive:** T26 on-target verification, T16 listen-only capture, T73 parked-current measurement, first labelled rides.
8. **After real data:** threshold tuning (ALR-005 fires on most demo rides), T14, then T62-T64.
9. **User:** Android Studio AVD; T66 camera later; Pi power-on. Older items stay in `TASKS.md` (T5, T10-T13, T16, T17, T26, T28, T29, T34, T35).

## Blockers / pending decisions

- Q-040 (teacher model for Ride LLM training data) before T62. Q-038 before T13. Q-036, Q-035, Q-032, Q-031/Q-001 wait for hardware; Q-022/Q-023 (5)-(6) stay open by D-100; Q-009 blocks the hil-bench host.
- Every alert rule and threshold is PROVISIONAL and validated only on synthetic data (circular): real rides needed before tuning claims.

## Recent sessions
- 2026-11-26/27: T6 `.ioc` for both boards via the CubeMX CLI (0 pin mismatches; FW packages need the GUI license); roadmap + cards T67-T73; Gemini run 3 and run 4 reviewed (held-out leakage, router whole-word matching + refusal guard, `did.` scoring, mobile queue races, RAG split contamination fixed); D-133; ~30 PRs merged.
- 2026-11-25/26 (nonstop run): server up locally with mock data; D-127..D-132 (model visible, symptom check, conversations/memory, in-ride alerts, UI redesign, explain mode, Ride LLM + ML↔LLM interaction); defs v0.32.0/v0.33.0 released; ~45 PRs merged across defs/server/mcp/mobile/analyzer/workspace; DeepSeek reviewed; two 5-hour usage limits hit.
- 2026-11-25: Redmi/intercom research; Pi plan; D-122 accounts + D-123 notifications (defs#187, server#90-#92, mobile#45); rename to "Sürüş Asistanı"; local E2E on the Mac.
- 2026-11-24 (night run): D-121 rider assistant: defs#185/#186 + v0.31.0 tag and repin of 8 repos + manifest, server#87/#88, linux-node#29, mobile#43/#44, conn#60.
- 2026-11-22: safety-node#20, defs#181, server T30; defs v0.30.0; T20/T22 consumers; ci-ok + CI-5; rulesets + secret scanning (D-120); T31.
