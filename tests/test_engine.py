import chess
import pytest
import time

from engine.engine import get_best_move

STARTING_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
BACK_RANK_MATE = "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1"
WHITE_IS_CHECKMATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"

def test_returns_legal_move_from_starting_position():
    board = chess.Board(STARTING_POSITION)
    move = get_best_move(board, 0.5)

    assert isinstance(move, str)
    assert chess.Move.from_uci(move) in board.legal_moves

def test_finds_mate_in_one():
    board = chess.Board(BACK_RANK_MATE)
    move = get_best_move(board, 0.5)

    assert isinstance(move, str)
    assert chess.Move.from_uci(move) == chess.Move.from_uci("d1d8")

def test_returns_none_when_no_legal_moves():
    board = chess.Board(WHITE_IS_CHECKMATED)
    assert get_best_move(board, 0.5) is None

@pytest.mark.parametrize("time_limit", [0.1, 0.5, 1.0])

def test_respects_time_limit(time_limit):
    board = chess.Board(STARTING_POSITION)
    start_time = time.perf_counter()
    get_best_move(board, time_limit)
    elapsed = time.perf_counter() - start_time
    assert elapsed < time_limit + 0.1

def test_returns_move_even_with_tiny_time_limit():
    board = chess.Board(STARTING_POSITION)
    move = get_best_move(board, 0.001)
    assert move is not None
    assert chess.Move.from_uci(move) in board.legal_moves

def test_does_not_modify_callers_board():
    board = chess.Board()
    get_best_move(board, 0.05)
    assert board.fen() == chess.STARTING_FEN
    assert len(board.move_stack) == 0