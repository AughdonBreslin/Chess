import numpy as np

from itertools import product

from piece_info import Color, PieceType, PIECE_STR, EMPTY, ROOK, BISHOP, \
                       QUEEN, KNIGHT, PAWN, KING, NONE, WHITE, BLACK

class ChessPiece:
    def __init__(self, color: Color, type: PieceType, can_castle: bool = None) -> None:
        self.color = color
        self.type = type
        self.can_castle = can_castle

    def __eq__(self, other) -> bool:
        match other:
            case ChessPiece():
                return self.color == other.color and self.type == other.type and self.can_castle == other.can_castle
            case Color():
                return self.color == other
            case int():
                return self.color == other
            case PieceType():
                return self.type == other
            case bad:
                raise TypeError(f"Error: Testing equality against incompatible type {bad}.")
    
    def __ne__(self, other) -> bool:
        match other:
            case ChessPiece():
                return self.color != other.color or self.type != other.type
            case Color():
                return self.color != other
            case int():
                return self.color != other
            case PieceType():
                return self.type != other
            case bad:
                raise TypeError(f"Error: Testing inequality against incompatible type {bad}.")
            
    def __repr__(self) -> str:
        return PIECE_STR[self.type][self.color]
    
    @staticmethod
    def out_of_bounds(position: tuple[int, int]) -> bool:
        return position[0] < 0 or position[0] > 7 or position[1] < 0 or position[1] > 7

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        return False

    def moves(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        return []
    
    def line_of_sight(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return []
    
class Empty(ChessPiece):
    def __init__(self) -> None:
        super().__init__(NONE, EMPTY)
    
class Rook(ChessPiece):
    def __init__(self, color, can_castle=False) -> None:
        super().__init__(color, ROOK, can_castle)
        self.can_castle = can_castle

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        return (start_pos[0] == end_pos[0]) != (start_pos[1] == end_pos[1])
    
    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return [(start_pos[0], i) for i in range(8) if i != start_pos[1]] + \
               [(i, start_pos[1]) for i in range(8) if i != start_pos[0]]
    
    def line_of_sight(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list[tuple[int, int]]:
        if not self.can_move(start_pos, end_pos):
            return []
        return [(start_pos[0], i) for i in range(min(start_pos[1], end_pos[1]) + 1, max(start_pos[1], end_pos[1]))] if start_pos[0] == end_pos[0] else \
                [(i, start_pos[1]) for i in range(min(start_pos[0], end_pos[0]) + 1, max(start_pos[0], end_pos[0]))]
    
class Bishop(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color, BISHOP)

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        return abs(start_pos[0] - end_pos[0]) == abs(start_pos[1] - end_pos[1]) and start_pos != end_pos
    
    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        # minor diagonal, major diagonal
        return [(start_pos[0] + i, start_pos[1] + i) for i in range(0 - min(start_pos), 7 - max(start_pos) + 1) if i != 0] + \
               [(start_pos[0] - i, start_pos[1] + i) for i in range(-min(7 - start_pos[0], start_pos[1]), min(start_pos[0], 7 - start_pos[1]) + 1) if i != 0]
    
    def line_of_sight(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list[tuple[int, int]]:
        if not self.can_move(start_pos, end_pos):
            return []
        up = 1 if end_pos[0] > start_pos[0] else -1
        right = 1 if end_pos[1] > start_pos[1] else -1
        return [(start_pos[0] + i, start_pos[1] + j) for (i, j) in \
                zip(range(up, end_pos[0] - start_pos[0], up), range(right, end_pos[1] - start_pos[1], right))]
    
class Queen(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color, QUEEN)

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        return Rook(self.color).can_move(start_pos, end_pos) or \
             Bishop(self.color).can_move(start_pos, end_pos)
    
    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return Rook(self.color).moves(start_pos) + \
             Bishop(self.color).moves(start_pos)
    
    def line_of_sight(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list[tuple[int, int]]:
        if not self.can_move(start_pos, end_pos):
            raise ValueError(f"Queen at {start_pos} cannot move to {end_pos}.")
        return Bishop(self.color).line_of_sight(start_pos, end_pos) + \
            Rook(self.color).line_of_sight(start_pos, end_pos)
             

class Knight(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color, KNIGHT)

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        return (abs(start_pos[0] - end_pos[0]) == 2 and abs(start_pos[1] - end_pos[1]) == 1) or \
               (abs(start_pos[0] - end_pos[0]) == 1 and abs(start_pos[1] - end_pos[1]) == 2)
    
    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return [(start_pos[0] + i*k, start_pos[1] + j*(3-k)) for (i, j, k) in product([-1, 1], [-1, 1], [1, 2]) \
                if not self.out_of_bounds((start_pos[0] + i*k, start_pos[1] + j*(3-k)))]

class Pawn(ChessPiece):
    def __init__(self, color) -> None:
        super().__init__(color, PAWN)

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        
        return (end_pos[0] - start_pos[0] == (-1)**self.color and end_pos[1] == start_pos[1]) or \
               (end_pos[0] - start_pos[0] == 2*(-1)**self.color and end_pos[1] == start_pos[1] and start_pos[0] == 1 + 5*self.color) or \
               (end_pos[0] - start_pos[0] == (-1)**self.color and abs(end_pos[1] - start_pos[1]) == 1)

    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]] | list[tuple[int, int, str]]:
        if start_pos[0] + (-1)**self.color == 7*(1 - self.color):
            return [(start_pos[0] + (-1)**self.color, start_pos[1], p) for p in ["q", "r", "b", "n"]]
        return [(start_pos[0] + (-1)**self.color, start_pos[1])] + \
               ([(start_pos[0] + 2*(-1)**self.color, start_pos[1])] if start_pos[0] == 1 + 5*self.color  else []) + \
               self.attack_options(start_pos)
    
    def attack_options(self, start_pos: tuple[int, int]) -> list[tuple[int, int]] | list[tuple[int, int, str]]:
        if start_pos[0] + (-1)**self.color == 7*(1 - self.color):
            return [(start_pos[0] + (-1)**self.color, start_pos[1] + i, p) for p in ["q", "r", "b", "n"] for i in [-1, 1] \
                if not self.out_of_bounds((start_pos[0] + (-1)**self.color, start_pos[1] + i))]
        return [(start_pos[0] + (-1)**self.color, start_pos[1] + i) for i in [-1, 1] \
                if not self.out_of_bounds((start_pos[0] + (-1)**self.color, start_pos[1] + i))]

class King(ChessPiece):
    def __init__(self, color, can_castle=False) -> None:
        super().__init__(color, KING, can_castle)
        self.can_castle = can_castle

    def can_move(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> bool:
        if self.out_of_bounds(start_pos) or self.out_of_bounds(end_pos):
            return False
        
        # moving one, castling
        return abs(start_pos[0] - end_pos[0]) <= 1 and abs(start_pos[1] - end_pos[1]) <= 1 and not (start_pos[0] == end_pos[0] and start_pos[1] == end_pos[1]) or \
                start_pos == (7*self.color, 3) and self.can_castle and abs(start_pos[1] - end_pos[1]) == 2 and start_pos[0] == end_pos[0]

    def moves(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return [(start_pos[0] + i, start_pos[1] + j) for i in [-1, 0, 1] for j in [-1, 0, 1] \
                if not self.out_of_bounds((start_pos[0] + i, start_pos[1] + j)) and not (i == 0 and j == 0)] + \
                self.castling_options(start_pos)
    
    def castling_options(self, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
        if start_pos != (7*self.color, 3):
            return []
        return [(start_pos[0], start_pos[1] + 2*i) for i in [-1, 1]] if self.can_castle else []

FEN_MAP: dict[str, ChessPiece] = {
    "p": Pawn,
    "r": Rook,
    "b": Bishop,
    "q": Queen,
    "k": King,
    "n": Knight,
}