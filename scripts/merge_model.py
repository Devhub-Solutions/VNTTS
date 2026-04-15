#!/usr/bin/env python3
"""Merge model .part files into full ONNX models."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vntts.model_parts import merge_all_parts_in_dir, merge_parts_to_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        type=Path,
        help="Model directory to scan OR target model file to merge",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output when merging a single file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target.is_dir():
        merged = merge_all_parts_in_dir(args.target)
        if not merged:
            print("No missing models needed merging.")
            return
        print(f"Merged {len(merged)} file(s):")
        for p in merged:
            print(p)
        return

    merged = merge_parts_to_file(args.target, overwrite=args.overwrite)
    if merged is None:
        print(f"No merge performed for {args.target}")
    else:
        print(f"Merged: {merged}")


if __name__ == "__main__":
    main()
