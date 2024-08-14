from enum import Enum

class PieceType(Enum):
    EMPTY = "Empty"
    PAWN = "Pawn"
    ROOK = "Rook"
    KNIGHT = "Knight"
    BISHOP = "Bishop"
    QUEEN = "Queen"
    KING = "King"

    def __str__(self) -> str:
        return self.value

class Color(Enum):
    NONE = -1
    WHITE = 0
    BLACK = 1

    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        match other:
            case Color():
                return self.name == other.name
            case int():
                return self.value == other
            case bad:
                raise TypeError(f"Error: Testing equality against incompatible type {bad}.")
            
    def __ne__(self, other) -> bool:
        match other:
            case Color():
                return self.name != other.name
            case int():
                return self.value != other
            case bad:
                raise TypeError(f"Error: Testing inequality against incompatible type {bad}.")
    
    def __index__(self) -> int:
        return self.value

    def __sub__(self, other) -> int:
        return self.value - other
    
    def __rsub__(self, other) -> int:
        return other - self.value
    
    def __mul__(self, other) -> int:
        return self.value * other
    
    def __rmul__(self, other) -> int:
        return other * self.value
        
    def __rpow__(self, other) -> int:
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

PIECE_FEN: dict[PieceType, tuple[str, str]] = {
    EMPTY: (".", "."),
    PAWN: ("P", "p"),
    ROOK: ("R", "r"),
    BISHOP: ("B", "b"),
    QUEEN: ("Q", "q"),
    KING: ("K", "k"),
    KNIGHT: ("N", "n")
}

def board_to_coord(board: str) -> tuple[int, int]:
    file = board[0].upper()
    rank = board[1]
    return ord(rank) - ord('1'), 7 - (ord(file) - ord('A'))

def coord_to_board(coord: tuple[int, int]) -> str:
    return chr(7 - coord[1] + ord('A')) + str(coord[0] + 1)