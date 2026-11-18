import chess

from engine.config import MAX_DEPTH, MATE_SCORE
from engine.search import Search, SearchTimeout
from engine.evaluation import evaluate

def get_best_move(board: chess.Board, time_limit: float, evaluate_fn = evaluate) -> str | None:
    """Gets the best move from a chess position given a specific time limit"""
    board = board.copy()
    search = Search(time_limit, evaluate_fn)    
    depth = 1

    # asserting that depth 1 is always completed even when time limit is exceeded
    real_deadline = search.deadline
    search.deadline = float("inf")
    best_move, best_score = search.find_best_move(board, depth)
    search.deadline = real_deadline
    depth += 1

    while True:

        if best_move is None:
            break

        if abs(best_score) > MATE_SCORE - MAX_DEPTH:
            break

        if depth > MAX_DEPTH:
            break

        try:
            best_move, best_score = search.find_best_move(board, depth, best_move)
            depth += 1

        except SearchTimeout:
            break
    
    return best_move.uci() if best_move else None