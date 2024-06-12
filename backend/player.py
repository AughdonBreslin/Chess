import numpy as np
from piece_info import coord_to_board
class ChessBot():
    def get_move(self, board):
        pass
    
class RandomBot(ChessBot):
    def get_move(self, board):
        moves = board.all_valid_moves()
        move = moves[np.random.randint(0, len(moves))]
        print(f"Bot move: {coord_to_board(move[0])} -> {coord_to_board(move[1])}")
        return move