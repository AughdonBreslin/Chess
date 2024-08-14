import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from board import *

class TestPieces(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPieces, self).__init__(*args, **kwargs)
        self.board = Board()
        
    def test_empty(self):
        # Arrange
        self.board.clear()
        
        # Act
        piece = Empty()
        
        # Assert
        self.assertEqual(piece.type, EMPTY)
        self.assertEqual(piece.color, NONE)
        self.assertEqual(piece.is_valid_move((0, 0), (0, 1), self.board), False)
        self.assertEqual(piece.get_line_of_sight((0, 0), (0, 1), self.board), [])
        self.assertEqual(piece.get_valid_moves((0,0), self.board), [])

    def test_pawn_white(self):
        # Arrange
        self.board.clear()
        self.board.board[board_to_coord("E1")] = King(WHITE)
        
        # Act
        piece = Pawn(WHITE)
        self.board.board[board_to_coord("A2")] = piece
        
        # Assert
        self.assertEqual(piece.type, PAWN)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("A2"), board_to_coord("A3"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("A2"), board_to_coord("A4"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("A2"), board_to_coord("A5"), self.board), False)
        self.assertEqual(piece.is_valid_move(board_to_coord("A2"), board_to_coord("B3"), self.board), False)
        self.assertEqual(piece.get_line_of_sight(board_to_coord("A2"), board_to_coord("A4"), self.board), [])
        self.assertEqual(piece.get_valid_moves(board_to_coord("A2"), self.board), [(board_to_coord("A2"), board_to_coord("A3")), (board_to_coord("A2"), board_to_coord("A4"))])
        self.board.board[board_to_coord("B3")] = Pawn(BLACK)
        self.assertEqual(piece.is_valid_move(board_to_coord("A2"), board_to_coord("B3"), self.board), True)
        self.assertEqual(piece.get_valid_moves(board_to_coord("A2"), self.board), [(board_to_coord("A2"), board_to_coord("B3")), (board_to_coord("A2"), board_to_coord("A3")), (board_to_coord("A2"), board_to_coord("A4"))])

    def test_pawn_black(self):
        # Arrange
        self.board.clear()
        self.board.current_player = BLACK
        self.board.board[board_to_coord("E8")] = King(BLACK)
        
        # Act
        piece = Pawn(BLACK)
        self.board.board[board_to_coord("A7")] = piece
        
        # Assert
        self.assertEqual(piece.type, PAWN)
        self.assertEqual(piece.color, BLACK)
        self.assertEqual(piece.is_valid_move(board_to_coord("A7"), board_to_coord("A6"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("A7"), board_to_coord("A5"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("A7"), board_to_coord("A4"), self.board), False)
        self.assertEqual(piece.is_valid_move(board_to_coord("A7"), board_to_coord("B6"), self.board), False)
        self.assertEqual(piece.get_line_of_sight(board_to_coord("A7"), board_to_coord("A5"), self.board), [])
        self.assertEqual(piece.get_valid_moves(board_to_coord("A7"), self.board), [(board_to_coord("A7"), board_to_coord("A6")), (board_to_coord("A7"), board_to_coord("A5"))])
        self.board.board[board_to_coord("B6")] = Pawn(WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("A7"), board_to_coord("B6"), self.board), True)
        self.assertEqual(piece.get_valid_moves(board_to_coord("A7"), self.board), [(board_to_coord("A7"), board_to_coord("B6")), (board_to_coord("A7"), board_to_coord("A6")), (board_to_coord("A7"), board_to_coord("A5"))])

    def test_knight(self):
            # Arrange
            self.board.clear()
            self.board.board[board_to_coord("F2")] = King(WHITE)
            
            # Act
            piece = Knight(WHITE)
            self.board.board[board_to_coord("E4")] = piece
            self.board.board[board_to_coord("G5")] = Pawn(BLACK)
            
            # Assert
            self.assertEqual(piece.type, KNIGHT)
            self.assertEqual(piece.color, WHITE)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("C3"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("C5"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("D2"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("D6"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("F2"), self.board), False) # King in the way
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("F6"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("G3"), self.board), True)
            self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("G5"), self.board), True) # Pawn capture
            self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("G5"), self.board), [])
            self.assertEqual(set(piece.get_valid_moves(board_to_coord("E4"), self.board)), set([(board_to_coord("E4"), board_to_coord("C3")), (board_to_coord("E4"), board_to_coord("C5")),
                                                                                                (board_to_coord("E4"), board_to_coord("D2")), (board_to_coord("E4"), board_to_coord("D6")),
                                                                                                (board_to_coord("E4"), board_to_coord("F6")),
                                                                                                (board_to_coord("E4"), board_to_coord("G3")), (board_to_coord("E4"), board_to_coord("G5"))]))

    def test_rook(self):
        # Arrange
        self.board.clear()
        self.board.board[board_to_coord("E1")] = King(WHITE)
        
        # Act
        piece = Rook(WHITE)
        self.board.board[board_to_coord("E4")] = piece
        self.board.board[board_to_coord("B4")] = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.type, ROOK)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("A4"), self.board), False) # Pawn in the way
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("B4"), self.board), True) # Pawn capture
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E1"), self.board), False) # King in the way
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E2"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E8"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H4"), self.board), True)
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("B4"), self.board), [board_to_coord("D4"), board_to_coord("C4")])
        self.assertEqual(set(piece.get_valid_moves(board_to_coord("E4"), self.board)), set([(board_to_coord("E4"), board_to_coord("D4")), (board_to_coord("E4"), board_to_coord("C4")), (board_to_coord("E4"), board_to_coord("B4")),
                                                                                             (board_to_coord("E4"), board_to_coord("F4")), (board_to_coord("E4"), board_to_coord("G4")), (board_to_coord("E4"), board_to_coord("H4")),
                                                                                             (board_to_coord("E4"), board_to_coord("E5")), (board_to_coord("E4"), board_to_coord("E6")), (board_to_coord("E4"), board_to_coord("E7")), (board_to_coord("E4"), board_to_coord("E8")),
                                                                                             (board_to_coord("E4"), board_to_coord("E3")), (board_to_coord("E4"), board_to_coord("E2"))]))

    def test_bishop(self):
        # Arrange
        self.board.clear()
        self.board.board[board_to_coord("B1")] = King(WHITE)
        
        # Act
        piece = Bishop(WHITE)
        self.board.board[board_to_coord("E4")] = piece
        self.board.board[board_to_coord("G6")] = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.type, BISHOP)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("A8"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("B1"), self.board), False) # King in the way
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("C2"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("G6"), self.board), True) # Pawn capture
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H1"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H7"), self.board), False) # Pawn in the way
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("G6"), self.board), [board_to_coord("F5")])
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("A8"), self.board), [board_to_coord("D5"), board_to_coord("C6"), board_to_coord("B7")])
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("H1"), self.board), [board_to_coord("F3"), board_to_coord("G2")])
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("C2"), self.board), [board_to_coord("D3")])
        self.assertEqual(set(piece.get_valid_moves(board_to_coord("E4"), self.board)), set([(board_to_coord("E4"), board_to_coord("F5")), (board_to_coord("E4"), board_to_coord("G6")),
                                                                                             (board_to_coord("E4"), board_to_coord("D3")), (board_to_coord("E4"), board_to_coord("C2")), 
                                                                                             (board_to_coord("E4"), board_to_coord("D5")), (board_to_coord("E4"), board_to_coord("C6")), (board_to_coord("E4"), board_to_coord("B7")),
                                                                                             (board_to_coord("E4"), board_to_coord("A8")), (board_to_coord("E4"), board_to_coord("F3")), (board_to_coord("E4"), board_to_coord("G2")),
                                                                                             (board_to_coord("E4"), board_to_coord("H1"))]))
        
    def test_queen(self):
        # Arrange
        self.board.clear()
        self.board.board[board_to_coord("B1")] = King(WHITE)
        
        # Act
        piece = Queen(WHITE)
        self.board.board[board_to_coord("E4")] = piece
        self.board.board[board_to_coord("G6")] = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.type, QUEEN)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("A4"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("A8"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("B1"), self.board), False) # King in the way
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("C2"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E1"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E8"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("G6"), self.board), True) # Pawn capture
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H1"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H4"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("H7"), self.board), False) # Pawn in the way
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("C2"), self.board), [board_to_coord("D3")])
        self.assertEqual(set(piece.get_valid_moves(board_to_coord("E4"), self.board)), set([(board_to_coord("E4"), board_to_coord("F5")), (board_to_coord("E4"), board_to_coord("G6")),
                                                                                             (board_to_coord("E4"), board_to_coord("F3")), (board_to_coord("E4"), board_to_coord("G2")), (board_to_coord("E4"), board_to_coord("H1")),
                                                                                             (board_to_coord("E4"), board_to_coord("D3")), (board_to_coord("E4"), board_to_coord("C2")), 
                                                                                             (board_to_coord("E4"), board_to_coord("D5")), (board_to_coord("E4"), board_to_coord("C6")), (board_to_coord("E4"), board_to_coord("B7")), (board_to_coord("E4"), board_to_coord("A8")),
                                                                                             (board_to_coord("E4"), board_to_coord("E5")), (board_to_coord("E4"), board_to_coord("E6")), (board_to_coord("E4"), board_to_coord("E7")), (board_to_coord("E4"), board_to_coord("E8")),
                                                                                             (board_to_coord("E4"), board_to_coord("E3")), (board_to_coord("E4"), board_to_coord("E2")), (board_to_coord("E4"), board_to_coord("E1")),
                                                                                             (board_to_coord("E4"), board_to_coord("F4")), (board_to_coord("E4"), board_to_coord("G4")), (board_to_coord("E4"), board_to_coord("H4")),
                                                                                             (board_to_coord("E4"), board_to_coord("D4")), (board_to_coord("E4"), board_to_coord("C4")), (board_to_coord("E4"), board_to_coord("B4")), (board_to_coord("E4"), board_to_coord("A4"))]))
    
    def test_king_movement(self):
        # Arrange
        self.board.clear()
        
        # Act
        piece = King(WHITE)
        self.board.board[board_to_coord("E4")] = piece
        self.board.board[board_to_coord("E6")] = Pawn(BLACK)
        
        # Assert
        self.assertEqual(piece.type, KING)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("D3"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("D4"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("D5"), self.board), True) # strictly legal, but not allowed
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E3"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("E5"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("F3"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("F4"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E4"), board_to_coord("F5"), self.board), True) # strictly legal, but not allowed
        self.assertEqual(piece.get_line_of_sight(board_to_coord("E4"), board_to_coord("D3"), self.board), [])
        self.assertEqual(set(piece.get_valid_moves(board_to_coord("E4"), self.board)), set([(board_to_coord("E4"), board_to_coord("D3")), (board_to_coord("E4"), board_to_coord("D4")),
                                                                                             (board_to_coord("E4"), board_to_coord("E3")), (board_to_coord("E4"), board_to_coord("E5")),
                                                                                             (board_to_coord("E4"), board_to_coord("F3")), (board_to_coord("E4"), board_to_coord("F4"))]))
        
    def test_king_castling(self):
        # Arrange
        self.board.clear()
        
        # Act
        piece = King(WHITE)
        self.board.board[board_to_coord("E1")] = piece
        self.board.board[board_to_coord("H1")] = Rook(WHITE)
        self.board.board[board_to_coord("A1")] = Rook(WHITE)
        
        # Assert
        self.assertEqual(piece.type, KING)
        self.assertEqual(piece.color, WHITE)
        self.assertEqual(piece.is_valid_move(board_to_coord("E1"), board_to_coord("C1"), self.board), True)
        self.assertEqual(piece.is_valid_move(board_to_coord("E1"), board_to_coord("G1"), self.board), True)
        self.assertEqual(piece.is_valid_castle(board_to_coord("E1"), board_to_coord("C1"), self.board), True)     
        self.assertEqual(piece.is_valid_castle(board_to_coord("E1"), board_to_coord("G1"), self.board), True)

if __name__ == "__main__":
    unittest.main()