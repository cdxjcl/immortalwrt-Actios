#!/usr/bin/env python3
"""Drop the obsolete tc_depth context line from TurboACC's 953 patch.

Linux 6.12.85 and 6.18.60 no longer have the ``tc_depth`` bitfield in
struct sk_buff.  TurboACC's Shortcut-FE patch still lists it as context,
so the hunk no longer applies.  Removing that one context line and
decrementing the hunk counts keeps the fast_forwarded field insertion.
"""

import re
import sys
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)$")


def fix_patch(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if "tc_depth:2" not in line or not line.startswith(" "):
            continue

        hunk_index = index - 1
        while hunk_index >= 0 and not lines[hunk_index].startswith("@@ "):
            hunk_index -= 1
        if hunk_index < 0:
            continue

        match = HUNK_RE.match(lines[hunk_index])
        if not match:
            continue

        old_start, old_count, new_start, new_count = (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4)),
        )
        lines[hunk_index] = (
            f"@@ -{old_start},{old_count - 1} "
            f"+{new_start},{new_count - 1} @@{match.group(5)}"
        )
        del lines[index]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True

    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: fix_turboacc_953.py <patch> [...]", file=sys.stderr)
        return 2

    for name in sys.argv[1:]:
        patch = Path(name)
        if not patch.is_file():
            print(f"skip missing patch: {patch}")
            continue
        if fix_patch(patch):
            print(f"fixed tc_depth context: {patch}")
        else:
            print(f"no tc_depth context found: {patch}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
