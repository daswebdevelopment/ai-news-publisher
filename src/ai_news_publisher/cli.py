from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .pipeline import generate_markdown_digest, normalize_items


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an AI news markdown digest from JSON input.")
    parser.add_argument("input", type=Path, help="Path to JSON file containing a list of news item objects")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("digest.md"),
        help="Output markdown file path (default: digest.md)",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        raw_text = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading input file '{args.input}': {exc}", file=sys.stderr)
        return 1

    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"Error parsing JSON in '{args.input}': {exc}", file=sys.stderr)
        return 1

    if not isinstance(raw, list):
        print("Input JSON must be a list of item objects", file=sys.stderr)
        return 1

    try:
        items = normalize_items(raw)
    except ValueError as exc:
        print(f"Invalid news item data: {exc}", file=sys.stderr)
        return 1

    digest = generate_markdown_digest(items)
    try:
        args.output.write_text(digest, encoding="utf-8")
    except OSError as exc:
        print(f"Error writing output file '{args.output}': {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(items)} normalized stories to {args.output}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
