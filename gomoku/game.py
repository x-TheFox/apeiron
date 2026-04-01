"""CLI game loop for the Gomoku AI.

Match format
------------
Best-of-many: first player to win TARGET_WINS games wins the match.
Colors alternate each game so neither side keeps a permanent first-player
advantage.

Usage
-----
Run via play.py at the project root, or directly:
    python -m gomoku.game
"""

from __future__ import annotations

import sys
import time

from .board import Board
from .agent import Agent

TARGET_WINS = 5          # wins needed to claim the match
DEFAULT_DEPTH = 4        # AI search depth (increase for stronger play)

_SYMBOLS  = {Board.BLACK: "X", Board.WHITE: "O"}
_NAMES    = {Board.BLACK: "Black (X)", Board.WHITE: "White (O)"}


# ── Human input ───────────────────────────────────────────────────────────────

def _prompt_move(board: Board, player: int) -> tuple[int, int]:
    """Ask the human for a move; loop until valid input is given."""
    sym = _SYMBOLS[player]
    while True:
        raw = input(f"  Your move ({sym}) [row col / q]: ").strip()
        if raw.lower() in ("q", "quit"):
            print("\n  Goodbye!")
            sys.exit(0)
        parts = raw.split()
        if len(parts) != 2:
            print("  Enter two integers separated by a space, e.g.  0 0  or  -3 5")
            continue
        try:
            r, c = int(parts[0]), int(parts[1])
        except ValueError:
            print("  Both values must be integers.")
            continue
        if (r, c) in board.stones:
            print(f"  ({r}, {c}) is already occupied — pick a different cell.")
            continue
        return r, c


# ── Single-game loop ──────────────────────────────────────────────────────────

def play_one_game(
    human_player: int,
    ai_depth: int = DEFAULT_DEPTH,
) -> int:
    """Play a single game of Gomoku.

    Parameters
    ----------
    human_player:
        Which colour the human controls for this game (Board.BLACK or Board.WHITE).
    ai_depth:
        Minimax search depth for the AI.

    Returns
    -------
    The winning player constant (Board.BLACK or Board.WHITE).
    """
    ai_player = 3 - human_player
    agent     = Agent(player=ai_player, depth=ai_depth)
    board     = Board()
    current   = Board.BLACK   # Black always moves first

    print()
    print("  ┌─────────────────────────────────────┐")
    print(f"  │  You are {_NAMES[human_player]:<27}│")
    print(f"  │  AI  is  {_NAMES[ai_player]:<27}│")
    print("  │  Black (X) goes first.              │")
    print("  └─────────────────────────────────────┘")
    print()

    while True:
        board.display()

        if current == human_player:
            move = _prompt_move(board, current)
        else:
            print(f"  AI ({_SYMBOLS[ai_player]}) is thinking…", end="", flush=True)
            t0   = time.perf_counter()
            move = agent.get_best_move(board)
            dt   = time.perf_counter() - t0
            r, c = move
            print(f"\r  AI ({_SYMBOLS[ai_player]}) plays ({r:+d}, {c:+d})  [{dt:.2f} s]")

        r, c = move
        board.place_stone(r, c, current)

        winner = board.check_winner(r, c)
        if winner:
            board.display()
            who = "You win!" if winner == human_player else "AI wins!"
            print(f"  *** {who}  ({_NAMES[winner]}) ***")
            print()
            return winner

        current = Board.WHITE if current == Board.BLACK else Board.BLACK


# ── Match loop ────────────────────────────────────────────────────────────────

def run_match(
    human_first_color: int,
    ai_depth: int = DEFAULT_DEPTH,
    target: int = TARGET_WINS,
) -> None:
    """Run a first-to-*target* match between the human and the AI."""
    scores = {Board.BLACK: 0, Board.WHITE: 0}
    game_num = 0

    # Determine which colour the human starts with.
    human_color = human_first_color

    while max(scores.values()) < target:
        game_num += 1
        ai_color  = 3 - human_color

        print(f"\n  ── Game {game_num} ──")
        print(f"  Score  You: {scores[human_first_color]}  AI: {scores[3-human_first_color]}  "
              f"(first to {target})")

        winner = play_one_game(human_color, ai_depth)
        scores[winner] += 1

        print(f"  Updated score  You: {scores[human_first_color]}  "
              f"AI: {scores[3-human_first_color]}")

        if max(scores.values()) >= target:
            break

        # Prompt for next game
        again = input("\n  Play next game? [Y/n]: ").strip().lower()
        if again in ("n", "no"):
            break

        # Swap colours for the next game so neither side permanently benefits
        # from the first-player advantage.
        human_color = 3 - human_color

    # Final result
    print()
    print("  ═══════════════════════════════")
    if scores[human_first_color] >= target:
        print("  Congratulations!  You won the match!")
    elif scores[3 - human_first_color] >= target:
        print("  The AI won the match. Better luck next time!")
    else:
        print("  Match ended early.")
    print(f"  Final score  You: {scores[human_first_color]}   "
          f"AI: {scores[3-human_first_color]}")
    print("  ═══════════════════════════════")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main(ai_depth: int = DEFAULT_DEPTH) -> None:
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║   GOMOKU  —  Five-in-a-Row               ║")
    print("  ║   Infinite board  ·  First to 5 wins      ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()
    print("  Rules:")
    print("    • Place stones alternately on an infinite grid.")
    print("    • First to get 5 (or more) in a row wins the game.")
    print("    • Win 5 games to claim the match.")
    print()
    print("  Coordinates:")
    print("    Enter moves as  row col  (any integers, e.g. '0 0', '-2 3').")
    print("    Type 'q' at any prompt to quit.")
    print()

    # Colour selection
    while True:
        choice = input("  Play as Black (X, goes first)? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            human_color = Board.BLACK
            break
        if choice in ("n", "no"):
            human_color = Board.WHITE
            break
        print("  Please enter Y or N.")

    run_match(human_color, ai_depth)


if __name__ == "__main__":
    main()
