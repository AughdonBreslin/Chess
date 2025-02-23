import numpy as np
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import WHITE, BLACK, KING, PAWN, coord_to_board
from pieces import Empty, Rook, Bishop, Queen, King, Knight, Pawn
from board import Board

class TestBoard(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board = Board()

    def test_board_properties(self):
        # Assert
        self.assertEqual(self.board.current_player, WHITE)
        self.assertEqual(self.board.en_passant_square, "-")
        self.assertEqual(self.board.halfmove_clock, 0)
        self.assertEqual(self.board.move_num, 1)
        self.assertEqual(self.board.history, [])

    def test_board_clear(self):
        # Arrange
        self.board[0][0] = Rook(WHITE)

        # Act
        self.board.clear()

        # Assert
        self.assertTrue((self.board == np.array([[Empty() for _ in range(8)] for _ in range(8)])).all())
        self.assertEqual(self.board.current_player, WHITE)
        self.assertEqual(self.board.en_passant_square, "-")
        self.assertEqual(self.board.halfmove_clock, 0)
        self.assertEqual(self.board.move_num, 1)
        self.assertEqual(self.board.history, [])

    def test_board_setup(self):
        # Act
        self.board.setup()

        # Assert
        self.assertTrue(not (self.board[0] == [Rook(WHITE), Knight(BLACK), Bishop(WHITE), King(WHITE),
                                                     Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)]).all())
        self.assertTrue(not (self.board[0] == [Rook(WHITE), Knight(WHITE), Bishop(WHITE), King(WHITE),
                                                     Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)]).all())
        self.assertTrue((self.board[0] == [Rook(WHITE, True), Knight(WHITE), Bishop(WHITE), King(WHITE, True),
                                                 Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE, True)]).all())
        self.assertTrue((self.board[1] == [Pawn(WHITE) for _ in range(8)]).all())
        self.assertTrue((self.board[6] == [Pawn(BLACK) for _ in range(8)]).all())
        self.assertTrue((self.board[7] == [Rook(BLACK, True), Knight(BLACK), Bishop(BLACK), King(BLACK, True),
                                                 Queen(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK, True)]).all())
        
    def test_board_load_fen(self):
        # Arrange
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        # Act
        self.board.load_fen(fen)
        print(self.board)

        # Assert
        
        self.assertTrue((self.board[0] == [Rook(WHITE, True), Knight(WHITE), Bishop(WHITE), King(WHITE, True),
                                                 Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE, True)]).all())
        self.assertTrue((self.board[1] == [Pawn(WHITE) for _ in range(8)]).all())
        self.assertTrue((self.board[6] == [Pawn(BLACK) for _ in range(8)]).all())
        self.assertTrue((self.board[7] == [Rook(BLACK, True), Knight(BLACK), Bishop(BLACK), King(BLACK, True),
                                                 Queen(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK, True)]).all())
        self.assertEqual(self.board.current_player, WHITE)
        self.assertEqual(self.board.en_passant_square, "-")
        self.assertEqual(self.board.halfmove_clock, 0)
        self.assertEqual(self.board.move_num, 1)

    def test_board_to_fen1(self):
        # Arrange
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.board.load_fen(fen)

        # Act
        result = self.board.to_fen()

        # Assert
        self.assertEqual(result, fen)

    def test_board_to_fen2(self):
        # Arrange
        fen = "2rqk2r/1pb1p1pp/2p1Pn2/2Pp1p2/pPnP4/2N2NP1/P1b2PBP/R1BQK1R1 b Qk b3 0 1"
        self.board.load_fen(fen)
        print(self.board)

        # Act
        result = self.board.to_fen()

        # Assert
        self.assertEqual(result, fen)

    def test_move(self):
        # Arrange
        self.board.setup()
        move = ((6, 4), (4, 4))

        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[4][4], Pawn(BLACK))
        self.assertEqual(self.board[6][4], Empty())
        self.assertEqual(self.board.current_player, BLACK)
        self.assertEqual(self.board.en_passant_square, "d6")
        self.assertEqual(self.board.halfmove_clock, 0)
        self.assertEqual(self.board.move_num, 2)
        self.assertEqual(self.board.history, [move])

    def test_move2(self):
        # Arrange
        self.board.setup()
        move = ((0, 1), (2, 1))

        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[2][1], Knight(WHITE))
        self.assertEqual(self.board[0][1], Empty())
        self.assertEqual(self.board.current_player, BLACK)
        self.assertEqual(self.board.en_passant_square, "-")
        self.assertEqual(self.board.halfmove_clock, 1)
        self.assertEqual(self.board.move_num, 2)
        self.assertEqual(self.board.history, [move])

    def test_move_promotion(self):
        # Arrange
        self.board.clear()
        self.board.current_player = BLACK
        self.board[1][0] = Pawn(BLACK)
        move = ((1, 0), (0, 0))

        # Act
        self.board.move(move[0], move[1] + ("q",))

        # Assert
        self.assertEqual(self.board[0][0], Queen(BLACK))
        self.assertEqual(self.board[1][0], Empty())

    def test_move_castling_K(self):
        # Arrange
        self.board.clear()
        king = King(WHITE, True)
        self.board[0][3] = king
        rook = Rook(WHITE, True)
        self.board[0][0] = rook
        move = ((0, 3), (0, 1))
        
        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[0][0], Empty())
        self.assertEqual(self.board[0][1], king)
        self.assertEqual(self.board[0][2], rook)
        self.assertEqual(self.board[0][3], Empty())

    def test_move_castling_Q(self):
        # Arrange
        self.board.clear()
        king = King(WHITE, True)
        self.board[0][3] = king
        rook = Rook(WHITE, True)
        self.board[0][7] = rook
        move = ((0, 3), (0, 5))
        
        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[0][7], Empty())
        self.assertEqual(self.board[0][6], Empty())
        self.assertEqual(self.board[0][5], king)
        self.assertEqual(self.board[0][4], rook)
        self.assertEqual(self.board[0][3], Empty())

    def test_move_castling_k(self):
        # Arrange
        self.board.clear()
        self.board.current_player = BLACK
        king = King(BLACK, True)
        self.board[7][3] = king
        rook = Rook(BLACK, True)
        self.board[7][0] = rook
        move = ((7, 3), (7, 1))

        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[7][0], Empty())
        self.assertEqual(self.board[7][1], king)
        self.assertEqual(self.board[7][2], rook)
        self.assertEqual(self.board[7][3], Empty())

    def test_move_castling_q(self):
        # Arrange
        self.board.clear()
        self.board.current_player = BLACK
        king = King(BLACK, True)
        self.board[7][3] = king
        rook = Rook(BLACK, True)
        self.board[7][7] = rook
        move = ((7, 3), (7, 5))

        # Act
        self.board.move(move[0], move[1])

        # Assert
        self.assertEqual(self.board[7][7], Empty())
        self.assertEqual(self.board[7][6], Empty())
        self.assertEqual(self.board[7][5], king)
        self.assertEqual(self.board[7][4], rook)
        self.assertEqual(self.board[7][3], Empty())

    def test_move_en_passant(self):
        # Arrange
        self.board.clear()
        pawn_w = Pawn(WHITE)
        self.board[1][4] = pawn_w
        pawn_b = Pawn(BLACK)
        self.board[3][3] = pawn_b
        move = ((1, 4), (3, 4))
        move2 = ((3, 3), (2, 4))

        # Act
        self.board.move(move[0], move[1])
        self.board.move(move2[0], move2[1])

        # Assert
        self.assertEqual(self.board[3][4], Empty())
        self.assertEqual(self.board[3][3], Empty())
        self.assertEqual(self.board[2][4], pawn_b)

    def test_find_piece(self):
        # Arrange
        self.board.clear()
        self.board[4][4] = King(WHITE)

        # Act
        pos = self.board.find_piece(KING)

        # Assert
        self.assertEqual(pos, (4, 4))

    def test_find_piece2(self):
        # Arrange
        self.board.clear()

        # Act
        pos = self.board.find_piece(KING)

        # Assert
        self.assertEqual(pos, None)

    def test_find_pieces(self):
        # Arrange
        self.board.clear()
        pawns = [Pawn(WHITE) for _ in range(8)]
        self.board[1] = pawns

        # Act
        pos = self.board.find_pieces(PAWN)

        # Assert
        self.assertTrue(pos, [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)])
