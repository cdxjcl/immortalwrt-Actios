#!/usr/bin/env python3
"""Rebase TurboACC firewall4 patch hunks for firewall4 2026-11-08."""

import sys
from pathlib import Path

FULLCONE_HEADER = "@@ -5,6 +5,10 @@ config defaults"
FULLCONE_BLOCK = [
    "@@ -5,5 +5,9 @@ config defaults",
    " \toption forward\t\tREJECT",
    "+\toption flow_offloading\t1",
    "+\toption flow_offloading_hw\t1",
    "+\toption fullcone\t\t1",
    "+\toption fullcone6\t0",
    " ",
    " config zone",
    " \toption name\t\tlan",
    " \tlist   network\t\t'lan'",
]

TCPCCA_HEADER = "@@ -5,6 +5,7 @@"
TCPCCA_BLOCK = [
    "@@ -9,4 +9,5 @@ config defaults",
    " \toption fullcone6\t0",
    "+\toption tcpcca\t\tcubic",
    " ",
    " config zone",
    " \toption name\t\tlan",
]


def adapt(path: Path, header: str, block: list[str]) -> None:
    if not path.is_file():
        print(f"skip missing patch: {path}")
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(header)
    except ValueError:
        print(f"hunk already adapted: {path}")
        return

    end = start + 1
    while end < len(lines) and not lines[end].startswith(("@@ ", "--- a/")):
        end += 1

    lines[start:end] = block
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"adapted: {path}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: fix_turboacc_firewall4.py <patch-dir>", file=sys.stderr)
        return 2

    patch_dir = Path(sys.argv[1])
    adapt(
        patch_dir / "001-firewall4-add-support-for-fullcone-nat.patch",
        FULLCONE_HEADER,
        FULLCONE_BLOCK,
    )
    adapt(
        patch_dir / "003-add-tcpcca-default-and-apply.patch",
        TCPCCA_HEADER,
        TCPCCA_BLOCK,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
