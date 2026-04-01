#!/usr/bin/env python3
"""Entry point — run this file to start a match against the AI.

Usage
-----
    python play.py           # default depth 4
    python play.py --depth 6 # stronger AI (slower)
"""

import argparse
from gomoku.game import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gomoku AI — Five-in-a-Row on an infinite board")
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=4,
        metavar="N",
        help="Minimax search depth (default: 4). Higher = stronger but slower.",
    )
    args = parser.parse_args()
    main(ai_depth=args.depth)
