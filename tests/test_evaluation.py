import chess
import pytest

from engine.evaluation import evaluate, material_score, piece_square_score

WHITE_UP_QUEEN_WHITE_TO_MOVE = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
WHITE_UP_QUEEN_BLACK_TO_MOVE = "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
KNIGHT_IN_CENTER = "4k3/8/8/8/3N4/8/8/4K3 w - - 0 1"
KNIGHT_ON_RIM = "4k3/8/8/8/8/8/N7/4K3 w - - 0 1"

def test_start_position_is_balanced():
    assert evaluate(chess.Board()) == 0

def test_material_advantage_for_side_to_move():
    assert material_score(chess.Board(WHITE_UP_QUEEN_WHITE_TO_MOVE)) == 900

def test_material_flips_with_side_to_move():
    assert material_score(chess.Board(WHITE_UP_QUEEN_BLACK_TO_MOVE)) == -900

def test_centralized_knight_scores_higher_than_rim_knight():
    center = piece_square_score(chess.Board(KNIGHT_IN_CENTER))
    rim = piece_square_score(chess.Board(KNIGHT_ON_RIM))
    assert center > rim

@pytest.mark.parametrize("fen", [
    WHITE_UP_QUEEN_WHITE_TO_MOVE,
    WHITE_UP_QUEEN_BLACK_TO_MOVE,
    KNIGHT_IN_CENTER,
    "4k3/8/8/8/8/8/4P3/R3K3 w Q - 0 1",
    "6k1/5ppp/8/8/8/8/5PPP/3R2K1 b - - 0 1",
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 4",
])
def test_evaluation_is_color_symmetric(fen):
    board = chess.Board(fen)
    assert evaluate(board) == evaluate(board.mirror())