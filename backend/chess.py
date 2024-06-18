import argparse
from board import *
from player import *

class Chess():
    def parse_args(self):
        parser = argparse.ArgumentParser(description="Chess game.")
        parser.add_argument("-f", "--fen", type=str, help="FEN string to load.")
        parser.add_argument("-v", "--verbose", action="store_true", help="Print all valid moves.")
        return parser.parse_args()

    def play_game(self, args=None, player_w=None, player_b=None):
        fen = args.fen
        board = Board(fen)
        board.print_board()
        while not board.checkmate(args.verbose) and not board.stalemate() and not board.half_move_clock >= 50:
            if args.verbose:
                print(f"Half move clock: {board.half_move_clock}")
            print("Current player: " + str(board.current_player))
            if args.verbose:
                board.all_valid_moves(args.verbose)

            if player_w and board.current_player == WHITE:
                move = player_w.get_move(board)
                start_pos = move[0]
                end_pos = move[1]
            elif player_b and board.current_player == BLACK:
                move = player_b.get_move(board)
                start_pos = move[0]
                end_pos = move[1]
            else:
                move = input("Enter a move: ")
                if len(move) != 4:
                    print("Invalid move. Please enter a move in the format 'e2e4'.")
                    continue
                if move[0] not in "abcdefgh" or move[1] not in "12345678" or move[2] not in "abcdefgh" or move[3] not in "12345678":
                    print("Invalid move. Please enter a move in the format 'e2e4'.")
                    continue

                move = [char.upper() for char in move]
                move[0], move[1], move[2], move[3] = board_to_coord(move[0:2]) + board_to_coord(move[2:4])

                start_pos = (int(move[0]), int(move[1]))
                end_pos = (int(move[2]), int(move[3]))

            board.move(start_pos, end_pos)
            board.print_board()

        if board.checkmate():
            print(f"Game over. {board.current_player} loses.")
            return 1-board.current_player
        elif board.stalemate():
            print(f"Game over. {board.current_player} has been stalemated.")  
        elif board.half_move_clock >= 50:
            print("Game over. 50-move rule.")
        else:
            print("Game over. Unknown reason.")
        return 0.5



if __name__ == "__main__":
    chess = Chess()
    games_played = 0
    while True:
        chess.play_game(chess.parse_args(), player_w=RandomBot(), player_b=RandomBot())
        games_played += 1
        print(f"GAMES PLAYED: {games_played} ##############################################################################################################################")