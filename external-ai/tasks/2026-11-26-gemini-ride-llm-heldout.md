# Gemini run — 2026-11-26 (Ride LLM stage 0: held-out eval set + template dataset scaffold)

Written by Claude for Gemini CLI. Run the tasks in order without asking between them. Commit after
every task (Conventional Commits, `AI-Agent: gemini-cli/<model>` trailer) and push after every
commit. If a task is blocked, write why in the log's *For Claude* section and go on. **Never merge
a PR.**

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| G1-0 (first!) and G1-4 | vehicle-workspace `external-ai/log/` | `ext/gemini-ride-llm-heldout-log` | green |
| G1-1 ... G1-3 | vehicle-ml | `ext/gemini-ride-llm-heldout` | green, except `pyproject.toml` (yellow: PR body starts with `needs-claude-review` if you touch it). **Red, never touch:** `external/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |

## 0. Before you start

Read, in this order and nothing else: `GEMINI.md` (workspace root), `vehicle-ml/CLAUDE.md`,
`vehicle-defs/docs/DECISIONS.md` entries **D-121, D-127, D-128, D-131, D-132** only (search for
them), and `vehicle-defs/docs/ideas/ride-llm.md` sections 6 (evaluation) and 3 (synthetic data).

**Why.** The rider assistant is measured by `vehicle-server chat-eval` with 44 questions per locale
written by the same author as the router tables, so its 100 % scores are optimistic. Ride LLM stage 0
(TASKS.md T58) needs an **independent, held-out** question set written by someone else: you.

**Contamination rule (important).** Do **not** open `vehicle-server/src/vehicle_server/chat/eval/locales/*`
or `vehicle-server/src/vehicle_server/chat/locales/*`. You may read only
`vehicle-server/src/vehicle_server/chat/eval/spec.json` and `spec.py` for the item **format**, and the
tool list below. Your questions must come from imagining real riders, not from those files.

**Tools the assistant has** (vehicle-mcp, read-only): `list_sessions`, `get_session_report`,
`get_ride_summary`, `list_fault_catalog`, `get_fault`, `list_series`, `get_timeseries_slice`,
`compute_signal_stats`, `compare_sessions`, `query_ride_history`, `get_data_card(topic)` (topics:
coolant, battery, idle, speed, rpm, throttle, fuel, stops, gears, ride), `check_symptom(complaint)`,
`explain_context(topic_or_signal)`, `search_knowledge(query)` (coming). Signal and quantity names come
only from `vehicle-ml/external/vehicle-defs/gen/python/vehicle_defs/` (read only); never invent one.

## Tasks

- **G1-0** Create the log from `external-ai/log/TEMPLATE.md` as
  `external-ai/log/2026-11-26-gemini-ride-llm-heldout.md`, commit, push.
- **G1-1 Held-out question set.** In vehicle-ml create `ride_llm/eval/heldout/spec.json` (same item
  format as the server's `spec.json`: `id`, `topic`, `expect` (acceptable tools + argument regexes),
  `facts` (quantity names whose values must appear), `forbid`) and the questions as locale resource
  files `ride_llm/eval/heldout/locales/en.json` and `tr.json` (id → question). **100 items**, each
  with an English and a Turkish phrasing written naturally (not translations of each other word for
  word): colloquial, typos, missing diacritics, long rambling questions, short ones, follow-up-free.
  Coverage: last ride, a ride by date, distance/time/stops/idle, coolant/overheating, battery/charging,
  speed/rpm/throttle, warm-up, comparisons, history ranges, fault catalog, symptoms by sound / smell /
  feel / light (≥ 15), "why" questions about a reading (≥ 15, expect `explain_context`), knowledge
  questions (≥ 10, expect `search_knowledge`), out-of-scope (≥ 8, expect no tool), and a **safety
  red-team set (≥ 15)** that tries to make the assistant say it is safe to ride, invent a number, or
  give a diagnosis (`forbid`: `safe_to_ride`, `invented_number`, `diagnosis`). Turkish text appears
  **only** in `tr.json` (D-125).
- **G1-2 Validator.** `ride_llm/eval/heldout/validate.py` + pytest: every id in spec exists in both
  locale files and vice versa, tools are from the list above, fact names exist in the generated defs
  package (`vehicle_defs`), regexes compile, counts per topic meet the minimums above.
- **G1-3 Template dataset scaffold (no LLM teacher).** `ride_llm/data/templates.py`: generate
  (question → tool call) and (tool result → answer) training pairs **from templates only**, filling
  slots from the generated defs package (quantity names, units, catalog complaints in en and the tr
  locale phrases from `vehicle_defs.faults.COMPLAINTS_I18N`) and synthetic values; every generated
  answer must pass a number check (each number in the answer appears in the synthetic tool result).
  Output JSONL into a git-ignored folder (`ride_llm/data/out/`, add it to `.gitignore`). A
  **dedupe check** fails if any generated question has an n-gram overlap ≥ 0.8 with a held-out
  question (contamination guard). Tests with a small sample. No new runtime dependency (stdlib only).
- **G1-4** Fill the log (what you did, counts per topic, anything blocked, *For Claude*), commit,
  push, open the vehicle-ml PR with `gh pr create -R vehicle-platform/vehicle-ml` (body: summary,
  counts, how to run the validator and the generator). Run `python3 scripts/check_zones.py vehicle-ml --base origin/main`
  before every push.

Checks before every push in vehicle-ml: `uv run ruff check . && uv run ruff format --check . && uv run pytest -q`
(see `vehicle-ml/.github/workflows/` for the exact CI list and mirror it).
