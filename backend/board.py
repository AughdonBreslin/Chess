from pieces import *

class Board():
    def __init__(self, fen: str = None, board = []):
        self.current_player = WHITE
        self.board = array([[Empty() for j in range(8)] for i in range(8)])
        self.en_passant_target_square = ""
        self.half_move_clock = 0
        self.moves = 1
        if board:
            self.board = board
        elif fen:
            self.load_fen(fen)
        else:
            self.setup()

    def setup(self):
        self.board[0] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE), King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)]
        self.board[1] = [Pawn(WHITE) for _ in range(8)]
        self.board[6] = [Pawn(BLACK) for _ in range(8)]
        self.board[7] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK), King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)]

    def load_fen(self, fen: str):
        fen = fen.split(" ")
        board = fen[0].split("/")
        for i in range(8):
            j = 0
            for char in board[i]:
                if char.isdigit():
                    j += int(char)
                else:
                    self.board[7-i][j] = self.char_to_piece(char)
                    j += 1

        self.current_player = WHITE if fen[1] == "w" else BLACK

        castling_rights = fen[2]
        if castling_rights != "-":
            if "K" in castling_rights and self.board[0][7] == ROOK and self.board[0][4] == KING:
                self.board[0][7].can_castle = True
                self.board[0][4].can_castle = True
            if "Q" in castling_rights and self.board[0][0] == ROOK and self.board[0][4] == KING:
                self.board[0][0].can_castle = True
                self.board[0][4].can_castle = True
            if "k" in castling_rights and self.board[7][7] == ROOK and self.board[7][4] == KING:
                self.board[7][7].can_castle = True
                self.board[7][4].can_castle = True
            if "q" in castling_rights and self.board[7][0] == ROOK and self.board[7][4] == KING:
                self.board[7][0].can_castle = True
                self.board[7][4].can_castle = True

        self.en_passant_target_square = fen[3]
        self.half_move_clock = int(fen[4])
        self.moves = int(fen[5])
        


    def char_to_piece(self, char: str) -> ChessPiece:
        color = WHITE if char.isupper() else BLACK
        char = char.lower()
        return {
            "p": Pawn(color),
            "r": Rook(color),
            "n": Knight(color),
            "b": Bishop(color),
            "q": Queen(color),
            "k": King(color)
        }[char]

    def switch_player(self):
        if self.current_player == WHITE:
            for pawn_pos in self.find_pieces(PAWN, BLACK):
                self.board[pawn_pos].en_passantable = False
            self.current_player = BLACK
        else:
            for pawn_pos in self.find_pieces(PAWN, WHITE):
                self.board[pawn_pos].en_passantable = False 
            self.current_player = WHITE

    def all_valid_moves(self, verbose=False):
        all_valid_moves = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece.color == self.current_player:
                    valid_moves = piece.get_valid_moves((i, j), self)
                    if verbose:
                        print(f"{piece}({coord_to_board((i, j))}):", [f"{coord_to_board(start_pos)} -> {coord_to_board(end_pos)}" for (start_pos, end_pos) in valid_moves])
                    all_valid_moves += valid_moves
        return all_valid_moves
    
    def castle_rook(self, start_pos, end_pos, king):
        direction = end_pos[1] > start_pos[1]
        rook_start_pos = (7*self.current_player, 7*direction)
        rook_end_pos = (7*self.current_player, 7*direction + 2*(-1)**direction + 1 - direction)
        self.board[rook_end_pos] = self.board[rook_start_pos]
        self.board[rook_end_pos].can_castle = False
        self.board[rook_start_pos] = Empty()
        king.can_castle = False

    def move(self, start_pos, end_pos):
        piece = self.board[start_pos]
        if piece == EMPTY:
            print(f"Invalid: No piece at {coord_to_board(start_pos)}")
            return False
        
        if piece.color != self.current_player:
            print(f"Invalid: This is not your piece.")
            return False
    
        if not piece.is_valid_move(start_pos, end_pos, self):
            print(f"Invalid: Your {piece} cannot move like this.")
            return False
        
        if (start_pos, end_pos) not in piece.get_valid_moves(start_pos, self):
            print(f"Invalid: Your king will be in check if you move like this.")
            return False

        if piece == PAWN and end_pos[0] == 7*(1-piece.color):
            piece = piece.promotion()
            if not piece:
                print("Invalid promotion.")
                return False
        elif piece == KING and abs(end_pos[1] - start_pos[1]) == 2:
            if self.check(start_pos) or not piece.is_valid_castle(start_pos, end_pos, self):
                return False
            self.castle_rook(start_pos, end_pos, piece)
        
        if self.board[end_pos] != EMPTY or piece == PAWN:
            self.half_move_clock = 0
        else:
            self.half_move_clock += 1

        self.board[start_pos] = Empty()
        self.board[end_pos] = piece

        if piece == KING or piece == ROOK:
            piece.can_castle = False

        self.switch_player()
        self.moves += 0.5

    def check(self, king_pos):
        attackers_positions = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece.color != self.current_player and piece.is_valid_move((i,j), king_pos, self):
                    attackers_positions.append((i,j))
                    # print(f"Check: {self.current_player} king is in check at {coord_to_board(king_pos)} by {piece.color} {piece.type} at {coord_to_board((i, j))}.")
        if len(attackers_positions) > 0:
            # print("Attacker(s) positions:", [f"{self.board[pos]}({coord_to_board(pos)})" for pos in attackers_positions])
            pass
        return attackers_positions
    
    def find_piece(self, piece, color=NONE):
        if color == NONE:
            color = self.current_player

        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == piece and self.board[i][j].color == color:
                    # print(f"Piece {self.board[i][j]} found at {coord_to_board((i, j))}.")
                    return (i, j)
        print(f"Warning: Piece {self.current_player} {piece} not found.")
        return ()
    
    def find_pieces(self, piece, color=NONE):
        if color == NONE:
            color = self.current_player
        piece_positions = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == piece and self.board[i][j].color == color:
                    # print(f"Piece {self.board[i][j]} found at {coord_to_board((i, j))}.")
                    piece_positions.append((i, j))
        if not piece_positions:
            print(f"Warning: Piece {color} {piece} not found.")
        return piece_positions
    
    def try_move(self, start_pos, end_pos):
        original = self.board[end_pos]
        self.board[end_pos] = self.board[start_pos]
        self.board[start_pos] = Empty()
        return original

    def undo_move(self, start_pos, end_pos, moved_piece, original):
        self.board[start_pos] = moved_piece
        self.board[end_pos] = original
    
    def check_for_check(self, start_pos, end_pos, list):
        piece = self.board[start_pos]
        potential_capture = self.try_move(start_pos, end_pos)
        if not self.check(self.find_piece(KING, self.current_player)):
            list.append((start_pos, end_pos))
        self.undo_move(start_pos, end_pos, piece, potential_capture)

    def checkmate(self, verbose=False):
        king_pos = self.find_piece(KING)
        king = self.board[king_pos]
        if not king_pos:
            print(f"Error: Cannot find king; illegal position.")
            return False
        
        attackers_positions = self.check(king_pos)
        if not attackers_positions:
            return False
        
        capturing_moves = []
        blocking_moves = []
        if len(attackers_positions) == 1:
            attacker_pos = attackers_positions[0]
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    piece = self.board[i][j]
                    if piece.color != self.current_player:
                        continue
                    if piece.is_valid_move((i, j), attacker_pos, self):
                        if piece == KING:
                            self.check_for_check((i, j), attacker_pos, capturing_moves)
                        else:
                            capturing_moves.append(((i, j), attacker_pos))
            for square in self.board[attacker_pos].get_line_of_sight(attacker_pos, king_pos, self):
                for i in range(len(self.board)):
                    for j in range(len(self.board[i])):
                        piece = self.board[i][j]
                        if piece != EMPTY and piece != KING and piece.color == self.current_player and piece.is_valid_move((i,j), square, self):
                            blocking_moves.append(((i, j), square))
        running_moves = [move for move in king.get_valid_moves(king_pos, self) if move not in capturing_moves]

        if verbose:
            print("Capturing Moves:", [f"{coord_to_board(start)} -> {coord_to_board(end)}" for (start, end) in capturing_moves])
            print("Blocking Moves:", [f"{coord_to_board(start)} -> {coord_to_board(end)}" for (start, end) in blocking_moves])
            print("Running Moves:", [f"{coord_to_board(start)} -> {coord_to_board(end)}" for (start, end) in running_moves])
        return not (capturing_moves or blocking_moves or running_moves)

    def stalemate(self, verbose=False):
        king_pos = self.find_piece(KING)
        if not self.check(king_pos) and len(self.all_valid_moves(verbose)) == 0:
            # print(f"{self.current_player} has been stalemated!")
            return True
        return False

    def print_board(self):
        print("  | A | B | C | D | E | F | G | H |")
        print("-" * 37)
        for i in range(8):
            print(str(i+1) + " | ", end="")
            for j in range(8):
                print(str(self.board[i][j]) + " | ", end="")
            print(str(i+1), end="")
            print("\n" + "-" * 37)
        print("  | A | B | C | D | E | F | G | H |")