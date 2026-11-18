import chess
import time

from engine.config import MATE_SCORE, INF, PIECE_VALUES, MAX_DEPTH
from engine.evaluation import evaluate

class SearchTimeout(Exception):
    pass

class Search:
    def __init__(self, time_limit: float, evaluate_fn = evaluate):
        self.deadline = time.perf_counter() + time_limit
        self.evaluate = evaluate_fn
        self.nodes = 0

    def _check_time(self):
        self.nodes += 1
        
        if self.nodes % 1024 == 0 and time.perf_counter() > self.deadline:
            raise SearchTimeout

    def negamax(self, board: chess.Board, depth: int, ply: int, alpha: int, beta: int) -> int:
        """Returns the score of the position for the side to move."""

        self._check_time()

        if ply >= MAX_DEPTH:
            return self.evaluate(board)

        if board.is_checkmate():
            return -MATE_SCORE + ply

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        if board.is_repetition(2):
            return 0

        if board.is_check():
            depth += 1

        if depth == 0:
            return self.quiescence(board, ply, alpha, beta)

        best_score = -INF

        for move in order_moves(board, board.legal_moves):
            board.push(move)
            best_score = max(best_score, -self.negamax(board, depth - 1, ply + 1, -beta, -alpha))
            board.pop()

            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score

    def quiescence(self, board: chess.Board, ply: int, alpha: int, beta: int) -> int:
        """Look at capture moves to prevent blunders due to the horizon effect"""

        self._check_time()
        in_check = board.is_check()

        if in_check:
            best_score = -INF
            moves = board.legal_moves

        else:
            stand_pat = self.evaluate(board)

            if stand_pat >= beta:
                return stand_pat

            best_score = stand_pat
            alpha = max(alpha, stand_pat)
            moves = board.generate_legal_captures()

        for move in order_moves(board, moves):
            board.push(move)
            score = -self.quiescence(board, ply + 1, -beta, -alpha)
            board.pop()

            if score > best_score:
                best_score = score

            if score > alpha:
                alpha = score

            if alpha >= beta:
                break

        if in_check and best_score == -INF:
            return -MATE_SCORE + ply

        return best_score

    def find_best_move(self, board: chess.Board, depth: int, first_move: chess.Move | None = None) -> tuple[chess.Move | None, int]:
        """Returns the best move in the current position."""

        best_score = -INF
        best_move = None

        moves = order_moves(board, board.legal_moves)

        if first_move in moves:
            moves.remove(first_move)
            moves.insert(0, first_move)

        for move in moves:        
            board.push(move)
            score = -self.negamax(board, depth - 1, 1, -INF, -best_score)

            if score > best_score:
                best_move = move
                best_score = score

            board.pop()

        return (best_move, best_score)

def move_score(board: chess.Board, move: chess.Move) -> int:
    """Ordering score for a single move: higher means search it earlier"""

    score = 0
    
    if board.is_capture(move):
        if board.is_en_passant(move):
            attacker = chess.PAWN
            victim = chess.PAWN

        else:
            attacker = board.piece_type_at(move.from_square)
            victim = board.piece_type_at(move.to_square)
        
        score = 10 * PIECE_VALUES[victim] - PIECE_VALUES.get(attacker, 0) # assigning value 0 if attacker is the king

    if move.promotion is not None:
        score += 2 * PIECE_VALUES[move.promotion]

    return score

def order_moves(board: chess.Board, moves) -> list[chess.Move]:
    """Orders moves based on the MVV-LVA principle"""

    return sorted(moves, key = lambda move: move_score(board, move), reverse = True)