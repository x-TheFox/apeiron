"""Sparse, infinite Gomoku board.

Player constants
----------------
Board.BLACK = 1  (X, moves first)
Board.WHITE = 2  (O)
"""

from __future__ import annotations

_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class Board:
    BLACK = 1
    WHITE = 2

    def __init__(self) -> None:
        # Maps (row, col) -> player (1 or 2).  Missing keys are empty cells.
        self.stones: dict[tuple[int, int], int] = {}
        self.last_move: tuple[int, int] | None = None

    # ── Mutation ──────────────────────────────────────────────────────────────

    def place_stone(self, row: int, col: int, player: int) -> None:
        """Place *player*'s stone at (row, col).  Raises if already occupied."""
        if (row, col) in self.stones:
            raise ValueError(f"Cell ({row}, {col}) is already occupied.")
        if player not in (self.BLACK, self.WHITE):
            raise ValueError(f"Invalid player: {player}. Must be 1 (BLACK) or 2 (WHITE).")
        self.stones[(row, col)] = player
        self.last_move = (row, col)

    def remove_stone(self, row: int, col: int) -> None:
        """Remove the stone at (row, col).  Used by the AI for backtracking."""
        self.stones.pop((row, col), None)

    # ── Queries ───────────────────────────────────────────────────────────────

    def check_winner(self, row: int, col: int) -> int:
        """Return the winning player after a stone was placed at (row, col).

        Returns 0 if there is no winner yet.  Freestyle rules: >=5 in a row wins.
        The stone must already be present in self.stones.
        """
        player = self.stones.get((row, col))
        if player is None:
            return 0

        for dr, dc in _DIRECTIONS:
            count = 1

            # Count forward
            r, c = row + dr, col + dc
            while self.stones.get((r, c)) == player:
                count += 1
                r, c = r + dr, c + dc

            # Count backward
            r, c = row - dr, col - dc
            while self.stones.get((r, c)) == player:
                count += 1
                r, c = r - dr, c - dc

            if count >= 5:
                return player

        return 0

    def get_candidate_moves(self, radius: int = 2) -> list[tuple[int, int]]:
        """Return empty cells within *radius* of any placed stone.

        On an empty board returns [(0, 0)] so the AI always has at least one option.
        """
        if not self.stones:
            return [(0, 0)]

        seen: set[tuple[int, int]] = set()
        for r, c in self.stones:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    pos = (r + dr, c + dc)
                    if pos not in self.stones:
                        seen.add(pos)
        return list(seen)

    # ── Display ───────────────────────────────────────────────────────────────

    def display(self, margin: int = 1) -> None:
        """Pretty-print the occupied region plus a *margin* of empty cells."""
        if not self.stones:
            print("  (empty board)\n")
            return

        rows = [r for r, _ in self.stones]
        cols = [c for _, c in self.stones]
        min_r, max_r = min(rows) - margin, max(rows) + margin
        min_c, max_c = min(cols) - margin, max(cols) + margin

        # Width needed to display any coordinate label
        w = max(
            len(str(min_r)), len(str(max_r)),
            len(str(min_c)), len(str(max_c)),
        ) + 1

        # Column header row
        print(" " * w, end="")
        for c in range(min_c, max_c + 1):
            print(f"{c:>{w}}", end="")
        print()

        # Board rows
        for r in range(min_r, max_r + 1):
            print(f"{r:>{w}}", end="")
            for c in range(min_c, max_c + 1):
                p = self.stones.get((r, c))
                sym = "X" if p == self.BLACK else "O" if p == self.WHITE else "."
                print(f"{sym:>{w}}", end="")
            print()
        print()
