import chess

from engine.engine import get_best_move

def main():
    color = input("Which color do you want to play? (White: w, Black: else) ")
    player_color = chess.WHITE if color == "w" else chess.BLACK

    board = chess.Board()

    while True:

        print(board.unicode(orientation = player_color, invert_color = True))
        
        if board.is_game_over(claim_draw = True):
            print(f"Game over: {board.result()} ({board.outcome().termination.name.lower()})")
            break

        if board.turn == player_color:
            move = read_player_move(board)
            board.push(move)

        else:
            move = chess.Move.from_uci(get_best_move(board.fen(), 3))
            print("Engine move:", board.san(move))
            board.push(move)

def read_player_move(board: chess.Board) -> chess.Move:
    while True:
        user_move = input("Your move: ")

        for parse in (board.parse_san, board.parse_uci):
            try:
                return parse(user_move)

            except ValueError:
                pass

        print("Invalid or illegal move, try again (e.g. e4, Nf3)")

if __name__ == "__main__":
    main()