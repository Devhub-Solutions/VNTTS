#!/usr/bin/env python3
"""Split large model files into <=900MB chunks for git-friendly storage."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vntts.model_parts import split_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to source model file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write split parts (default: source directory)",
    )
    parser.add_argument(
        "--chunk-size-mb",
        type=int,
        default=900,
        help="Chunk size in MB (default: 900)",
    )
    parser.add_argument(
        "--keep-extension-prefix",
        action="store_true",
        help="Use <filename>.partN instead of <stem>.partN",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parts = split_file(
        source_file=args.source,
        output_dir=args.output_dir,
        chunk_size_mb=args.chunk_size_mb,
        use_stem_only=not args.keep_extension_prefix,
    )
    print(f"Created {len(parts)} part(s):")
    for p in parts:
        print(p)


if __name__ == "__main__":
    main()
