import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import EMPTY, PAWN, ROOK, BISHOP, QUEEN, KING, KNIGHT, NONE, WHITE, BLACK, board_to_coord, coord_to_board

class TestPieceInfo(unittest.TestCase):
    def test_piece_type(self):
        self.assertEqual(str(EMPTY), "EMPTY")
        self.assertEqual(str(PAWN), "PAWN")
        self.assertEqual(str(ROOK), "ROOK")
        self.assertEqual(str(KNIGHT), "KNIGHT")
        self.assertEqual(str(BISHOP), "BISHOP")
        self.assertEqual(str(QUEEN), "QUEEN")
        self.assertEqual(str(KING), "KING")

    def test_color(self):
        self.assertEqual(str(NONE), "NONE")
        self.assertEqual(str(WHITE), "WHITE")
        self.assertEqual(str(BLACK), "BLACK")
        self.assertEqual(int(NONE), -1)
        self.assertEqual(int(WHITE), 0)
        self.assertEqual(int(BLACK), 1)
        self.assertEqual(1 - WHITE, BLACK)
        self.assertEqual(1 - BLACK, WHITE)
        self.assertEqual((-1) ** WHITE, 1)
        self.assertEqual((-1) ** BLACK, -1)
        self.assertEqual(WHITE == BLACK, False)
        self.assertEqual(WHITE != BLACK, True)

    def test_board_to_coord(self):
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

if __name__ == "__main__":
    unittest.main()