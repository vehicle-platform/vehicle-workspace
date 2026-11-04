# CLAUDE.md — vehicle-workspace (workspace root)

@PLATFORM-RULES.md

This folder is the `vehicle-workspace` repo (manifest, setup, shared `.claude/`). It ignores the 12 independent platform repos cloned inside it (D-015). Locally, **always start Claude from this root** so every repo and the shared agents/skills are available. Each repo also carries synced copies of its relevant agents/skills and of `PLATFORM-RULES.md` for single-repo cloud sessions.

## Session protocol

1. At session start read `STATUS.md` (short). Do NOT read the large docs. Also run `grep -l '^review: pending' external-ai/log/*.md`: pending work by other AI tools → tell the user and offer `/external-review` (D-071).
2. Architecture: `vehicle-defs/docs/ARCHITECTURE.md` + `DECISIONS.md` first. For details, use the `docs/README.md` index or the `docs-researcher` agent.
3. Broad code search → `Explore` agent. Single file/symbol → Grep/Read directly.
4. One session = one task. When done, run `/handoff` to update `STATUS.md` and suggest `/clear`.
5. Keep Opus for architecture and safety judgment. Bulk work goes to `sonnet`/`haiku` subagents.

## Shared Claude assets (source of truth here)

- `PLATFORM-RULES.md`, `.claude/agents/`, `.claude/skills/` are the **only** place to edit these. After editing, run `python3 scripts/sync_claude.py` to copy them into each repo's `.claude/`, then commit in the affected repos. `--check` reports drift without writing.
- Which repo receives which agent/skill is defined in `scripts/sync_claude.py` (`REPO_ASSETS`).

| Agent | Model | Use |
|---|---|---|
| `docs-researcher` | haiku | Answers questions from the docs without loading them into the main context |
| `vss-schema-guardian` | haiku | Detects hardcoded CAN IDs/signals/VSS paths, checks the defs submodule pin |
| `architecture-guard` | sonnet | Checks repo scope, layering, dependency direction, bus rules and decisions |
| `safety-reviewer` | opus | ISO 26262/MISRA-aware review of safety-critical changes |
| `hil-scenario-validator` | haiku | Repo-owned by vehicle-hil-bench (not synced): checks HIL scenario YAML against the schema and vehicle independence |

## Other AI tools (D-071)

- The user also develops with non-Claude tools to save tokens. They read `AGENTS.md` / `GEMINI.md` (rendered by `scripts/sync_claude.py` from `external-ai/AGENTS.base.md`, `external-ai/zones.json` and `PLATFORM-RULES.md`; never edit the rendered files), work on `ext/<tool>-<topic>` branches with an `AI-Agent:` commit trailer, and log each session in `external-ai/log/` with `review: pending`.
- Zones: red = Claude only, yellow = Claude reviews before the user merges, green = free. `python3 scripts/check_zones.py <repo>` classifies a diff. Changing a zone or the base text is a Claude edit here, followed by the sync.
- `/external-review` (workspace skill) reviews, fixes and refactors their work and closes the logs.

## Worktrees

- Code changes happen in `<repo>/.claude/worktrees/<topic>` on branch `claude/<topic>` (one worktree per PR). `.claude/worktrees/` is ignored (workspace `.gitignore`; each repo's `.git/info/exclude`, added by the script below).
- `python3 scripts/worktrees.py` writes `WORKTREES.md` (generated, gitignored): every worktree of the workspace and the 12 repos with its PR state and a verdict. **remove** = merged, clean (submodules included) and nothing unpushed.
- **VS Code / GitLens visibility:** after creating, switching or removing a worktree or branch, run `python3 scripts/vscode_workspace.py`. It writes `vehicle-platform.code-workspace` (generated, gitignored): the workspace, the 12 repos and every worktree as VS Code folders, agent work first (🤖 `claude/*`, 🐋 `ext/opencode-*`/`ext/deepseek-*`, ✳️ other `ext/*`), so Source Control and GitLens see it. Commit authors carry the agent too (user-level `includeIf "onbranch:..."` in `~/.gitconfig`: `Alihan [Claude]`, `Alihan [DeepSeek]`; the email stays the user's, so GitHub still credits the account).
- After a PR is merged: `python3 scripts/worktrees.py --prune` removes the **remove** rows and their local branches. `/handoff` runs the report and asks before pruning.
