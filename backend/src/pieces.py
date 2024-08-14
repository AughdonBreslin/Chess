import numpy as np # type: ignore

from piece_info import *

class ChessPiece:
    def __init__(self, color: Color, type: PieceType):
        self.color = color
        self.type = type

    def __eq__(self, other):
        match other:
            case PieceType():
                return self.type == other
            case Color():
                return self.color == other
            case ChessPiece():
                return self.type == other.type and self.color == other.color
            case bad:
                raise Exception(f"Error: Testing equality against incompatible type {bad}.")

    def __ne__(self, other):
        return self.type != other

    def __str__(self):
        return PIECE_STR[self.type][self.color.value]
    
    def out_of_bounds(self, position: Tuple[int, int]):
        return position[0] < 0 or position[0] > 7 or position[1] < 0 or position[1] > 7
    
class Empty(ChessPiece):
    def __init__(self):
        super().__init__(NONE, EMPTY)

    def is_valid_move(self, start_pos, end_pos, board):
        return False
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        return []
    
    def get_valid_moves(self, start_pos, board):
        return []
    
class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color, ROOK)
        self.can_castle = True

    def is_valid_move(self, start_pos, end_pos, board):
        # Check out of bounds
        if super().out_of_bounds(start_pos) or super().out_of_bounds(end_pos):
            # print("Out of bounds.")
            return False
        
        # If both or neither change, invalid
        if (start_pos[0] == end_pos[0]) == (start_pos[1] == end_pos[1]):
            # print("Move is not horizontal or vertical.")
            return False
        
        # Check if end position is a friendly piece
        if board.board[end_pos].color == self.color:
            # print(f"Rook is trying to capture its own {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
            return False
        
        # Check if the path is blocked
        axis = start_pos[0] == end_pos[0]
        if start_pos[0] == end_pos[0]:
            for i in range(min(start_pos[1], end_pos[1]) + 1, max(start_pos[1], end_pos[1])):
                if board.board[start_pos[0]][i] != EMPTY:
                    # print(f"Invalid: Path is blocked by {str(board.board[start_pos[0]][i])} at {str((start_pos[0], i))}.")
                    return False
        else:
            for i in range(min(start_pos[0], end_pos[0]) + 1, max(start_pos[0], end_pos[0])):
                if board.board[i][start_pos[1]] != EMPTY:
                    # print(f"Path is blocked by {str(board.board[i][start_pos[1]])} at {str((i, start_pos[1]))}.")
                    return False
        return True
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        if self.is_valid_move(start_pos, end_pos, board):
            axis = start_pos[0] == end_pos[0]
            dir = 1 if end_pos[axis] > start_pos[axis] else -1
            print(start_pos, end_pos, range(start_pos[axis]+dir, end_pos[axis], dir))
            return [(axis*start_pos[0] + (1-axis)*dir*i, (1-axis)*start_pos[1] + axis*dir*i) for i in range(start_pos[axis]+dir, end_pos[axis], dir)]
        return []
    
    def get_valid_moves(self, start_pos, board):
        moves = []
        for axis in [0, 1]:
            for dir in [-1, 1]:
                end_pos = (start_pos[0] + (1-axis)*dir, start_pos[1] + axis*dir)
                while not super().out_of_bounds(end_pos) and board.board[end_pos].color != self.color:
                    board.check_for_check(start_pos, end_pos, moves)
                    if board.board[end_pos].color == 1-self.color:
                        break
                    end_pos = (end_pos[0] + (1-axis)*dir, end_pos[1] + axis*dir)
        return moves
    
