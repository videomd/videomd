"""`videomd check DIR` and `videomd read DIR`."""
from __future__ import annotations

import argparse
import json
import sys

from . import VERSION, __version__, check, read


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="videomd", description="Check and read VIDEO.md packages.")
    ap.add_argument("--version", action="version", version=f"videomd {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check that each directory is a conforming VIDEO.md package")
    c.add_argument("dirs", nargs="+")
    r = sub.add_parser("read", help="print a package's card, timeline and shot data as JSON")
    r.add_argument("dir")
    args = ap.parse_args(argv)
    if args.cmd == "read":
        print(json.dumps(read(args.dir), ensure_ascii=False, indent=2))
        return 0
    bad = 0
    for d in args.dirs:
        errs = check(d)
        if errs:
            bad += 1
            print(f"{d}: does not conform")
            for e in errs:
                print(f"  {e}")
        else:
            print(f"{d}: conforms to VIDEO.md {VERSION}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
