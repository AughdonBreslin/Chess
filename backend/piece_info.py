from enum import Enum
from numpy import array

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
        if isinstance(other, Color):
            return self.name == other.name
        elif isinstance(other, int):
            return self.value == other
        else:
            raise TypeError("Invalid comparison: other must be a Color or an integer")
    
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

def board_to_coord(board: str) -> list[int, int]:
    return ord(board[1]) - ord('1'), ord(board[0]) - ord('A')

def coord_to_board(coord: list[int, int]) -> str:
    return chr(coord[1] + ord('A')) + str(coord[0] + 1)