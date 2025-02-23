import argparse

from piece_info import Color, WHITE
from board import Board
from evaluator import GameEvaluator
from handler import Handler

class Chess:
    def __init__(self, fen: str = None, moves: list[str] = None, verbose: bool = False) -> None:
        self.args = self.parse_args()
        self.fen = self.args.fen if self.args.fen else fen
        self.verbose = self.args.verbose if self.args.verbose else verbose
        self.moves = moves

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Chess game.")
        parser.add_argument("-f", "--fen", type=str, help="FEN string to load.")
        parser.add_argument("-v", "--verbose", action="store_true", help="Prints additional info at each move.")
        return parser.parse_args()

    def play(self) -> int:
        board = Board(self.fen)
        evaluator = GameEvaluator(board)
        handler = Handler()
        game_state = evaluator.is_game_over()
        while not game_state["game_over"]:
            print(repr(board) if self.verbose else str(board))
            move = handler.get_move()
            validity = evaluator.is_valid(move["start_pos"], move["end_pos"])
            if validity["valid"]:
                board.move(move["start_pos"], move["end_pos"])
            else:
                print(validity)
            game_state = evaluator.is_game_over()
        print(evaluator.is_game_over() if self.verbose else "")
        print(repr(board) if self.verbose else str(board))
        result = evaluator.outcome(game_state)
        print(result["reason"])
        return result["point"]
        
        
if __name__ == "__main__":
    chess = Chess()
    chess.play()

