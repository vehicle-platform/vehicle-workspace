#!/usr/bin/env python3
"""Pin third-party GitHub Actions to full commit SHAs (QUALITY CI-1, T24).

Usage: python3 scripts/pin_actions.py <repo-dir> [<repo-dir> ...]

Rewrites `uses: owner/repo[/sub]@<tag>` in <repo>/.github/workflows/*.yml to
`@<sha> # vX.Y.Z` using the PINS table below, adds `persist-credentials: false`
to actions/checkout steps and an explicit `toolchain: stable` to
dtolnay/rust-toolchain steps that relied on the `@stable` ref name.
Idempotent. Add a row to PINS to introduce a new action (resolve the SHA with
`gh api repos/<owner>/<repo>/git/ref/tags/<tag>`; dereference annotated tags).
Renovate (renovate-config/) keeps the pins fresh afterwards.
"""
import re
import sys
from pathlib import Path

# (action, ref as written in workflows) -> (sha, comment)
PINS = {
    ("actions/checkout", "v4"): ("11d5960a326750d5838078e36cf38b85af677262", "v4.4.0"),
    ("actions/cache", "v4"): ("0057852bfaa89a56745cba8c7296529d2fc39830", "v4.3.0"),
    ("actions/setup-java", "v4"): ("cf277c60eb25467037889841efdb72551f06f6c3", "v4.9.1"),
    ("actions/setup-node", "v4"): ("49933ea5288caeca8642d1e84afbd3f7d6820020", "v4.4.0"),
    ("actions/setup-python", "v5"): ("a26af69be951a213d495a4c3e4e4022e16d87065", "v5.6.0"),
    ("actions/upload-artifact", "v4"): ("ea165f8d65b6e75b540449e92b4886f43607fa02", "v4.6.2"),
    ("astral-sh/setup-uv", "v3"): ("caf0cab7a618c569241d31dcd442f54681755d39", "v3.2.4"),
    ("astral-sh/setup-uv", "v6"): ("d0cc045d04ccac9d8b7881df0226f9e82c39688e", "v6.8.0"),
    ("subosito/flutter-action", "v2"): ("1a449444c387b1966244ae4d4f8c696479add0b2", "v2.23.0"),
    ("Swatinem/rust-cache", "v2"): ("d1527c8f67ef9af357290475d4af4b0fab8f12e0", "v2.9.3"),
    ("dtolnay/rust-toolchain", "stable"): ("39008827e6b4319a349e9a42dfc90579dd25f1ca", "stable"),
}
SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^(?P<indent>\s*)(?P<dash>-\s+)?uses:\s+(?P<act>[^@\s]+)@(?P<ref>\S+)(?:\s+#.*)?$")


def process(text: str, name: str) -> str:
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = USES.match(line)
        if not m or m["act"].startswith(("./", "docker://")):
            out.append(line)
            i += 1
            continue
        act, ref = m["act"], m["ref"]
        base = "/".join(act.split("/")[:2])
        if SHA.match(ref):
            # already pinned: keep the line and the existing comment
            out.append(line)
        else:
            pin = PINS.get((base, ref))
            if not pin:
                print(f"{name}: UNKNOWN action {act}@{ref}", file=sys.stderr)
                out.append(line)
                i += 1
                continue
            out.append(f"{m['indent']}{m['dash'] or ''}uses: {act}@{pin[0]} # {pin[1]}")
        # collect the `with:` block (if any) directly under this step
        key_col = len(m["indent"]) + len(m["dash"] or "")
        k = i + 1
        kcol = " " * key_col
        if k < len(lines) and lines[k].startswith(kcol + "with:"):
            blk_end = k + 1
            while blk_end < len(lines) and lines[blk_end].startswith(kcol + "  ") and lines[blk_end].strip():
                blk_end += 1
            body = lines[k:blk_end]
            extra = []
            joined = "\n".join(body)
            if base == "actions/checkout" and "persist-credentials" not in joined:
                extra.append(f"{kcol}  persist-credentials: false")
            if base == "dtolnay/rust-toolchain" and "toolchain:" not in joined:
                extra.append(f"{kcol}  toolchain: stable")
            out.extend(body + extra)
            i = blk_end
            continue
        extra = []
        if base == "actions/checkout":
            extra = [f"{kcol}with:", f"{kcol}  persist-credentials: false"]
        elif base == "dtolnay/rust-toolchain":
            extra = [f"{kcol}with:", f"{kcol}  toolchain: stable"]
        out.extend(extra)
        i += 1
    return "\n".join(out)


def main() -> int:
    for repo in sys.argv[1:]:
        for wf in sorted(Path(repo, ".github", "workflows").glob("*.y*ml")):
            old = wf.read_text()
            new = process(old, str(wf))
            if new != old:
                wf.write_text(new)
                print(f"updated {wf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
