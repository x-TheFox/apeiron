"""Unit tests for gomoku.agent — correctness of key tactical decisions."""

from gomoku.board import Board
from gomoku.agent import Agent


def _fill(board: Board, player: int, positions: list[tuple[int, int]]) -> None:
    for r, c in positions:
        board.place_stone(r, c, player)


def _agent(player: int, depth: int = 2) -> Agent:
    return Agent(player=player, depth=depth)


# ── Immediate wins ────────────────────────────────────────────────────────────

def test_completes_horizontal_five():
    """Agent must complete its own four-in-a-row to win."""
    b = Board()
    _fill(b, Board.BLACK, [(0, c) for c in range(4)])   # Black has 4 in a row
    b.place_stone(5, 5, Board.WHITE)                     # White elsewhere
    move = _agent(Board.BLACK).get_best_move(b)
    b.place_stone(*move, Board.BLACK)
    assert b.check_winner(*move) == Board.BLACK


def test_completes_vertical_five():
    b = Board()
    _fill(b, Board.WHITE, [(r, 3) for r in range(4)])
    b.place_stone(5, 5, Board.BLACK)
    move = _agent(Board.WHITE).get_best_move(b)
    b.place_stone(*move, Board.WHITE)
    assert b.check_winner(*move) == Board.WHITE


def test_completes_diagonal_five():
    b = Board()
    _fill(b, Board.BLACK, [(i, i) for i in range(4)])
    b.place_stone(10, 0, Board.WHITE)
    move = _agent(Board.BLACK).get_best_move(b)
    b.place_stone(*move, Board.BLACK)
    assert b.check_winner(*move) == Board.BLACK


def test_completes_anti_diagonal_five():
    b = Board()
    _fill(b, Board.WHITE, [(i, 4 - i) for i in range(4)])
    b.place_stone(10, 10, Board.BLACK)
    move = _agent(Board.WHITE).get_best_move(b)
    b.place_stone(*move, Board.WHITE)
    assert b.check_winner(*move) == Board.WHITE


# ── Immediate blocks ──────────────────────────────────────────────────────────

def test_blocks_horizontal_four():
    """Agent (Black) must block White's four-in-a-row."""
    b = Board()
    _fill(b, Board.WHITE, [(0, c) for c in range(4)])
    b.place_stone(5, 5, Board.BLACK)
    move = _agent(Board.BLACK).get_best_move(b)
    # Winning squares for White are (0, 4) and (0, -1)
    assert move in {(0, 4), (0, -1)}


def test_blocks_vertical_four():
    b = Board()
    _fill(b, Board.WHITE, [(r, 0) for r in range(4)])
    b.place_stone(5, 5, Board.BLACK)
    move = _agent(Board.BLACK).get_best_move(b)
    assert move in {(4, 0), (-1, 0)}


def test_blocks_diagonal_four():
    b = Board()
    _fill(b, Board.WHITE, [(i, i) for i in range(4)])
    b.place_stone(10, 0, Board.BLACK)
    move = _agent(Board.BLACK).get_best_move(b)
    assert move in {(4, 4), (-1, -1)}


# ── Win beats block ───────────────────────────────────────────────────────────

def test_wins_instead_of_blocks_when_both_available():
    """If the AI can win AND the opponent has a four, it should win first."""
    b = Board()
    # AI (Black) has four in a row
    _fill(b, Board.BLACK, [(0, c) for c in range(4)])
    # Opponent (White) also has four in a row at different location
    _fill(b, Board.WHITE, [(5, c) for c in range(4)])
    move = _agent(Board.BLACK).get_best_move(b)
    b.place_stone(*move, Board.BLACK)
    assert b.check_winner(*move) == Board.BLACK


# ── Move validity ─────────────────────────────────────────────────────────────

def test_never_plays_occupied_cell():
    b = Board()
    b.place_stone(0, 0, Board.BLACK)
    b.place_stone(0, 1, Board.WHITE)
    b.place_stone(1, 0, Board.BLACK)
    move = _agent(Board.WHITE).get_best_move(b)
    assert move not in b.stones


def test_first_move_on_empty_board():
    """AI must return a valid (integer, integer) move on an empty board."""
    b = Board()
    move = _agent(Board.BLACK).get_best_move(b)
    assert isinstance(move, tuple) and len(move) == 2
    assert all(isinstance(x, int) for x in move)


# ── Depth-4 tactical tests ────────────────────────────────────────────────────

def test_creates_open_four_threat(depth: int = 4):
    """At depth 4 the AI should create an open-four when no immediate
     win/block is needed, forcing the opponent to respond."""
    b = Board()
    # Black has an open three: . X X X .
    _fill(b, Board.BLACK, [(0, c) for c in (1, 2, 3)])
    b.place_stone(5, 5, Board.WHITE)
    agent = Agent(player=Board.BLACK, depth=depth)
    move = agent.get_best_move(b)
    b.place_stone(*move, Board.BLACK)
    # After the move Black should have at least a four-in-a-row
    from gomoku.evaluator import evaluate, FOUR as FOUR_SCORE
    score = evaluate(b, Board.BLACK)
    assert score >= FOUR_SCORE, f"Expected AI to create a four; score={score}"
