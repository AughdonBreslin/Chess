import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import EMPTY, PAWN, ROOK, BISHOP, QUEEN, KING, KNIGHT, NONE, WHITE, BLACK, board_to_coord, coord_to_board

class TestPieceInfo(unittest.TestCase):
    def test_piece_type_str(self):
        # Assert
        self.assertEqual(str(EMPTY), "Empty")
        self.assertEqual(str(PAWN), "Pawn")
        self.assertEqual(str(ROOK), "Rook")
        self.assertEqual(str(KNIGHT), "Knight")
        self.assertEqual(str(BISHOP), "Bishop")
        self.assertEqual(str(QUEEN), "Queen")
        self.assertEqual(str(KING), "King")

    def test_color_str(self):
        # Assert
        self.assertEqual(str(NONE), "NONE")
        self.assertEqual(str(WHITE), "WHITE")
        self.assertEqual(str(BLACK), "BLACK")

    def test_color_int(self):
        # Assert
        self.assertEqual(int(NONE), -1)
        self.assertEqual(int(WHITE), 0)
        self.assertEqual(int(BLACK), 1)

    def test_color_eq(self):
        # Assert
        self.assertEqual(WHITE == BLACK, False)
        self.assertEqual(WHITE == 0, True)
        self.assertEqual(WHITE == 1, False)
        self.assertEqual(BLACK == 0, False)
        self.assertEqual(BLACK == 1, True)

    def test_color_ne(self):
        # Assert
        self.assertEqual(WHITE != BLACK, True)
        self.assertEqual(WHITE != 0, False)
        self.assertEqual(WHITE != 1, True)
        self.assertEqual(BLACK != 0, True)
        self.assertEqual(BLACK != 1, False)

    def test_color_index(self):
        # Arrange
        arr = [WHITE, BLACK]

        # Assert
        self.assertEqual(arr[WHITE], WHITE)
        self.assertEqual(arr[BLACK], BLACK)

    def test_color_sub(self):
        # Assert
        self.assertEqual(WHITE - 1, -1)
        self.assertEqual(BLACK - 1, 0)

    def test_color_rsub(self):
        # Assert
        self.assertEqual(1 - WHITE, BLACK)
        self.assertEqual(1 - BLACK, WHITE)

    def test_color_mul(self):
        # Assert
        self.assertEqual(WHITE * 1, 0)
        self.assertEqual(BLACK * 1, 1)

    def test_color_rmul(self):
        # Assert
        self.assertEqual(1 * WHITE, 0)
        self.assertEqual(1 * BLACK, 1)

    def test_color_rpow(self):
        # Assert
        self.assertEqual((-1) ** WHITE, 1)
        self.assertEqual((-1) ** BLACK, -1)

    def test_board_to_coord(self):
        # Assert
        self.assertEqual(board_to_coord("A1"), (0, 7))
        self.assertEqual(board_to_coord("A2"), (1, 7))
        self.assertEqual(board_to_coord("A3"), (2, 7))
        self.assertEqual(board_to_coord("A4"), (3, 7))
        self.assertEqual(board_to_coord("A5"), (4, 7))
        self.assertEqual(board_to_coord("A6"), (5, 7))
        self.assertEqual(board_to_coord("A7"), (6, 7))
        self.assertEqual(board_to_coord("A8"), (7, 7))
        self.assertEqual(board_to_coord("B1"), (0, 6))
        self.assertEqual(board_to_coord("C1"), (0, 5))
        self.assertEqual(board_to_coord("D1"), (0, 4))
        self.assertEqual(board_to_coord("E1"), (0, 3))
        self.assertEqual(board_to_coord("F1"), (0, 2))
        self.assertEqual(board_to_coord("G1"), (0, 1))
        self.assertEqual(board_to_coord("H1"), (0, 0))

    def test_coord_to_board(self):
        # Assert
        self.assertEqual(coord_to_board((0, 7)), "A1")
        self.assertEqual(coord_to_board((1, 7)), "A2")
        self.assertEqual(coord_to_board((2, 7)), "A3")
        self.assertEqual(coord_to_board((3, 7)), "A4")
        self.assertEqual(coord_to_board((4, 7)), "A5")
        self.assertEqual(coord_to_board((5, 7)), "A6")
        self.assertEqual(coord_to_board((6, 7)), "A7")
        self.assertEqual(coord_to_board((7, 7)), "A8")
        self.assertEqual(coord_to_board((0, 6)), "B1")
        self.assertEqual(coord_to_board((0, 5)), "C1")
        self.assertEqual(coord_to_board((0, 4)), "D1")
        self.assertEqual(coord_to_board((0, 3)), "E1")
        self.assertEqual(coord_to_board((0, 2)), "F1")
        self.assertEqual(coord_to_board((0, 1)), "G1")
        self.assertEqual(coord_to_board((0, 0)), "H1")