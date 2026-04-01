"""Gomoku AI agent.

Algorithm
---------
Minimax with alpha-beta pruning, depth-limited search.

Two levels of move ordering are used to maximise pruning efficiency:

  1. Winning moves first (complete 5-in-a-row).
  2. Blocking moves next (prevent opponent's 5-in-a-row).
  3. Remaining moves sorted by a fast proximity heuristic (cells adjacent to
     more existing stones are tried before cells far from the action).

At the root ``get_best_move`` additionally uses the full heuristic evaluator
to re-rank the candidates after the shortcut checks, giving stronger ordering
at the first ply where it matters most for pruning quality.

Candidate move set
------------------
Only cells within *radius* steps of any existing stone are considered.  On an
empty board the center (0, 0) is the sole candidate.  An optional
*max_candidates* cap keeps the search manageable on dense boards.

Depth / strength guide
-----------------------
  depth=2 — instant, handles obvious 1-move threats
  depth=4 — fast (<1 s), strong for casual play            [default]
  depth=6 — a few seconds per move, stronger mid-game tactics
"""

from __future__ import annotations

from .board import Board
from .evaluator import evaluate, FIVE

_INF = float("inf")
_WIN_SCORE  =  FIVE + 200   # returned for proven wins (offset by depth to prefer faster wins)
_LOSS_SCORE = -_WIN_SCORE


class Agent:
    """Gomoku AI agent.

    Parameters
    ----------
    player:
        The player this agent controls (``Board.BLACK`` = 1 or ``Board.WHITE`` = 2).
    depth:
        Minimax search depth in plies.  4 is the recommended default.
    max_candidates:
        Cap on the number of candidate moves considered per node.  Reducing
        this speeds up the search at some cost to quality.
    """

    def __init__(
        self,
        player: int,
        depth: int = 4,
        max_candidates: int = 20,
    ) -> None:
        self.player        = player
        self.opponent      = 3 - player
        self.depth         = depth
        self.max_candidates = max_candidates

    # ── Public API ────────────────────────────────────────────────────────────

    def get_best_move(self, board: Board) -> tuple[int, int]:
        """Return the best move for this agent given the current *board* state."""

        # Shortcut 1: win immediately if possible.
        win = self._find_immediate(board, self.player)
        if win is not None:
            return win

        # Shortcut 2: block opponent's immediate win.
        block = self._find_immediate(board, self.opponent)
        if block is not None:
            return block

        # Full alpha-beta search.
        candidates = self._order_root(board)
        if not candidates:
            # Fallback — should not happen in a real game.
            return board.get_candidate_moves()[0]

        best_move  = candidates[0]
        best_score = -_INF
        alpha      = -_INF
        beta       = _INF

        for move in candidates:
            r, c = move
            board.place_stone(r, c, self.player)
            score = self._minimax(board, self.depth - 1, alpha, beta, False)
            board.remove_stone(r, c)

            if score > best_score:
                best_score = score
                best_move  = move

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_move

    # ── Move ordering ─────────────────────────────────────────────────────────

    def _find_immediate(self, board: Board, player: int) -> tuple[int, int] | None:
        """Return any single move that immediately wins for *player*, or None."""
        for move in board.get_candidate_moves():
            r, c = move
            board.place_stone(r, c, player)
            winner = board.check_winner(r, c)
            board.remove_stone(r, c)
            if winner == player:
                return move
        return None

    def _order_root(self, board: Board) -> list[tuple[int, int]]:
        """Move ordering for the root ply.

        Wins first → blocks second → remaining sorted by full evaluation (most
        expensive but done once, at ply 1 only).
        """
        candidates = board.get_candidate_moves()
        wins, blocks, rest = [], [], []

        for move in candidates:
            r, c = move
            # Win?
            board.place_stone(r, c, self.player)
            if board.check_winner(r, c) == self.player:
                board.remove_stone(r, c)
                wins.append(move)
                continue
            board.remove_stone(r, c)
            # Block?
            board.place_stone(r, c, self.opponent)
            if board.check_winner(r, c) == self.opponent:
                board.remove_stone(r, c)
                blocks.append(move)
                continue
            board.remove_stone(r, c)
            rest.append(move)

        # Sort 'rest' by the full evaluation (higher = better for AI)
        def eval_move(m: tuple[int, int]) -> int:
            r, c = m
            board.place_stone(r, c, self.player)
            s = evaluate(board, self.player)
            board.remove_stone(r, c)
            return s

        rest.sort(key=eval_move, reverse=True)
        ordered = wins + blocks + rest
        return ordered[: self.max_candidates]

    def _order_fast(
        self,
        board: Board,
        candidates: list[tuple[int, int]],
        current_player: int,
    ) -> list[tuple[int, int]]:
        """Lightweight move ordering for interior tree nodes.

        Wins → blocks → proximity-score (counts nearby stones; O(25) per move).
        Caps total moves at *max_candidates* for speed.
        """
        opponent = 3 - current_player
        wins, blocks, rest = [], [], []

        for move in candidates:
            r, c = move
            board.place_stone(r, c, current_player)
            w = board.check_winner(r, c)
            board.remove_stone(r, c)
            if w == current_player:
                wins.append(move)
                continue

            board.place_stone(r, c, opponent)
            w = board.check_winner(r, c)
            board.remove_stone(r, c)
            if w == opponent:
                blocks.append(move)
                continue

            rest.append(move)

        rest.sort(key=lambda m: self._proximity(board, m), reverse=True)
        ordered = wins + blocks + rest
        return ordered[: self.max_candidates]

    def _proximity(self, board: Board, move: tuple[int, int]) -> int:
        """Score a move by how many existing stones are close to it.

        Closer stones contribute more (radius-1 → weight 2, radius-2 → weight 1).
        """
        r, c = move
        score = 0
        stones = board.stones
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                if (r + dr, c + dc) in stones:
                    dist = max(abs(dr), abs(dc))
                    score += 3 - dist   # dist 1 → 2 pts, dist 2 → 1 pt
        return score

    # ── Minimax ───────────────────────────────────────────────────────────────

    def _minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        current_player = self.player if maximizing else self.opponent

        if depth == 0:
            return float(evaluate(board, self.player))

        candidates = board.get_candidate_moves()
        if not candidates:
            return float(evaluate(board, self.player))

        ordered = self._order_fast(board, candidates, current_player)

        if maximizing:
            value = -_INF
            for move in ordered:
                r, c = move
                board.place_stone(r, c, current_player)
                winner = board.check_winner(r, c)
                if winner:
                    board.remove_stone(r, c)
                    # Return immediately — no need to search deeper.
                    return float(_WIN_SCORE + depth) if winner == self.player \
                           else float(_LOSS_SCORE - depth)

                child = self._minimax(board, depth - 1, alpha, beta, False)
                board.remove_stone(r, c)

                value = max(value, child)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        else:
            value = _INF
            for move in ordered:
                r, c = move
                board.place_stone(r, c, current_player)
                winner = board.check_winner(r, c)
                if winner:
                    board.remove_stone(r, c)
                    return float(_WIN_SCORE + depth) if winner == self.player \
                           else float(_LOSS_SCORE - depth)

                child = self._minimax(board, depth - 1, alpha, beta, True)
                board.remove_stone(r, c)

                value = min(value, child)
                beta  = min(beta, value)
                if beta <= alpha:
                    break
            return value
