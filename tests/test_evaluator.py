"""Unit tests for gomoku.evaluator."""

from gomoku.board import Board
from gomoku.evaluator import (
    evaluate,
    FIVE, OPEN_FOUR, FOUR, OPEN_THREE, THREE, OPEN_TWO,
)


def _fill(board: Board, player: int, positions: list[tuple[int, int]]) -> None:
    for r, c in positions:
        board.place_stone(r, c, player)


# ── Basic sanity ──────────────────────────────────────────────────────────────

def test_empty_board_is_zero():
    assert evaluate(Board(), Board.BLACK) == 0


def test_score_from_black_perspective_positive_for_black():
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(3)])  # open three
    score = evaluate(b, Board.BLACK)
    assert score > 0


def test_score_from_white_perspective_positive_for_white():
    b = Board()
    _fill(b, Board.WHITE, [(0, c) for c in range(3)])
    score = evaluate(b, Board.WHITE)
    assert score > 0


# ── Five in a row ─────────────────────────────────────────────────────────────

def test_five_in_a_row_scores_FIVE_for_owner():
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(5)])
    assert evaluate(b, Board.BLACK) >= FIVE


def test_five_in_a_row_scores_negative_for_opponent():
    b = Board()
    _fill(b, Board.WHITE, [(0, c) for c in range(5)])
    assert evaluate(b, Board.BLACK) < 0


# ── Open four ─────────────────────────────────────────────────────────────────

def test_open_four_scores_at_least_OPEN_FOUR():
    """_XXXX_ — both ends open, score should reach OPEN_FOUR."""
    b = Board()
    # Cols 1-4 occupied, cols 0 and 5 empty → open four
    _fill(b, Board.BLACK, [(0, c) for c in range(1, 5)])
    score = evaluate(b, Board.BLACK)
    assert score >= OPEN_FOUR


def test_blocked_four_scores_less_than_open_four():
    """O XXXX _ — left end blocked → should score less than open four."""
    b = Board()
    b.place_stone(0, 0, Board.WHITE)                     # blocker
    _fill(b, Board.BLACK, [(0, c) for c in range(1, 5)])  # four in a row

    b2 = Board()
    _fill(b2, Board.BLACK, [(0, c) for c in range(1, 5)])  # open four

    assert evaluate(b, Board.BLACK) < evaluate(b2, Board.BLACK)


# ── Pattern ordering ──────────────────────────────────────────────────────────

def test_open_four_beats_open_three():
    """An open-four position is valued more than an open-three."""
    b_four = Board()
    _fill(b_four, Board.BLACK, [(0, c) for c in range(1, 5)])  # open four

    b_three = Board()
    _fill(b_three, Board.BLACK, [(0, c) for c in range(1, 4)])  # open three

    assert evaluate(b_four, Board.BLACK) > evaluate(b_three, Board.BLACK)


def test_open_three_beats_open_two():
    b_three = Board()
    _fill(b_three, Board.BLACK, [(0, c) for c in range(1, 4)])

    b_two = Board()
    _fill(b_two, Board.BLACK, [(0, c) for c in range(1, 3)])

    assert evaluate(b_three, Board.BLACK) > evaluate(b_two, Board.BLACK)


# ── Defensive bias ────────────────────────────────────────────────────────────

def test_opponent_threat_penalised_more_than_own_bonus():
    """Due to the 1.1x defensive bias, penalty for opponent open-three
    exceeds the bonus for our own equal open-three."""
    b_ours = Board()
    _fill(b_ours, Board.BLACK, [(0, c) for c in range(1, 4)])   # our open-3
    our_bonus = evaluate(b_ours, Board.BLACK)                    # positive

    b_theirs = Board()
    _fill(b_theirs, Board.WHITE, [(0, c) for c in range(1, 4)]) # their open-3
    their_penalty = evaluate(b_theirs, Board.BLACK)              # negative

    assert their_penalty < 0
    assert abs(their_penalty) > abs(our_bonus)


# ── Symmetric positions ───────────────────────────────────────────────────────

def test_symmetric_evaluate_both_positive():
    """evaluate(board_with_X_open_three, X) and
    evaluate(board_with_O_open_three, O) should both be positive."""
    b1 = Board()
    _fill(b1, Board.BLACK, [(0, c) for c in range(3)])
    assert evaluate(b1, Board.BLACK) > 0

    b2 = Board()
    _fill(b2, Board.WHITE, [(0, c) for c in range(3)])
    assert evaluate(b2, Board.WHITE) > 0


# ── Completely blocked runs ───────────────────────────────────────────────────

def test_fully_blocked_three_scores_zero_or_less():
    """_score_run(3, 0) — both ends blocked — must return 0."""
    from gomoku.evaluator import _score_run
    assert _score_run(3, 0) == 0

def test_blocked_three_scores_less_than_open_three():
    """O XXX _ evaluates lower for Black than _ XXX _."""
    b_blocked = Board()
    b_blocked.place_stone(0, 0, Board.WHITE)
    _fill(b_blocked, Board.BLACK, [(0, c) for c in range(1, 4)])
    blocked_score = evaluate(b_blocked, Board.BLACK)

    b_open = Board()
    _fill(b_open, Board.BLACK, [(0, c) for c in range(1, 4)])
    open_score = evaluate(b_open, Board.BLACK)

    assert open_score > blocked_score
