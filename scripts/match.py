import chess
import chess.pgn
import random
import math

from engine.registry import ENGINES
from engine.engine import get_best_move

MAX_PLIES = 200

OPENINGS = {
    # e4 openings
    "Italian": "e4 e5 Nf3 Nc6 Bc4",
    "Spanish": "e4 e5 Nf3 Nc6 Bb5",
    "Caro-Kann": "e4 c6 d4 d5",
    "Sicilian": "e4 c5",
    "French": "e4 e6",
    "Scandinavian": "e4 d5",
    "Pirc": "e4 d6 d4 Nf6",
    "Scotch": "e4 e5 Nf3 Nc6 d4",
    "Petrov": "e4 e5 Nf3 Nf6",
    "Philidor": "e4 e5 Nf3 d6",
    "Vienna": "e4 e5 Nc3",

    # d4 openings
    "King's Indian": "d4 Nf6 c4 g6",
    "Grunfeld": "d4 Nf6 c4 g6 Nc3 d5",
    "Benoni": "d4 Nf6 c4 c5",
    "Queen's Gambit": "d4 d5 c4",
    "Slav": "d4 d5 c4 c6",
    "Colle": "d4 d5 Nf3 Nf6 e3",
    "London": "d4 d5 Bf4",
    "Nimzo-Indian": "d4 Nf6 c4 e6 Nc3 Bb4",
    "Dutch": "d4 f5",
    "Catalan": "d4 Nf6 c4 e6 g3"
}

WHITE_SCORE = {"1-0": 1.0, "1/2-1/2": 0.5, "0-1": 0.0}

def main():
    player_a = engine_player("pst", 1.0)
    player_b = engine_player("material", 1.0)

    wins, draws, losses = play_match(player_a, player_b, OPENINGS)
    elo, lower, upper = elo_difference(wins, draws, losses)
    score = (wins + 0.5 * draws) / (wins + draws + losses)

    print(f"pst vs. material: +{wins} ={draws} -{losses}"
          f"(score {score:.1%}, {elo:+.0f} Elo, 95% range {lower:+.0f} to {upper:+.0f})")

def engine_player(engine_id: str, time_limit: float):
    evaluate_fn = ENGINES[engine_id]["evaluate_fn"]

    def play(board: chess.Board) -> chess.Move:
        return chess.Move.from_uci(get_best_move(board, time_limit, evaluate_fn))

    return play

def random_player():
    def play(board: chess.Board) -> chess.Move:
        random_move = random.choice(list(board.legal_moves))

        return random_move

    return play

def play_game(white, black, opening):
    board = chess.Board()

    for move in opening.split():
        board.push_san(move)

    while not board.is_game_over(claim_draw = True):
        if len(board.move_stack) >= MAX_PLIES:
            return "1/2-1/2", "MOVE_LIMIT", board

        player = white if board.turn == chess.WHITE else black
        move = player(board)
        board.push(move)

    outcome = board.outcome(claim_draw = True)

    return outcome.result(), outcome.termination.name, board
    
def play_match(player_a, player_b, openings):
    wins = draws = losses = 0

    for opening_name, opening in openings.items():
        for a_is_white in (True, False):
            if a_is_white:
                result, termination, board = play_game(player_a, player_b, opening)

            else:
                result, termination, board = play_game(player_b, player_a, opening)

            game = chess.pgn.Game.from_board(board)
            game.headers["Event"] = opening_name
            game.headers["White"] = "A" if a_is_white else "B"
            game.headers["Black"] = "B" if a_is_white else "A"
            game.headers["Result"] = result
            game.headers["Termination"] = termination

            print(f"{opening_name}, A as {'White' if a_is_white else 'Black'}: {result} {termination} {board.fen()}")
            print(game, end = "\n\n")

            white_score = WHITE_SCORE[result]
            a_score = white_score if a_is_white else 1 - white_score

            if a_score == 1:
                wins += 1

            elif a_score == 0.5:
                draws += 1

            else:
                losses += 1

    return wins, draws, losses

def score_to_elo(score: float) -> float:
    score = min(max(score, 1e-3), 1 - 1e-3)
        
    return -400 * math.log10(1 / score - 1)

def elo_difference(wins: int, draws: int, losses: int) -> tuple[float, float, float]:
    num_games = wins + draws + losses

    if num_games == 0:
        raise ValueError("No games played")
    
    score = (wins + 0.5 * draws) / num_games
    variance = (wins + draws * 0.25) / num_games - score ** 2
    std_error = math.sqrt(variance / num_games)

    lower, upper = score - 1.96 * std_error, score + 1.96 * std_error

    return score_to_elo(score), score_to_elo(lower), score_to_elo(upper)

if __name__ == "__main__":
    main()