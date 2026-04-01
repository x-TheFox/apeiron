"""Pattern-based board evaluation for Gomoku.

Scanning strategy
-----------------
For every stone on the board we scan along each of the 4 axis-directions.
To avoid counting a run more than once we only start counting from the
*canonical start* of every run — the cell whose predecessor in that direction
is NOT the same colour.

Run classification (length L, open_ends O)
-------------------------------------------
open_ends == 0 and L < 5 → 0     (completely blocked, useless)
L >= 5                   → FIVE
L == 4, O == 2           → OPEN_FOUR  (_XXXX_ — two winning threats; unstoppable)
L == 4, O == 1           → FOUR       (one threat to complete to win)
L == 3, O == 2           → OPEN_THREE (_XXX_ — will become open-four if unblocked)
L == 3, O == 1           → THREE
L == 2, O == 2           → OPEN_TWO
L == 2, O == 1           → TWO
L == 1, O == 2           → ONE

Defensive bias
--------------
Opponent threats are multiplied by 1.1 so the AI prefers blocking over
extending its own position when the heuristic values are otherwise equal.
"""

from __future__ import annotations

from .board import Board

# ── Score table ───────────────────────────────────────────────────────────────

FIVE       = 100_000_000
OPEN_FOUR  =  10_000_000
FOUR       =   1_000_000
OPEN_THREE =     100_000
THREE      =      10_000
OPEN_TWO   =       1_000
TWO        =         100
ONE        =          10

_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

_DEFENSIVE_BIAS = 1.1   # multiplier on opponent score


def _score_run(length: int, open_ends: int) -> int:
    if length >= 5:
        return FIVE
    if open_ends == 0:
        return 0  # completely blocked — no value
    if length == 4:
        return OPEN_FOUR if open_ends == 2 else FOUR
    if length == 3:
        return OPEN_THREE if open_ends == 2 else THREE
    if length == 2:
        return OPEN_TWO if open_ends == 2 else TWO
    # length == 1
    return ONE if open_ends == 2 else 0


def evaluate(board: Board, ai_player: int) -> int:
    """Return a signed score for *ai_player*.

    Positive  → position is better for the AI.
    Negative  → position is better for the opponent.
    """
    opponent  = 3 - ai_player
    ai_score  = 0
    opp_score = 0

    stones = board.stones  # local reference for speed

    for (r, c), player in stones.items():
        for dr, dc in _DIRECTIONS:
            # Only process the canonical start of each run
            if stones.get((r - dr, c - dc)) == player:
                continue  # skip; a prior cell starts this run

            # Count consecutive stones of the same colour
            length = 0
            nr, nc = r, c
            while stones.get((nr, nc)) == player:
                length += 1
                nr, nc = nr + dr, nc + dc

            # (nr, nc) is the first cell beyond the run (forward end)
            # (r - dr, r - dc) is the cell before the run (backward end)
            right_open = (nr, nc) not in stones
            left_open  = (r - dr, c - dc) not in stones
            open_ends  = int(right_open) + int(left_open)

            s = _score_run(length, open_ends)
            if player == ai_player:
                ai_score  += s
            else:
                opp_score += s

    return ai_score - int(opp_score * _DEFENSIVE_BIAS)
