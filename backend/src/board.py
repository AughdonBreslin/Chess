from collections import Counter

from piece_info import PIECE_FEN, PAWN, coord_to_board, board_to_coord
from pieces import np, FEN_MAP, ChessPiece, EMPTY, KING, ROOK, PieceType, Color, WHITE, BLACK, FEN_MAP, Empty, Pawn, Rook, King, Knight, Bishop, Queen

class Board:
    def __init__(self, fen=None) -> None:
        self.load_fen(fen) if fen else self.setup()

    def __getitem__(self, position: tuple[int, int]) -> ChessPiece:
        return self.board[position]
    
    def __setitem__(self, index: int, value: list[ChessPiece]) -> None:
        self.board[index] = value

    def __len__(self) -> int:
        return len(self.board)

    def __str__(self) -> str:
        return self.chessboard()
    
    def __repr__(self) -> str:
        return self.chessboard() + self.info()
    
    def clear(self) -> None:
        self.board = np.array([[Empty() for _ in range(8)] for _ in range(8)])
        self.current_player = WHITE
        self.en_passant_square = "-"
        self.halfmove_clock = 0
        self.history = []
        self.move_num = 1
        self.fen_counter = Counter()

    def setup(self) -> None:
        self.clear()
        self.board[0] = [Rook(WHITE, True), Knight(WHITE), Bishop(WHITE), King(WHITE, True),
                         Queen(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE, True)]
        self.board[1] = [Pawn(WHITE) for _ in range(8)]
        self.board[6] = [Pawn(BLACK) for _ in range(8)]
        self.board[7] = [Rook(BLACK, True), Knight(BLACK), Bishop(BLACK), King(BLACK, True),
                         Queen(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK, True)]

    def char_to_piece(self, char: str) -> ChessPiece:
        return FEN_MAP[char.lower()]

    def load_fen(self, fen: str) -> None:
        self.clear()
        fen = fen.split()
        board = fen[0].split("/")

        if len(board) != 8:
            raise ValueError("Invalid FEN string.")
        for i in range(8):
            j = 0
            for char in board[i]:
                if char.isdigit():
                    j += int(char)
                else:
                    self.board[7-i][7-j] = self.char_to_piece(char)(WHITE if char.isupper() else BLACK)
                    j += 1

        self.current_player = WHITE if fen[1] == "w" else BLACK

        castling_rights = fen[2]
        if castling_rights != "-":
            if "K" in castling_rights and \
                self.board[0][3] == KING and self.board[0][3] == WHITE and \
                self.board[0][0] == ROOK and self.board[0][0] == WHITE:
                self.board[0][3].can_castle = True
                self.board[0][0].can_castle = True
            if "Q" in castling_rights and \
                self.board[0][3] == KING and self.board[0][3] == WHITE and \
                self.board[0][7] == ROOK and self.board[0][7] == WHITE:
                self.board[0][3].can_castle = True
                self.board[0][7].can_castle = True
            if "k" in castling_rights and \
                self.board[7][3] == KING and self.board[7][3] == BLACK and \
                self.board[7][0] == ROOK and self.board[7][0] == BLACK:
                self.board[7][3].can_castle = True
                self.board[7][0].can_castle = True
            if "q" in castling_rights and \
                self.board[7][3] == KING and self.board[7][3] == BLACK \
                and self.board[7][7] == ROOK and self.board[7][7] == BLACK:
                self.board[7][3].can_castle = True
                self.board[7][7].can_castle = True

        self.en_passant_square = fen[3]
        self.halfmove_clock = int(fen[4])
        self.move_num = int(fen[5])

    def to_fen(self) -> str:
        fen = ""
        for i in range(8):
            empty = 0
            for j in range(8):
                if self.board[7-i][7-j] == EMPTY:
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    fen += PIECE_FEN[self.board[7-i][7-j].type][self.board[7-i][7-j].color]
            if empty:
                fen += str(empty)
            if i < 7:
                fen += "/"

        fen += " " + ("w" if self.current_player == WHITE else "b") + " "
        castling_rights = ""
        if self.board[0][3] == KING and self.board[0][3] == WHITE and self.board[0][3].can_castle and \
           self.board[0][0] == ROOK and self.board[0][0] == WHITE and self.board[0][0].can_castle:
            castling_rights += "K"
        if self.board[0][3] == KING and self.board[0][3] == WHITE and self.board[0][3].can_castle and \
           self.board[0][7] == ROOK and self.board[0][7] == WHITE and self.board[0][7].can_castle:
            castling_rights += "Q"
        if self.board[7][3] == KING and self.board[7][3] == BLACK and self.board[7][3].can_castle and \
           self.board[7][0] == ROOK and self.board[7][0] == BLACK and self.board[7][0].can_castle:
            castling_rights += "k"
        if self.board[7][3] == KING and self.board[7][3] == BLACK and self.board[7][3].can_castle and \
           self.board[7][7] == ROOK and self.board[7][7] == BLACK and self.board[7][7].can_castle:
            castling_rights += "q"
        fen += castling_rights if castling_rights else "-"
        fen += " " + self.en_passant_square + " " + str(self.halfmove_clock) + " " + str(self.move_num)
        return fen

    def move(self, start_pos: tuple[int, int], end_pos: tuple[int, int] | tuple[int, int, str]) -> None:
        self.history.append((start_pos, end_pos))
        self.move_num += 1
        piece = self.board[start_pos]
        destination = self.board[end_pos[:2]]

        if piece == KING or piece == ROOK:
            self.board[start_pos].can_castle = False
        
        if len(end_pos) == 3:
            self.board[end_pos[:2]] = FEN_MAP[end_pos[2]](self.current_player)
        elif piece == PAWN and self.en_passant_square != "-" and end_pos == board_to_coord(self.en_passant_square):
            self.board[end_pos] = piece
            self.board[start_pos[0]][end_pos[1]] = Empty()
        elif piece == KING and abs(start_pos[1] - end_pos[1]) == 2:
            self.board[end_pos] = piece
            side = end_pos[1] > start_pos[1]
            rook = self.board[7*self.current_player][7*side]
            rook.can_castle = False
            self.board[7*self.current_player][7*side] = Empty()
            self.board[7*self.current_player][(start_pos[1]+end_pos[1])//2] = rook
        else:
            self.board[end_pos] = piece
        self.board[start_pos] = Empty()
        self.current_player = Color(1 - self.current_player)

        if piece == PAWN and abs(start_pos[0] - end_pos[0]) == 2:
            self.en_passant_square = coord_to_board(((start_pos[0] + end_pos[0]) // 2, start_pos[1])).lower()
        else:
            self.en_passant_square = "-"

        if piece == PAWN or destination != EMPTY:
            self.halfmove_clock = 0
            self.fen_counter = Counter()
        else:
            self.halfmove_clock += 1
            self.fen_counter[self.to_fen()] += 1

    def find_piece(self, piece_type: PieceType, color: Color = None) -> tuple[int, int]:
        if not color:
            color = self.current_player
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == piece_type and self.board[i][j] == color:
                    return (i, j)
        return None

    def find_pieces(self, piece_type: PieceType, color: Color = None) -> list[tuple[int, int]]:
        if not color:
            color = self.current_player
        res = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == piece_type and self.board[i][j] == color:
                    res.append((i, j))
        return res
    
    def chessboard(self) -> str:
        res = ""
        res += "  " + "| A | B | C | D | E | F | G | H |"[::(-1)**(self.current_player)] + "\n"
        res += "-" * 37 + "\n"
        for i in range(7 - 7*self.current_player, 8 - 9*(1-self.current_player), (-1)**(1 - self.current_player)):
            res += str(i+1) + " | "
            for j in range(7 - 7*self.current_player, 8 - 9*(1-self.current_player), (-1)**(1-self.current_player)):
                res += str(self.board[i][j]) + " | "
            res += str(i+1) + "\n" + "-" * 37 + "\n"
        res += "  " + "| A | B | C | D | E | F | G | H |"[::(-1)**(self.current_player)] + "\n"
        return res
    
    def info(self) -> str:
        res = ""
        res += "Current player: " + str(self.current_player) + "\n"
        res += "En passant square: " + self.en_passant_square + "\n"
        res += "Halfmove clock: " + str(self.halfmove_clock) + "\n"
        res += "Move number: " + str(self.move_num) + "\n"
        return res