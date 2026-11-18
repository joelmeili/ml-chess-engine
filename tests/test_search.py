import chess
import pytest

from engine.config import INF
from engine.search import Search

BACK_RANK_MATE = "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1"
FREE_QUEEN = "4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1"
DEFENDED_ROOK = "3rk3/8/8/8/8/8/8/3QK3 w - - 0 1"
WHITE_IS_CHECKMATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"

def make_search() -> Search:
    return Search(time_limit = 60)

@pytest.mark.parametrize("depth", [1, 2, 3])
def test_finds_mate_in_one(depth):
    board = chess.Board(BACK_RANK_MATE)
    assert make_search().find_best_move(board, depth)[0] == chess.Move.from_uci("d1d8")

@pytest.mark.parametrize("depth", [1, 2])
def test_captures_free_queen(depth):
    board = chess.Board(FREE_QUEEN)
    assert make_search().find_best_move(board, depth)[0] == chess.Move.from_uci("d1d5")

@pytest.mark.parametrize("depth", [1, 2])
def test_avoids_defended_rook(depth):
    board = chess.Board(DEFENDED_ROOK)
    assert make_search().find_best_move(board, depth)[0] != chess.Move.from_uci("d1d8")

def test_quiescence_sees_recapture():
    board = chess.Board(DEFENDED_ROOK)
    score = make_search().negamax(board, 1, 0, -INF, INF)
    assert 300 < score < 500

def test_search_leaves_board_unchanged():
    board = chess.Board(DEFENDED_ROOK)
    fen_before = board.fen()
    make_search().find_best_move(board, 2)[0]
    assert board.fen() == fen_before

def test_returns_none_when_no_legal_moves():
    board = chess.Board(WHITE_IS_CHECKMATED)
    assert make_search().find_best_move(board, 1)[0] is None

def test_repeated_position_scores_as_draw():
    board = chess.Board()
    for move in "Nf3 Nf6 Ng1 Ng8".split():
        board.push_san(move)
    assert make_search().negamax(board, 2, 1, -INF, INF) == 0