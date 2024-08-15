import numpy as np
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import WHITE, BLACK, KING, PAWN, coord_to_board
from pieces import Empty, Rook, Bishop, Queen, King, Knight, Pawn
from board import Board
from evaluator import GameEvaluator, PieceEvaluator

class TestBoard(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board = Board()
        self.evaluator = GameEvaluator(self.board)

    def test_in_check_from_knight(self):
        # Arrange
        self.board.load_fen("r1bqkbnr/pppppppp/8/8/3nP3/8/PPPPKPPP/RNBQ1BNR w kq - 3 3")

        # Act
        attacker_pos = self.evaluator.in_check()

        # Assert
        self.assertEqual(attacker_pos, [(3, 4)])

    def test_in_check_protected_bishop(self):
        # Arrange
        self.board.load_fen("rn1qkbnr/ppp1ppp1/8/8/5P2/3PBKNb/PPP2NbP/R4b2 w kq - 0 1")

        # Act
        attacker_pos = self.evaluator.in_check()

        # Assert
        self.assertEqual(attacker_pos, [(1, 1)])

    def test_is_checkmate_protected_bishop(self):
        # Arrange
        self.board.load_fen("rn1qkbnr/ppp1ppp1/8/8/5P2/3PBKNb/PPP2NbP/R4b2 w kq - 0 1")
        
        # Act
        res = self.evaluator.is_checkmate()

        # Assert
        self.assertEqual(res["checkmate"], True)
        self.assertEqual(res["capturing_moves"], [])
        self.assertEqual(res["blocking_moves"], [])
        self.assertEqual(res["running_moves"], [])

    def test_is_checkmate_fools_mate(self):
        # Arrange
        self.board.load_fen("rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1")

        # Act
        res = self.evaluator.is_checkmate()

        # Assert
        self.assertEqual(res["checkmate"], True)
        self.assertEqual(res["capturing_moves"], [])
        self.assertEqual(res["blocking_moves"], [])
        self.assertEqual(res["running_moves"], [])

    def test_is_checkmate_en_passant_only_move(self):
        # Arrange
        self.board.load_fen("rnbq1bnr/ppppp2p/3Q4/6pk/5pP1/7K/PPPPPP1P/RNB2BNR b - g3 0 1")

        # Act
        res = self.evaluator.is_checkmate()

        # Assert
        self.assertEqual(self.board.en_passant_square, coord_to_board((2, 1)).lower())
        self.assertEqual(res["checkmate"], False)
        self.assertEqual(res["capturing_moves"], [((3, 2), (2, 1))])
        self.assertEqual(res["blocking_moves"], [])
        self.assertEqual(res["running_moves"], [])

    def test_is_checkmate_pinned_pawn(self):
        # Arrange
        self.board.load_fen("rnbqkb2/ppppppp1/4r3/7p/8/2Pn4/PP1PPPPP/RNBQKBNR w KQq - 0 1")

        # Act
        res = self.evaluator.is_checkmate()

        # Assert
        self.assertEqual(res["checkmate"], True)
        self.assertEqual(res["capturing_moves"], [])
        self.assertEqual(res["blocking_moves"], [])
        self.assertEqual(res["running_moves"], [])

    def test_is_checkmate_pawn_only_move(self):
        # Arrange
        self.board.load_fen("rnbqkb2/ppppppp1/4r3/7p/8/3n4/PPPPPPPP/RNBQKBNR w KQq - 0 1")

        # Act
        res = self.evaluator.is_checkmate()

        # Assert
        self.assertEqual(res["checkmate"], False)
        self.assertEqual(res["capturing_moves"], [((1, 5), (2, 4))])
        self.assertEqual(res["blocking_moves"], [])
        self.assertEqual(res["running_moves"], [])

    def test_is_stalemate_blocked_bishops(self):
        # Arrange
        self.board.load_fen("rnbqkbnr/8/4p3/3pPp2/p1pP1Pp1/PpP1B1Pp/1P1B1B1P/B1B1B1BK w kq - 0 1")

        # Act
        res = self.evaluator.is_stalemate()

        # Assert
        self.assertEqual(res["stalemate"], True)
        self.assertEqual(res["moves"], [])

    def test_is_stalemate_cornered_king(self):
        # Arrange
        self.board.load_fen("4k3/8/8/8/8/6q1/8/7K w - - 0 1")

        # Act
        res = self.evaluator.is_stalemate()

        # Assert
        self.assertEqual(res["stalemate"], True)
        self.assertEqual(res["moves"], [])

    def test_is_stalemate_free_pawn(self):
        # Arrange
        self.board.load_fen("4k3/8/P7/8/8/6q1/8/7K w - - 0 1")

        # Act
        res = self.evaluator.is_stalemate()

        # Assert
        self.assertEqual(res["stalemate"], False)
        self.assertEqual(res["moves"], [((5, 7), (6, 7))])