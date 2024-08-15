import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from piece_info import EMPTY, PAWN, ROOK, BISHOP, QUEEN, KING, KNIGHT, NONE, WHITE, BLACK, board_to_coord, coord_to_board
from pieces import ChessPiece, Empty, Rook, Knight, Bishop, Queen, King, Pawn

class TestPieces(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPieces, self).__init__(*args, **kwargs)

    def test_chess_piece_properties(self):
        # Arrange
        piece = ChessPiece(WHITE, PAWN)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, PAWN)

    def test_chess_piece_eq(self):
        # Arrange
        piece1 = ChessPiece(WHITE, PAWN)
        piece2 = ChessPiece(WHITE, PAWN)
        piece3 = ChessPiece(BLACK, PAWN)
        piece4 = ChessPiece(WHITE, ROOK)
        
        # Assert
        self.assertEqual(piece1 == piece2, True)
        self.assertEqual(piece1 == piece3, False)
        self.assertEqual(piece1 == piece4, False)
        self.assertEqual(piece1 == WHITE, True)
        self.assertEqual(piece1 == BLACK, False)
        self.assertEqual(piece1 == 0, True)
        self.assertEqual(piece1 == 1, False)
        self.assertEqual(piece1 == PAWN, True)
        self.assertEqual(piece1 == ROOK, False)

    def test_chess_piece_ne(self):
        # Arrange
        piece1 = ChessPiece(WHITE, PAWN)
        piece2 = ChessPiece(WHITE, PAWN)
        piece3 = ChessPiece(BLACK, PAWN)
        piece4 = ChessPiece(WHITE, ROOK)
        
        # Assert
        self.assertEqual(piece1 != piece2, False)
        self.assertEqual(piece1 != piece3, True)
        self.assertEqual(piece1 != piece4, True)
        self.assertEqual(piece1 != WHITE, False)
        self.assertEqual(piece1 != BLACK, True)
        self.assertEqual(piece1 != 0, False)
        self.assertEqual(piece1 != 1, True)
        self.assertEqual(piece1 != PAWN, False)
        self.assertEqual(piece1 != ROOK, True)

    def test_chess_piece_repr(self):
        # Arrange
        piece1 = ChessPiece(WHITE, PAWN)
        piece2 = ChessPiece(BLACK, PAWN)
        
        # Assert
        self.assertEqual(repr(piece1), "♟")
        self.assertEqual(repr(piece2), "♙")

    def test_chess_piece_out_of_bounds(self):
        # Assert
        self.assertEqual(ChessPiece.out_of_bounds((0, 0)), False)
        self.assertEqual(ChessPiece.out_of_bounds((0, 1)), False)
        self.assertEqual(ChessPiece.out_of_bounds((0, -1)), True)
        self.assertEqual(ChessPiece.out_of_bounds((0, 8)), True)
        self.assertEqual(ChessPiece.out_of_bounds((1, 0)), False)
        self.assertEqual(ChessPiece.out_of_bounds((-1, 0)), True)
        self.assertEqual(ChessPiece.out_of_bounds((8, 0)), True)

    def test_empty_piece_properties(self):
        # Arrange
        piece = Empty()
        
        # Assert
        self.assertEqual(piece.color, NONE)
        self.assertEqual(piece.type, EMPTY)
        self.assertEqual(piece, NONE)
        self.assertEqual(piece, EMPTY)

    def test_empty_piece_can_move(self):
        # Arrange
        piece = Empty()
        
        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 1)), False)
        self.assertEqual(piece.can_move((0, 0), (1, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (1, 1)), False)

    def test_empty_piece_moves(self):
        # Arrange
        piece = Empty()
        
        # Assert
        self.assertEqual(piece.moves((0, 0)), [])
        self.assertEqual(piece.moves((0, 1)), [])
        self.assertEqual(piece.moves((1, 0)), [])
        self.assertEqual(piece.moves((1, 1)), [])

    def test_empty_piece_line_of_sight(self):
        # Arrange
        piece = Empty()
        
        # Assert
        self.assertEqual(piece.line_of_sight((0, 0), (0, 0)), [])
        self.assertEqual(piece.line_of_sight((0, 0), (0, 1)), [])
        self.assertEqual(piece.line_of_sight((0, 0), (1, 0)), [])
        self.assertEqual(piece.line_of_sight((0, 0), (1, 1)), [])

    def test_rook_piece_properties(self):
        # Arrange
        piece = Rook(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, ROOK)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, ROOK)

    def test_rook_piece_can_move(self):
        # Arrange
        piece = Rook(WHITE)
        
        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 0)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 1)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 7)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 0)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 7)), False)

    def test_rook_piece_moves(self):
        # Arrange
        piece = Rook(WHITE)
        
        # Assert
        self.assertEqual(set(piece.moves((0, 0))), set([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]))
        self.assertEqual(set(piece.moves((0, 1))), set([(0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]))
        self.assertEqual(set(piece.moves((1, 0))), set([(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]))

    def test_rook_piece_line_of_sight(self):
        # Arrange
        piece = Rook(WHITE)
        
        # Assert
        self.assertEqual(piece.line_of_sight((0, 0), (0, 7)), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)])
        self.assertEqual(piece.line_of_sight((0, 0), (7, 0)), [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)])
        self.assertEqual(piece.line_of_sight((0, 0), (7, 7)), [])
        
    def test_bishop_piece_properties(self):
        # Arrange
        piece = Bishop(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, BISHOP)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, BISHOP)

    def test_bishop_piece_can_move(self):
        # Arrange
        piece = Bishop(WHITE)
        
        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 1)), False)
        self.assertEqual(piece.can_move((0, 0), (1, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (1, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 7)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 7)), False)

    def test_bishop_piece_moves(self):
        # Arrange
        piece = Bishop(WHITE)
        
        # Assert
        self.assertEqual(set(piece.moves((0, 0))), set([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)]))
        self.assertEqual(set(piece.moves((0, 1))), set([(1, 0), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]))
        self.assertEqual(set(piece.moves((1, 0))), set([(0, 1), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6)]))
        self.assertEqual(set(piece.moves((4, 4))), set([(3, 3), (2, 2), (1, 1), (0, 0), (3, 5), (2, 6), (1, 7), (5, 3), (6, 2), (7, 1), (5, 5), (6, 6), (7, 7)]))

    def test_bishop_piece_line_of_sight(self):
        # Arrange
        piece = Bishop(WHITE)
        
        # Assert
        self.assertEqual(piece.line_of_sight((0, 0), (7, 7)), [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])
        self.assertEqual(piece.line_of_sight((0, 0), (7, 0)), [])
        self.assertEqual(piece.line_of_sight((0, 0), (0, 7)), [])
        self.assertEqual(piece.line_of_sight((3, 4), (0, 1)), [(2, 3), (1, 2)])

    def test_queen_piece_properties(self):
        # Arrange
        piece = Queen(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, QUEEN)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, QUEEN)

    def test_queen_piece_can_move(self):
        # Arrange
        piece = Queen(WHITE)
        
        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 0)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 7)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 0)), True)
        self.assertEqual(piece.can_move((0, 0), (0, 7)), True)
        self.assertEqual(piece.can_move((4, 4), (0, 0)), True)
        self.assertEqual(piece.can_move((4, 4), (0, 4)), True)
        self.assertEqual(piece.can_move((4, 4), (4, 0)), True)
        self.assertEqual(piece.can_move((4, 4), (7, 7)), True)
        self.assertEqual(piece.can_move((4, 4), (7, 4)), True)
        self.assertEqual(piece.can_move((4, 4), (4, 7)), True)
        self.assertEqual(piece.can_move((4, 4), (1, 7)), True)
        self.assertEqual(piece.can_move((4, 4), (7, 1)), True)

    def test_queen_piece_moves(self):
        # Arrange
        piece = Queen(WHITE)
        
        # Assert
        self.assertEqual(set(piece.moves((0, 0))), set([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)]))
        self.assertEqual(set(piece.moves((0, 1))), set([(0, 0), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (1, 0), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]))
        self.assertEqual(set(piece.moves((1, 0))), set([(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (0, 1), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6)]))
        self.assertEqual(set(piece.moves((4, 4))), set([(3, 3), (2, 2), (1, 1), (0, 0), (3, 5), (2, 6), (1, 7), (5, 3), (6, 2), (7, 1), (5, 5), (6, 6), (7, 7), (3, 4), (2, 4), (1, 4), (0, 4), (5, 4), (6, 4), (7, 4), (4, 3), (4, 2), (4, 1), (4, 0), (4, 5), (4, 6), (4, 7)]))

    def test_queen_piece_line_of_sight(self):
        # Arrange
        piece = Queen(WHITE)
        
        # Assert
        self.assertEqual(piece.line_of_sight((0, 0), (7, 7)), [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])
        self.assertEqual(piece.line_of_sight((0, 0), (7, 0)), [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)])
        self.assertEqual(piece.line_of_sight((0, 0), (0, 7)), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)])
        self.assertEqual(piece.line_of_sight((3, 4), (0, 1)), [(2, 3), (1, 2)])

    def test_knight_piece_properties(self):
        # Arrange
        piece = Knight(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, KNIGHT)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, KNIGHT)

    def test_knight_piece_can_move(self):
        # Arrange
        piece = Knight(WHITE)

        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (1, 2)), True)
        self.assertEqual(piece.can_move((0, 0), (2, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (2, 2)), False)
        self.assertEqual(piece.can_move((4, 4), (2, 3)), True)
        self.assertEqual(piece.can_move((4, 4), (3, 2)), True)
        self.assertEqual(piece.can_move((4, 4), (3, 6)), True)
        self.assertEqual(piece.can_move((4, 4), (2, 5)), True)
        self.assertEqual(piece.can_move((4, 4), (6, 5)), True)
        self.assertEqual(piece.can_move((4, 4), (5, 6)), True)
        self.assertEqual(piece.can_move((4, 4), (6, 3)), True)
        self.assertEqual(piece.can_move((4, 4), (5, 2)), True)
        self.assertEqual(piece.can_move((4, 4), (3, 3)), False)
        
    def test_knight_piece_moves(self):
        # Arrange
        piece = Knight(WHITE)
        
        # Assert
        self.assertEqual(set(piece.moves((0, 0))), set([(1, 2), (2, 1)]))
        self.assertEqual(set(piece.moves((0, 1))), set([(1, 3), (2, 0), (2, 2)]))
        self.assertEqual(set(piece.moves((0, 4))), set([(1, 2), (1, 6), (2, 3), (2, 5)]))
        self.assertEqual(set(piece.moves((0, 6))), set([(1, 4), (2, 5), (2, 7)]))
        self.assertEqual(set(piece.moves((0, 7))), set([(1, 5), (2, 6)]))
        self.assertEqual(set(piece.moves((1, 0))), set([(0, 2), (2, 2), (3, 1)]))
        self.assertEqual(set(piece.moves((1, 1))), set([(0, 3), (2, 3), (3, 0), (3, 2)]))
        self.assertEqual(set(piece.moves((1, 4))), set([(0, 2), (0, 6), (2, 2), (2, 6), (3, 3), (3, 5)]))
        self.assertEqual(set(piece.moves((1, 6))), set([(0, 4), (2, 4), (3, 5), (3, 7)]))
        self.assertEqual(set(piece.moves((1, 7))), set([(0, 5), (2, 5), (3, 6)]))
        self.assertEqual(set(piece.moves((4, 0))), set([(2, 1), (6, 1), (3, 2), (5, 2)]))
        self.assertEqual(set(piece.moves((4, 1))), set([(2, 0), (2, 2), (6, 0), (6, 2), (3, 3), (5, 3)]))
        self.assertEqual(set(piece.moves((4, 4))), set([(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)]))
        self.assertEqual(set(piece.moves((4, 6))), set([(2, 5), (2, 7), (3, 4), (5, 4), (6, 5), (6, 7)]))
        self.assertEqual(set(piece.moves((4, 7))), set([(2, 6), (3, 5), (5, 5), (6, 6)]))
        self.assertEqual(set(piece.moves((6, 0))), set([(4, 1), (5, 2), (7, 2)]))
        self.assertEqual(set(piece.moves((6, 1))), set([(4, 0), (4, 2), (5, 3), (7, 3)]))
        self.assertEqual(set(piece.moves((6, 4))), set([(4, 3), (4, 5), (5, 2), (5, 6), (7, 2), (7, 6)]))
        self.assertEqual(set(piece.moves((6, 6))), set([(4, 5), (4, 7), (5, 4), (7, 4)]))
        self.assertEqual(set(piece.moves((6, 7))), set([(4, 6), (5, 5), (7, 5)]))
        self.assertEqual(set(piece.moves((7, 0))), set([(5, 1), (6, 2)]))
        self.assertEqual(set(piece.moves((7, 1))), set([(5, 0), (5, 2), (6, 3)]))
        self.assertEqual(set(piece.moves((7, 4))), set([(5, 3), (5, 5), (6, 2), (6, 6)]))
        self.assertEqual(set(piece.moves((7, 6))), set([(5, 5), (5, 7), (6, 4)]))
        self.assertEqual(set(piece.moves((7, 7))), set([(5, 6), (6, 5)]))

    def test_pawn_piece_properties(self):
        # Arrange
        piece = Pawn(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, PAWN)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, PAWN)

    def test_pawn_piece_can_move(self):
        # Arrange
        piece = Pawn(WHITE)
        piece2 = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.can_move((1, 0), (1, 0)), False)
        self.assertEqual(piece.can_move((1, 0), (2, 0)), True)
        self.assertEqual(piece.can_move((1, 0), (1, 1)), False)
        self.assertEqual(piece.can_move((1, 0), (3, 0)), True)
        self.assertEqual(piece.can_move((1, 0), (2, 1)), True)
        self.assertEqual(piece.can_move((1, 0), (2, -1)), False)
        self.assertEqual(piece2.can_move((6, 0), (6, 0)), False)
        self.assertEqual(piece2.can_move((6, 0), (5, 0)), True)
        self.assertEqual(piece2.can_move((6, 0), (6, 1)), False)
        self.assertEqual(piece2.can_move((6, 0), (4, 0)), True)
        self.assertEqual(piece2.can_move((6, 0), (5, 1)), True)
        self.assertEqual(piece2.can_move((6, 0), (5, -1)), False)

    def test_pawn_piece_moves(self):
        # Arrange
        piece = Pawn(WHITE)
        piece2 = Pawn(BLACK)
        
        # Assert
        self.assertEqual(set(piece.moves((1, 0))), set([(2, 0), (3, 0), (2, 1)]))
        self.assertEqual(set(piece.moves((1, 1))), set([(2, 0), (2, 1), (2, 2), (3, 1)]))
        self.assertEqual(set(piece.moves((2, 0))), set([(3, 0), (3, 1)]))
        self.assertEqual(set(piece.moves((2, 1))), set([(3, 0), (3, 1), (3, 2)]))
        self.assertEqual(set(piece2.moves((6, 0))), set([(5, 0), (4, 0), (5, 1)]))
        self.assertEqual(set(piece2.moves((6, 1))), set([(5, 1), (4, 1), (5, 0), (5, 2)]))
        self.assertEqual(set(piece2.moves((5, 0))), set([(4, 0), (4, 1)]))
        self.assertEqual(set(piece2.moves((5, 1))), set([(4, 0), (4, 1), (4, 2)]))

    def test_pawn_piece_line_of_sight(self):
        # Arrange
        piece = Pawn(WHITE)
        piece2 = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.line_of_sight((1, 0), (3, 0)), [])
        self.assertEqual(piece.line_of_sight((1, 0), (2, 1)), [])
        self.assertEqual(piece.line_of_sight((2, 0), (4, 0)), [])
        self.assertEqual(piece.line_of_sight((2, 0), (3, 1)), [])
        self.assertEqual(piece2.line_of_sight((6, 0), (4, 0)), [])
        self.assertEqual(piece2.line_of_sight((6, 0), (5, 1)), [])
        self.assertEqual(piece2.line_of_sight((5, 0), (3, 0)), [])
        self.assertEqual(piece2.line_of_sight((5, 0), (4, 1)), [])

    def test_pawn_attack_options(self):
        # Arrange
        piece = Pawn(WHITE)
        piece2 = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.attack_options((1, 0)), [(2, 1)])
        self.assertEqual(piece.attack_options((2, 0)), [(3, 1)])
        self.assertEqual(piece.attack_options((1, 1)), [(2, 0), (2, 2)])
        self.assertEqual(piece2.attack_options((6, 0)), [(5, 1)])
        self.assertEqual(piece2.attack_options((5, 0)), [(4, 1)])
        self.assertEqual(piece2.attack_options((6, 1)), [(5, 0), (5, 2)])

    def test_king_piece_properties(self):
        # Arrange
        piece = King(WHITE)
        
        # Assert
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.type, KING)
        self.assertEqual(piece, WHITE)
        self.assertEqual(piece, KING)

    def test_king_piece_can_move_no_castle(self):
        # Arrange
        piece = King(WHITE)
        
        # Assert
        self.assertEqual(piece.can_move((0, 0), (0, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 0)), True)
        self.assertEqual(piece.can_move((0, 0), (1, 1)), True)
        self.assertEqual(piece.can_move((0, 0), (7, 7)), False)
        self.assertEqual(piece.can_move((0, 0), (7, 0)), False)
        self.assertEqual(piece.can_move((0, 0), (0, 7)), False)
        self.assertEqual(piece.can_move((4, 4), (0, 0)), False)
        self.assertEqual(piece.can_move((4, 4), (3, 4)), True)
        self.assertEqual(piece.can_move((4, 4), (5, 4)), True)
        self.assertEqual(piece.can_move((4, 4), (4, 3)), True)
        self.assertEqual(piece.can_move((4, 4), (4, 5)), True)
        self.assertEqual(piece.can_move((4, 4), (3, 3)), True)
        self.assertEqual(piece.can_move((4, 4), (5, 5)), True)
        self.assertEqual(piece.can_move((4, 4), (3, 5)), True)
        self.assertEqual(piece.can_move((4, 4), (5, 3)), True)
        self.assertEqual(piece.can_move((4, 4), (2, 4)), False)
        self.assertEqual(piece.can_move((4, 4), (6, 4)), False)
        self.assertEqual(piece.can_move((4, 4), (4, 2)), False)
        self.assertEqual(piece.can_move((4, 4), (4, 6)), False)
        self.assertEqual(piece.can_move((0, 3), (0, 5)), False)
        self.assertEqual(piece.can_move((0, 3), (0, 1)), False)

    def test_king_piece_can_move_can_castle(self):
        # Arrange
        piece = King(WHITE, True)
        piece2 = King(BLACK, True)
        
        # Assert
        self.assertEqual(piece.can_move((4, 4), (2, 4)), False)
        self.assertEqual(piece.can_move((4, 4), (6, 4)), False)
        self.assertEqual(piece.can_move((4, 4), (4, 2)), False)
        self.assertEqual(piece.can_move((4, 4), (4, 6)), False)
        self.assertEqual(piece.can_move((0, 3), (0, 5)), True)
        self.assertEqual(piece.can_move((0, 3), (0, 1)), True)
        self.assertEqual(piece2.can_move((7, 3), (7, 5)), True)
        self.assertEqual(piece2.can_move((7, 3), (7, 1)), True)
        self.assertEqual(piece2.can_move((0, 3), (0, 1)), False)
        self.assertEqual(piece2.can_move((0, 3), (0, 5)), False)
    
    def test_king_piece_moves(self):
        # Arrange
        piece = King(WHITE)
        
        # Assert
        self.assertEqual(set(piece.moves((0, 0))), set([(0, 1), (1, 0), (1, 1)]))
        self.assertEqual(set(piece.moves((0, 1))), set([(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)]))
        self.assertEqual(set(piece.moves((1, 0))), set([(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)]))
        self.assertEqual(set(piece.moves((4, 4))), set([(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]))

    def test_king_piece_castling_options(self):
        # Arrange
        piece = King(WHITE, True)
        piece2 = King(BLACK, True)
        
        # Assert
        self.assertEqual(piece.castling_options((0, 3)), [(0, 1), (0, 5)])
        self.assertEqual(piece.castling_options((7, 3)), [])
        self.assertEqual(piece2.castling_options((7, 3)), [(7, 1), (7, 5)])
        self.assertEqual(piece2.castling_options((0, 3)), [])