class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color, BISHOP)

    def is_valid_move(self, start_pos, end_pos, board):
        # Check out of bounds
        if super().out_of_bounds(start_pos) or super().out_of_bounds(end_pos):
            # print("Out of bounds.")
            return False
        
        # If abs(direction changes) are not the same or neither change, invalid
        if abs(end_pos[0] - start_pos[0]) != abs(end_pos[1] - start_pos[1]) or abs(end_pos[0] - start_pos[0]) == 0:
            # print("Move is not diagonal.")
            return False
        
        # Check if end position is a friendly piece
        if board.board[end_pos].color == self.color:
            # print(f"Bishop is trying to capture its own {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
            return False
        
        # Check if the path is blocked
        up = end_pos[0] > start_pos[0]
        right = end_pos[1] > start_pos[1]

        for i in range(1, (start_pos[0] - end_pos[0])*(-1)**up):
            if board.board[start_pos[0] - i*(-1)**up][start_pos[1] - i*(-1)**right] != EMPTY:
                # print(f"Path is blocked by {board.board[start_pos[0] - i*(-1)**up][start_pos[1] - i*(-1)**right]} at {coord_to_board((start_pos[0] - i*(-1)**up, start_pos[1] - i*(-1)**right))}")
                return False
        
        return True
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        if self.is_valid_move(start_pos, end_pos, board):
            up = end_pos[0] > start_pos[0]
            right = end_pos[1] > start_pos[1]
            return [(start_pos[0] - i*(-1)**up, start_pos[1] - i*(-1)**right) for i in range(1, (start_pos[0] - end_pos[0])*(-1)**up)]

    def get_valid_moves(self, start_pos, board):
        moves = []
        for y in [-1, 1]:
            for x in [-1, 1]:
                end_pos = (start_pos[0] + y, start_pos[1] + x)
                while not super().out_of_bounds(end_pos) and board.board[end_pos].color != self.color:
                    board.check_for_check(start_pos, end_pos, moves)
                    if board.board[end_pos].color == 1-self.color:
                        break
                    end_pos = (end_pos[0] + y, end_pos[1] + x)
        return moves

class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color, QUEEN)

    def is_valid_move(self, start_pos, end_pos, board):
        # Check queen moves through rook and bishop
        return Rook(self.color).is_valid_move(start_pos, end_pos, board) or Bishop(self.color).is_valid_move(start_pos, end_pos, board)
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        if start_pos[0] == end_pos[0] or start_pos[1] == end_pos[1]:
            return Rook(self.color).get_line_of_sight(start_pos, end_pos, board)
        return Bishop(self.color).get_line_of_sight(start_pos, end_pos, board)

    def get_valid_moves(self, start_pos, board):
        return Rook(self.color).get_valid_moves(start_pos, board) + Bishop(self.color).get_valid_moves(start_pos, board)
    
