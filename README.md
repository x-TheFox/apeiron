# Apeiron: Gomoku AI on an Infinite Board

An implementation of Gomoku (Five-in-a-Row) with:

- An infinite sparse board representation
- A command-line game loop for human vs AI play
- A minimax + alpha-beta AI agent with tactical move ordering
- A pattern-based board evaluator
- A pytest test suite covering board logic, evaluator behavior, and key AI tactics

## Features

- Infinite grid using sparse storage (`dict[(row, col)] -> player`)
- Freestyle Gomoku win condition (`>=5` in a row)
- Human vs AI match flow (first to 5 wins by default)
- Alternate colors between games to reduce first-player bias
- AI tactical shortcuts:
	- Immediate win detection
	- Immediate block detection
- Search optimizations:
	- Alpha-beta pruning
	- Candidate move generation around existing stones
	- Root and interior move ordering heuristics
- Pattern-based evaluation (open/closed runs, defensive bias)

## Project Structure

```text
.
├── play.py                  # CLI entry point
├── gomoku/
│   ├── board.py             # Board representation, move candidates, win detection
│   ├── evaluator.py         # Heuristic scoring for board states
│   ├── agent.py             # Minimax + alpha-beta AI
│   └── game.py              # Interactive match/game loop
├── tests/
│   ├── test_board.py        # Board unit tests
│   ├── test_evaluator.py    # Evaluator unit tests
│   └── test_agent.py        # AI tactical decision tests
└── conftest.py              # Test path setup
```

## Requirements

- Python 3.10+
- `pytest` for running tests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest
```

## Running the Game

From the repository root:

```bash
python play.py
```

Or directly through the package module:

```bash
python -m gomoku.game
```

### AI Depth

You can control AI strength via search depth:

```bash
python play.py --depth 4
python play.py --depth 6
```

Rough guide:

- `depth=2`: very fast, handles immediate tactics
- `depth=4`: strong default for normal play
- `depth=6`: stronger but noticeably slower per move

## How to Play

- Coordinates are integer pairs: `row col`
- Examples: `0 0`, `-2 3`, `10 -4`
- Black (`X`) moves first
- Enter `q` to quit

During a match:

- The game is played as first-to-5 wins (configurable in `gomoku/game.py`)
- Colors alternate each game

## Core Design

### 1. Board (`gomoku/board.py`)

- Uses a sparse dictionary for infinite-board scalability
- `place_stone` validates occupancy and player value
- `check_winner` scans 4 directions from last move:
	- horizontal
	- vertical
	- diagonal down-right
	- diagonal down-left
- `get_candidate_moves(radius=2)` only returns empty cells near existing stones
	- On empty board: returns `(0, 0)`

### 2. Evaluator (`gomoku/evaluator.py`)

The evaluator scores contiguous runs with open-end awareness:

- `FIVE`
- `OPEN_FOUR` vs `FOUR`
- `OPEN_THREE` vs `THREE`
- `OPEN_TWO`, `TWO`, `ONE`

Scoring is from the AI perspective:

`score = ai_score - int(opponent_score * 1.1)`

The `1.1` multiplier adds a defensive bias so the AI is more willing to block threats.

### 3. Agent (`gomoku/agent.py`)

Decision pipeline:

1. Play immediate winning move if available
2. Otherwise block opponent immediate winning move
3. Otherwise run depth-limited minimax with alpha-beta pruning

Move ordering strategy:

- At root:
	- winning moves
	- blocking moves
	- remaining moves sorted by full evaluator score
- In deeper nodes:
	- winning moves
	- blocking moves
	- remaining moves by fast local proximity heuristic

This ordering improves pruning quality and practical strength.

## Testing

Run all tests:

```bash
pytest -q
```

Run specific test modules:

```bash
pytest tests/test_board.py -q
pytest tests/test_evaluator.py -q
pytest tests/test_agent.py -q
```

What tests validate:

- Board placement/removal safety
- Win detection in all directions, including 6-in-a-row freestyle wins
- Candidate generation behavior on sparse infinite board
- Evaluator pattern ordering and defensive bias
- Agent tactical correctness (win-now, block-now, win-over-block priority)

## Configuration Notes

Primary knobs:

- `gomoku/game.py`
	- `TARGET_WINS` (default `5`)
	- `DEFAULT_DEPTH` (default `4`)
- `gomoku/agent.py`
	- `depth`
	- `max_candidates` (default `20`)

Increasing depth and candidates improves play but costs time.

## Development Tips

- Keep board operations reversible (`place_stone` / `remove_stone`) for search backtracking
- If AI gets slow in mid/late game:
	- lower depth
	- lower `max_candidates`
	- tighten candidate radius (with caution)

## License

No license file is currently included in this repository. Add one if you plan to distribute or open-source this project.
