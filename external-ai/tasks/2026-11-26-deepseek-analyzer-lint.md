# DeepSeek run — 2026-11-26 (vehicle-analyzer: lint ratchet down)

Written by Claude for opencode/DeepSeek. Run the tasks in order without asking between them. Commit
after every task (Conventional Commits, `AI-Agent: opencode/<model>` trailer) and push after every
commit. If a task is blocked, write why in the log's *For Claude* section and go on. **Never merge a
PR.**

| Task | Repo | Branch (from an up-to-date `main`) | Zone |
|---|---|---|---|
| L1-0 (first!) and L1-4 | vehicle-workspace `external-ai/log/` | `ext/opencode-analyzer-lint-log` | green |
| L1-1 ... L1-3 | vehicle-analyzer | `ext/opencode-analyzer-lint` | green; `package.json` is **yellow** (the `--max-warnings` number lives there: PR body starts with `needs-claude-review`). **Red, never touch:** `src/services/webSerialCan*`, `src/services/udsComposer*`, `src-tauri/*`, `external/*`, `.github/*`, `CLAUDE.md`, `AGENTS.md` |

## 0. Before you start

Read only: `AGENTS.md` (workspace root), `vehicle-analyzer/CLAUDE.md`, `vehicle-analyzer/README.md`
(scripts section), `vehicle-analyzer/eslint.config.*`.

**Why.** `npm run lint` runs `eslint . --max-warnings 302` (a ratchet from T33). Every warning removed
lets the ratchet go down; the goal is **≤ 150** without disabling rules.

## Hard rules

- Never add `eslint-disable` comments, never weaken a rule in the eslint config, never change
  behaviour. Fix the code: types instead of `any`, missing dependency arrays explained or fixed,
  unused variables removed, etc.
- Keep every test green: `npm ci && npm run typecheck` (if present) `&& npm run lint && npm test`
  (mirror `.github/workflows/` exactly, including coverage floors and the UI tests if CI runs them).
- Small commits by warning category; do not touch red files even if they have warnings (list them in
  *For Claude*).

## Tasks

- **L1-0** Log from `external-ai/log/TEMPLATE.md` as `external-ai/log/2026-11-26-opencode-analyzer-lint.md`;
  record the starting warning count per rule (`npx eslint . -f json` summarised).
- **L1-1** Fix warnings rule by rule, largest count first, in green files only.
- **L1-2** Lower `--max-warnings` in `package.json` to the new count (yellow).
- **L1-3** Run the full CI list locally; open the PR with `gh pr create -R vehicle-platform/vehicle-analyzer`,
  body starting with `needs-claude-review`, listing before/after counts per rule.
- **L1-4** Fill the log (counts, red files skipped, *For Claude*), commit, push.

Run `python3 scripts/check_zones.py vehicle-analyzer --base origin/main` before every push.
