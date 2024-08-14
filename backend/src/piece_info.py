from enum import Enum
from typing import Tuple

class PieceType(Enum):
    EMPTY = "empty"
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

    def __str__(self):
        return self.name

class Color(Enum):
    NONE = -1
    WHITE = 0
    BLACK = 1

    def __str__(self):
        return self.name
    
    def __int__(self):
        return self.value
    
    def __eq__(self, other):
        match other:
            case Color():
                return self.name == other.name
            case int():
                return self.value == other
            case bad:
                raise TypeError(f"Error: Testing equality against incompatible type {bad}.")
    
    def __sub__(self, other):
        return self.value - other
    
    def __rsub__(self, other):
        return other - self.value
    
    def __mul__(self, other):
        return self.value * other
    
    def __rmul__(self, other):
        return other * self.value
        
    def __rpow__(self, other):
        return other ** self.value

NONE, BLACK, WHITE = Color.NONE, Color.BLACK, Color.WHITE
EMPTY, PAWN, ROOK, BISHOP, QUEEN, KING, KNIGHT = PieceType.EMPTY, PieceType.PAWN, PieceType.ROOK, PieceType.BISHOP, PieceType.QUEEN, PieceType.KING, PieceType.KNIGHT

PIECE_STR: dict[PieceType, tuple[str, str]] = {
    EMPTY: (" ", " "),
    PAWN: ("♟", "♙"),
    ROOK: ("♜", "♖"),
    BISHOP: ("♝", "♗"),
    QUEEN: ("♛", "♕"),
    KING: ("♚", "♔"),
    KNIGHT: ("♞", "♘")
}

FEN_MAP: dict[str, PieceType] = {
    "p": PAWN,
    "r": ROOK,
    "b": BISHOP,
    "q": QUEEN,
    "k": KING,
    "n": KNIGHT,
}

def board_to_coord(board: str) -> Tuple[int, int]:
    file = board[0].upper()
    rank = board[1]
    return ord(rank) - ord('1'), 7 - (ord(file) - ord('A'))

def coord_to_board(coord: Tuple[int, int]) -> str:
    return chr(7 - coord[1] + ord('A')) + str(coord[0] + 1)