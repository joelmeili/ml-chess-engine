import chess
import pytest

def perft(board: chess.Board, depth: int) -> int:
    if depth == 0:
        return 1

    nodes = 0

    for move in board.legal_moves:
        board.push(move)
        nodes += perft(board, depth - 1)
        board.pop()

    return nodes

@pytest.mark.parametrize("depth, expected", [
    (1, 20),
    (2, 400),
    (3, 8_902),
    (4, 197_281),
])

def test_perft_start_position(depth, expected):
    assert perft(chess.Board(), depth) == expected