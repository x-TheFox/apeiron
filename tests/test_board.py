"""Unit tests for gomoku.board."""

import pytest
from gomoku.board import Board


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fill(board: Board, player: int, positions: list[tuple[int, int]]) -> None:
    for r, c in positions:
        board.place_stone(r, c, player)


# ── Placement ─────────────────────────────────────────────────────────────────

def test_place_and_retrieve():
    b = Board()
    b.place_stone(0, 0, Board.BLACK)
    assert b.stones[(0, 0)] == Board.BLACK


def test_double_place_raises():
    b = Board()
    b.place_stone(2, 3, Board.BLACK)
    with pytest.raises(ValueError):
        b.place_stone(2, 3, Board.WHITE)


def test_invalid_player_raises():
    b = Board()
    with pytest.raises(ValueError):
        b.place_stone(0, 0, 99)


def test_remove_stone():
    b = Board()
    b.place_stone(5, 5, Board.BLACK)
    b.remove_stone(5, 5)
    assert (5, 5) not in b.stones


def test_remove_nonexistent_is_silent():
    b = Board()
    b.remove_stone(99, 99)  # should not raise


# ── Win detection ─────────────────────────────────────────────────────────────

def test_no_winner_with_four():
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(4)])
    assert b.check_winner(0, 3) == 0


def test_horizontal_win_black():
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(5)])
    assert b.check_winner(0, 4) == Board.BLACK


def test_horizontal_win_white():
    b = Board()
    _fill(b, Board.WHITE, [(0, c) for c in range(5)])
    assert b.check_winner(0, 0) == Board.WHITE


def test_vertical_win():
    b = Board()
    _fill(b, Board.BLACK, [(r, 7) for r in range(5)])
    assert b.check_winner(4, 7) == Board.BLACK


def test_diagonal_down_right_win():
    b = Board()
    _fill(b, Board.BLACK, [(i, i) for i in range(5)])
    assert b.check_winner(4, 4) == Board.BLACK


def test_diagonal_down_left_win():
    b = Board()
    _fill(b, Board.WHITE, [(i, 4 - i) for i in range(5)])
    assert b.check_winner(4, 0) == Board.WHITE


def test_win_checked_from_middle_stone():
    """check_winner should return a winner even when called on a non-endpoint."""
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(5)])
    assert b.check_winner(0, 2) == Board.BLACK  # middle stone


def test_six_in_row_wins_freestyle():
    """Freestyle Gomoku: 6+ in a row is still a valid win."""
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(6)])
    assert b.check_winner(0, 5) == Board.BLACK


def test_large_offset_win():
    """Win detection works at negative or very large coordinates."""
    b = Board()
    _fill(b, Board.WHITE, [(-100, c) for c in range(-50, -45)])
    assert b.check_winner(-100, -46) == Board.WHITE


def test_no_win_for_missing_stone():
    b = Board()
    assert b.check_winner(0, 0) == 0   # cell empty


# ── Candidate moves ───────────────────────────────────────────────────────────

def test_candidates_empty_board():
    b = Board()
    assert b.get_candidate_moves() == [(0, 0)]


def test_candidates_at_radius_1():
    b = Board()
    b.place_stone(10, 10, Board.BLACK)
    moves = set(b.get_candidate_moves(radius=1))
    expected = {(r, c) for r in range(9, 12) for c in range(9, 12) if (r, c) != (10, 10)}
    assert expected == moves


def test_candidates_exclude_occupied():
    b = Board()
    b.place_stone(0, 0, Board.BLACK)
    b.place_stone(0, 1, Board.WHITE)
    for move in b.get_candidate_moves():
        assert move not in b.stones


def test_candidates_radius_2_superset_of_radius_1():
    b = Board()
    b.place_stone(5, 5, Board.BLACK)
    r1 = set(b.get_candidate_moves(radius=1))
    r2 = set(b.get_candidate_moves(radius=2))
    assert r1.issubset(r2)
    assert len(r2) > len(r1)