class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color, KNIGHT)

    def is_valid_move(self, start_pos, end_pos, board):
        # Check out of bounds
        if super().out_of_bounds(start_pos) or super().out_of_bounds(end_pos):
            # print("Out of bounds.")
            return False
        
        # Check if end position is a friendly piece
        if board.board[end_pos].color == self.color:
            # print(f"Knight is trying to capture its own {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
            return False

        # Check if not L-shaped
        if not ((abs(end_pos[0] - start_pos[0]) == 2 and abs(end_pos[1] - start_pos[1]) == 1) or \
            (abs(end_pos[0] - start_pos[0]) == 1 and abs(end_pos[1] - start_pos[1]) == 2)):
            # print("Move is not L-shaped.")
            return False
        
        return True

    def get_line_of_sight(self, start_pos, end_pos, board):
        return []
        
    def get_valid_moves(self, start_pos, board):
        moves = []
        for y in [-1, 1]:
            for x in [-1, 1]:
                for dom in [1, 2]:
                    end_pos = (start_pos[0] + y*dom, start_pos[1] + x*(3-dom))
                    if not super().out_of_bounds(end_pos) and board.board[end_pos].color != self.color:
                        board.check_for_check(start_pos, end_pos, moves)
        return moves

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color, PAWN)
        self.en_passantable = False

    def promotion(self):
        return [Queen(self.color), Rook(self.color), Bishop(self.color), Knight(self.color)][np.random.randint(0, 4)]
        # piece = input("Enter the piece to which your pawn promotes (Q, R, B, N, enter to escape): ").lower()
        # if piece == "queen" or piece == "q":
        #     return Queen(self.color)
        # elif piece == "rook" or piece == "r":
        #     return Rook(self.color)
        # elif piece == "bishop" or piece == "b":
        #     return Bishop(self.color)
        # elif piece == "knight" or piece == "n":
        #     return Knight(self.color)
        # else:
        #     # print("Invalid piece.")
        #     return False

    def is_valid_move(self, start_pos, end_pos, board):
        # Check out of bounds
        if super().out_of_bounds(start_pos) or super().out_of_bounds(end_pos):
            # print("Out of bounds.")
            return False
        
        if not ((end_pos[0] - start_pos[0] == 1*(-1)**self.color and end_pos[1] == start_pos[1]) or \
                end_pos[0] - start_pos[0] == 2*(-1)**self.color and end_pos[1] == start_pos[1] or \
                end_pos[0] - start_pos[0] == 1*(-1)**self.color and abs(end_pos[1] - start_pos[1]) == 1):
            # print("Pawn is trying to make an unrecognized move.")
            return False
        
        # 1 step vertical
        if end_pos[0] - start_pos[0] == 1*(-1)**self.color and end_pos[1] == start_pos[1]:
            if board.board[end_pos[0]][end_pos[1]] != EMPTY:
                # print("Pawn is trying to move forward one step but is blocked.")
                return False
        # print("Pawn is moving forward one step and is not blocked.")
        # 2 step vertical
        elif end_pos[0] - start_pos[0] == 2*(-1)**self.color and end_pos[1] == start_pos[1]:
            if start_pos[0] != 1*(-1)**self.color % (len(board.board) - 1):
                # print("Pawn is trying to move forward two steps but has already moved.")
                return False
            elif board.board[end_pos] != EMPTY:
                # print(f"Pawn is trying to move forward two steps but is blocked by {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
                return False
            elif board.board[end_pos[0] - 1*(-1)**self.color][end_pos[1]] != EMPTY:
                # print(f"Pawn is trying to move forward two steps but is blocked by {str(board.board[end_pos[0] - 1*(-1)**self.color][end_pos[1]])} at {str((end_pos[0] - 1*(-1)**self.color, end_pos[1]))}.")
                return False
            else:
                # print("Pawn moves forward two steps and is not blocked.")
                self.en_passantable = True  

        # Capture
        elif end_pos[0] - start_pos[0] == 1*(-1)**self.color and abs(end_pos[1] - start_pos[1]) == 1:
            if board.board[end_pos] == EMPTY and board.board[start_pos[0]][end_pos[1]] == PAWN and board.board[start_pos[0]][end_pos[1]].en_passantable:
                # print(f"Pawn moves diagonally one step and en passants {str(board.board[start_pos[0]][end_pos[1]])} at {str((start_pos[0], end_pos[1]))}.")
                board.board[start_pos[0]][end_pos[1]] = Empty()
                return True
            elif board.board[end_pos] == EMPTY:
                # print("Pawn is trying to move diagonally one step but is not capturing.")
                return False
            elif board.board[end_pos].color == self.color:
                # print(f"Pawn is trying to move diagonally one step but is trying to capture its own {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
                return False
        return True
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        return []
    
    def get_valid_moves(self, start_pos, board):
        moves = []
        on_start = start_pos[0] == 1*(-1)**self.color % (len(board.board) - 1)
        # captures
        for x in [-1, 1]:
            end_pos = (start_pos[0] + 1*(-1)**self.color, start_pos[1] + x)
            if not super().out_of_bounds(end_pos) and board.board[end_pos].color == 1 - self.color:
                board.check_for_check(start_pos, end_pos, moves)
        # forward
        end_pos = (start_pos[0] + 1*(-1)**self.color, start_pos[1])
        if not super().out_of_bounds(end_pos) and board.board[end_pos].color == NONE:
            board.check_for_check(start_pos, end_pos, moves)
            if on_start:
                end_pos = (start_pos[0] + 2*(-1)**self.color, start_pos[1])
                if board.board[end_pos] == EMPTY:
                    board.check_for_check(start_pos, end_pos, moves)
        return moves

