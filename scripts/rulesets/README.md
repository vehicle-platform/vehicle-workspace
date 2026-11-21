# GitHub rulesets (D-120, provisional)

Applied 2026-11-21 to every public repo of the org with the GitHub API:

- `main.json` — `main-protection` on the default branch: PR required (0 approvals), no force-push or deletion, required checks `ci-ok`, `gitleaks`, `pin-check` from GitHub Actions (integration 15368). Admins bypass only through a PR.
- `main-no-ci.json` — the same without required checks, for repos without CI (vehicle-hil-bench, vehicle-io-node).
- `tags.json` — `release-tags` on `refs/tags/v*`: no deletion, update or force-move.

Apply to a new repo:

```bash
gh api -X POST repos/vehicle-platform/<repo>/rulesets --input scripts/rulesets/main.json
gh api -X POST repos/vehicle-platform/<repo>/rulesets --input scripts/rulesets/tags.json
```

Update an existing one: `gh api repos/vehicle-platform/<repo>/rulesets` for the id, then `gh api -X PUT repos/vehicle-platform/<repo>/rulesets/<id> --input ...`. Private repos need a paid plan for rulesets. Emergency merge: `gh pr merge --admin`.
