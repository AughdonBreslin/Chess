import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import EMPTY, PAWN, ROOK, BISHOP, QUEEN, KING, KNIGHT, NONE, WHITE, BLACK, board_to_coord, coord_to_board
from board import Board

class TestPieceInfo(unittest.TestCase):
    pass