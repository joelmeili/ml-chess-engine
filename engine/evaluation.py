import chess

from engine.config import PIECE_VALUES, PIECE_SQUARE_TABLES

def material_score(board: chess.Board) -> int:
    """Score in centipawns from the side to move's perspective"""

    own_score = 0
    opponent_score = 0

    for piece_type, value in PIECE_VALUES.items():
        own_score += value * len(board.pieces(piece_type, board.turn))
        opponent_score += value * len(board.pieces(piece_type, not board.turn))

    return own_score - opponent_score

def piece_square_score(board: chess.Board) -> int:
    """Score in respect to the piece square table"""

    own_score = 0
    opponent_score = 0

    for square, piece in board.piece_map().items():
        if piece.color == chess.WHITE:
            index = chess.square_mirror(square)

        else:
            index = square

        if piece.color == board.turn:
            own_score += PIECE_SQUARE_TABLES[piece.piece_type][index]

        else:
            opponent_score += PIECE_SQUARE_TABLES[piece.piece_type][index]

    return own_score - opponent_score

def evaluate(board: chess.Board) -> int:
    """Evaluation of the position with respect to material and piece square value"""

    return material_score(board) + piece_square_score(board)