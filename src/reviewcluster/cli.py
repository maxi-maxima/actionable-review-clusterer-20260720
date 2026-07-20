from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import load_comments, summarize_comments, to_json_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cluster review comments into actionable buckets.")
    parser.add_argument("input", nargs="?", help="Path to a JSON file of review comments. Reads stdin if omitted.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    comments = load_comments(raw)
    if args.json:
        print(json.dumps(to_json_summary(comments), indent=2, ensure_ascii=False))
    else:
        print(summarize_comments(comments), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