class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color, KING)
        self.can_castle = True

    def is_valid_move(self, start_pos, end_pos, board):
        # Check out of bounds
        if super().out_of_bounds(start_pos) or super().out_of_bounds(end_pos):
            # print("Out of bounds.")
            return False
        
        # Check if castling
        if self.can_castle and start_pos[0] == end_pos[0] and abs(end_pos[1] - start_pos[1]) == 2:
            # print("King is castling.")
            return True
        
        if board.board[end_pos].color == self.color:
            # print(f"King is trying to capture its own {str(board.board[end_pos[0]][end_pos[1]])} at {str(end_pos)}.")
            return False
        
        if (abs(end_pos[0] - start_pos[0]) > 1 or abs(end_pos[1] - start_pos[1]) > 1) and \
            not (self.can_castle and start_pos[0] == end_pos[0] and abs(end_pos[1] - start_pos[1]) == 2):
            # print("King is trying to move more than one step.")
            return False
        
        if end_pos[0] == start_pos[0] and end_pos[1] == start_pos[1]:
            # print("King is trying to move to the same position.")
            return False
        return True
    
    def is_valid_castle(self, start_pos, end_pos, board):
        if board.check(start_pos):
            # print("Cannot castle: King is in check.")
            return False
        if start_pos[0] != 7*self.color or start_pos[1] != 3:
            # print(f"Cannot castle: King not in starting square at {coord_to_board((7*self.color, 4))}.")
            return False
        if not self.can_castle:
            # print(f"Cannot castle: At some point king has moved from {coord_to_board((7*self.color, 4))}.")
            return False
        if end_pos[0] != start_pos[0] or abs(end_pos[1] - start_pos[1]) != 2:
            # print("Cannot castle: King is not moving two squares.")
            return False
        
        king_side = end_pos[1] < start_pos[1]
        rook_pos = (start_pos[0], 7*king_side)
        rook = board.board[rook_pos]
        if rook != ROOK:
            # print(f"Cannot castle: No rook found at {coord_to_board(rook_pos)}.")
            return False
        if not rook.can_castle:
            # print(f"Cannot castle: At some point rook has moved from {coord_to_board(rook_pos)}.")
            return False
        
        if board.board[start_pos[0]][start_pos[1] + 1*(-1)**(king_side)] != EMPTY or \
            board.board[start_pos[0]][start_pos[1] + 2*(-1)**(king_side)] != EMPTY or \
            (not king_side and board.board[start_pos[0]][start_pos[1] + 3*(-1)**(king_side)] != EMPTY):
            # print("Cannot castle: Path is not clear.")
            return False
        
        if board.check((start_pos[0], start_pos[1] + 1*(-1)**king_side)) or board.check(end_pos):
            # print("Cannot castle: Moving through or into check.")
            return False
        
        # print(f"{self.color} can castle {['queen', 'king'][king_side]} side.")
        return True
    
    def get_line_of_sight(self, start_pos, end_pos, board):
        return []
    
    def get_valid_moves(self, start_pos, board):
        moves = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x == 0 and y == 0:
                    continue
                end_pos = (start_pos[0] + y, start_pos[1] + x)
                if not super().out_of_bounds(end_pos) and board.board[end_pos].color != self.color:
                    board.check_for_check(start_pos, end_pos, moves)
        for dir in [-2, 2]:
            end_pos = (start_pos[0], start_pos[1] + dir)
            if self.is_valid_castle(start_pos, end_pos, board):
                moves.append((start_pos, end_pos))
        return moves