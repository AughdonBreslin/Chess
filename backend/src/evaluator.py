from board import Board
from piece_info import Color, BLACK, EMPTY, KING, PAWN, ROOK, board_to_coord
from pieces import ChessPiece, Pawn

class GameEvaluator:
    def __init__(self, board: Board):
        self.board = board

    def set_piece_eval(self, piece: ChessPiece, position: tuple[int, int]):
        if piece == PAWN:
            self.piece_eval = PawnEvaluator(piece, position, self.board)
        elif piece == KING:
            self.piece_eval = KingEvaluator(piece, position, self.board)
        else:
            self.piece_eval = PieceEvaluator(piece, position, self.board)

    def in_check(self) -> list[tuple[int, int]]:
        attacker_pos = []
        king_pos = self.board.find_piece(KING, self.board.current_player)
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece == 1 - self.board.current_player:
                    self.set_piece_eval(piece, (i, j))
                    res = self.piece_eval.is_capable(king_pos)
                    if res["capable"]:
                        attacker_pos.append((i, j))
        return attacker_pos


    def is_valid(self, start_pos: tuple[int, int], end_pos: tuple[int, int] | tuple[int, int, str]) -> dict[str, any]:
        res = {"info": f"Move from {start_pos} to {end_pos}", "reason": ""}
        if ChessPiece.out_of_bounds(start_pos):
            res["valid"] = False
            res["reason"] = f"Start position {start_pos} is out of bounds."
            return res
        
        piece: ChessPiece = self.board[start_pos]
        res["piece"] = piece

        if piece == EMPTY:
            res["valid"] = False
            res["reason"] = f"No piece ({piece}) at start position {start_pos}."
            return res
        
        if piece.color != self.board.current_player:
            res["valid"] = False
            res["reason"] = f"Piece ({piece}) at start position {start_pos} is not the current player's."
            return res
        
        if not piece.can_move(start_pos, end_pos):
            res["valid"] = False
            res["reason"] = f"Piece ({piece}) at start position {start_pos} cannot move to end position {end_pos}."
            return res
        
        self.set_piece_eval(piece, start_pos)
        validity = self.piece_eval.is_valid(end_pos)
        if not validity["valid"]:
            res["valid"] = False
            res["reason"] = validity["reason"]
            return res
        
        res["valid"] = True
        return res
    
    def is_game_over(self) -> dict[str, any]:
        checkmate = self.is_checkmate()
        stalemate = self.is_stalemate()
        fifty_move_rule = self.is_fifty_move_rule()
        return {"game_over": checkmate["checkmate"] or stalemate["stalemate"] or fifty_move_rule["fifty_move_rule"], 
                "checkmate": checkmate, "stalemate": stalemate, "fifty_move_rule": fifty_move_rule}
    
    def outcome(self, game_state: dict[str, int]) -> dict[str, int]:
        if game_state["checkmate"]["checkmate"]:
            return {"point": 1 if self.board.current_player == BLACK else 0,
                    "reason": game_state["checkmate"]["reason"]}
        if game_state["stalemate"]["stalemate"]:
            return {"point": 0.5, "reason": game_state["stalemate"]["reason"]}
        if game_state["fifty_move_rule"]["fifty_move_rule"]:
            return {"point": 0.5, "reason": game_state["fifty_move_rule"]["reason"]}
        if game_state["insufficient_material"]["insufficient_material"]:
            return {"point": 0.5, "reason": game_state["insufficient_material"]["reason"]}
        if game_state["threefold_repition"]["threefold_repition"]:
            return {"point": 0.5, "reason": game_state["threefold_repition"]["reason"]}
        return {"point": -1, "reason": "Game not over."}
    
    def is_checkmate(self):
        king_pos = self.board.find_piece(KING)
        res = {"checkmate": False, "reason": ""}
        if not king_pos:
            res["reason"] = "No king found."
            return res
        king = self.board[king_pos]

        attacker_pos = self.in_check()
        if not attacker_pos:
            res["reason"] = "No attacker found."
            return res
        
        capturing_moves = []
        blocking_moves = []
        if len(attacker_pos) == 1:
            attack_pos = attacker_pos[0]
            attacker = self.board[attack_pos]
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    piece = self.board[i][j]
                    if piece.color != self.board.current_player:
                        continue
                    self.set_piece_eval(piece, (i, j))
                    validity = self.piece_eval.is_valid(attack_pos)
                    if validity["valid"]:
                        capturing_moves.append(((i, j), attack_pos))
                    if piece == PAWN and self.board.en_passant_square != "-":
                        validity = self.piece_eval.is_valid(board_to_coord(self.board.en_passant_square))
                        if validity["valid"]:
                            capturing_moves.append(((i, j), board_to_coord(self.board.en_passant_square)))
            for square in attacker.line_of_sight(attack_pos, king_pos):
                for i in range(len(self.board)):
                    for j in range(len(self.board[i])):
                        piece = self.board[i][j]
                        if piece.color != self.board.current_player:
                            continue
                        self.set_piece_eval(piece, (i, j))
                        if self.piece_eval.is_valid(square)["valid"]:
                            blocking_moves.append(((i, j), square))
        self.set_piece_eval(king, king_pos)
        running_moves = [move for move in king.moves(king_pos) if self.piece_eval.is_valid(move)["valid"]]
        
        res["checkmate"] = not (capturing_moves or blocking_moves or running_moves)
        res["capturing_moves"] = capturing_moves
        res["blocking_moves"] = blocking_moves
        res["running_moves"] = running_moves
        res["reason"] = f"{Color(1-self.board.current_player)} wins! King {king} cannot escape attack{'s' if len(attacker_pos)>1 else ''} from {[self.board[attack_pos] for attack_pos in attacker_pos] if len(attacker_pos)>1 else attacker} at position{'s' if len(attacker_pos)>1 else ''} {attacker_pos if len(attacker_pos)>1 else attacker_pos[0]}."
        return res
    
    def is_stalemate(self):
        res = {"stalemate": False}
        attacker_pos = self.in_check()
        if attacker_pos:
            res["reason"] = f"Attacker found at {attacker_pos}."
            return res

        all_valid_moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                piece = self.board[i][j]
                if piece.color != self.board.current_player:
                    continue
                self.set_piece_eval(piece, (i, j))
                all_valid_moves.extend([((i, j), move) for move in piece.moves((i, j))  \
                                        if self.piece_eval.is_valid(move)["valid"]])
        res["stalemate"] = not all_valid_moves
        res["moves"] = all_valid_moves
        return res
    
    def is_fifty_move_rule(self):
        res = {"fifty_move_rule": False, "halfmove_clock": self.board.halfmove_clock}
        if self.board.halfmove_clock >= 50:
            res["fifty_move_rule"] = True
        return res
    
    def is_threefold_repition(self):
        res = {"threefold_repition": False, "fen": ""}
        if self.board.fen_counter.most_common(1)[0][1] >= 3:
            res["threefold_repition"] = True
            res["fen"] = self.board.fen_counter.most_common(1)[0][0]
        return res


class PieceEvaluator:
    def __init__(self, piece: ChessPiece, position: tuple[int, int], board: Board):
        self.piece = piece
        self.position = position
        self.board = board

    def set_game_eval(self):
        self.game_eval = GameEvaluator(self.board)

    def is_capable(self, end_pos: tuple[int, int]) -> dict[str, any]:
        res = {"info": f"{self.piece}({self.position} -> {end_pos})", "reason": ""}
        if not self.piece.can_move(self.position, end_pos):
            res["capable"] = False
            res["reason"] = f"Piece ({self.piece}) at position {self.position} cannot move to end position {end_pos}."
            return res

        if self.board[end_pos] != EMPTY and self.board[end_pos].color == self.piece.color:
            res["capable"] = False
            res["reason"] = f"End position {end_pos} is occupied by piece ({self.board[end_pos]}) of the same color."
            return res
        
        moves = self.piece.line_of_sight(self.position, end_pos)
        for move in moves:
            if self.board[move] != EMPTY:
                res["capable"] = False
                res["reason"] = f"Path to end position {end_pos} is obstructed by piece ({self.board[move]} at position {move})."
                return res
            
        res["capable"] = True
        return res
    
    def try_move(self, end_pos: tuple[int, int]) -> ChessPiece:
        original_piece = self.board[end_pos]
        self.board.board[end_pos] = self.piece
        self.board.board[self.position] = EMPTY
        if self.piece == PAWN and self.board.en_passant_square != "-" and end_pos == board_to_coord(self.board.en_passant_square):
            self.board.board[(self.position[0], end_pos[1])] = EMPTY
        return original_piece
    
    def undo_move(self, original_piece: ChessPiece, end_pos: tuple[int, int]) -> None:
        self.board.board[self.position] = self.piece
        self.board.board[end_pos] = original_piece
        if self.piece == PAWN and self.board.en_passant_square != "-" and end_pos == board_to_coord(self.board.en_passant_square):
            self.board.board[(self.position[0], end_pos[1])] = Pawn(1 - self.piece.color)
    
    def is_valid(self, end_pos: tuple[int, int]) -> dict[str, any]:
        res = {"info": f"{self.piece}({self.position} -> {end_pos})", "reason": ""}
        capability = self.is_capable(end_pos)
        if not capability["capable"]:
            res["valid"] = False
            res["reason"] = capability["reason"]
            return res
        
        self.set_game_eval()
        original_piece = self.try_move(end_pos)
        attacker_pos = self.game_eval.in_check()
        if attacker_pos:
            self.undo_move(original_piece, end_pos)
            res["valid"] = False
            res["reason"] = f"Move from {self.position} to {end_pos} puts the current player in check by {[f'{self.board[pos]}{pos}' for pos in attacker_pos]}."
            return res
        self.undo_move(original_piece, end_pos)
        res["valid"] = True
        return res
    
class KingEvaluator(PieceEvaluator):
    def __init__(self, piece: ChessPiece, position: tuple[int, int], board: Board):
        super().__init__(piece, position, board)

    def is_capable(self, end_pos: tuple[int, int]) -> dict[str, any]:
        res = super().is_capable(end_pos)
        if not res["capable"]:
            return res
        
        if abs(self.position[1] - end_pos[1]) == 2:
            if self.board[end_pos] != EMPTY:
                res["capable"] = False
                res["reason"] = f"King ({self.piece}) at position {self.position} cannot castle to end position {end_pos} because it is occupied."
                return res
            middle_pos = (self.position[0], (self.position[1] + end_pos[1]) // 2)
            if self.board[middle_pos] != EMPTY:
                res["capable"] = False
                res["reason"] = f"King ({self.piece}) at position {self.position} cannot castle to end position {end_pos} because the path is obstructed at {middle_pos}."
                return res
            if self.position[1] - end_pos[1] == 2:
                rook_pos = (self.position[0], 0)
                rook = self.board[rook_pos]
                if rook != ROOK or not rook.can_castle:
                    res["capable"] = False
                    res["reason"] = f"King ({self.piece}) at position {self.position} cannot castle to end position {end_pos} because the rook at {rook_pos} cannot castle."
                    return res
            else:
                rook_pos = (self.position[0], 7)
                rook = self.board[rook_pos]
                if rook != ROOK or not rook.can_castle:
                    res["capable"] = False
                    res["reason"] = f"King ({self.piece}) at position {self.position} cannot castle to end position {end_pos} because the rook at {rook_pos} cannot castle."
                    return res

        return res
    
    def is_valid(self, end_pos: tuple[int, int]) -> dict[str, any]:
        res = {"info": f"{self.piece}({self.position} -> {end_pos})", "reason": ""}
        capability = self.is_capable(end_pos)
        if not capability["capable"]:
            res["valid"] = False
            res["reason"] = capability["reason"]
            return res
        
        validity = super().is_valid(end_pos)
        if not validity["valid"]:
            res["valid"] = False
            res["reason"] = validity["reason"]
            return res
        
        if abs(self.position[1] - end_pos[1]) == 2:
            for move in [(self.position[0], (self.position[1] + end_pos[1]) // 2), end_pos]:
                original_piece = self.try_move(move)
                attacker_pos = self.game_eval.in_check()
                if attacker_pos:
                    self.undo_move(original_piece, move)
                    res["valid"] = False
                    res["reason"] = f"Move from {self.position} to {end_pos} castles through check by {[f'{self.board[pos]}{pos}' for pos in attacker_pos]}."
                    return res
                self.undo_move(original_piece, move)

        res["valid"] = True
        return res

class PawnEvaluator(PieceEvaluator):
    def __init__(self, piece: ChessPiece, position: tuple[int, int], board: Board):
        super().__init__(piece, position, board)

    def is_capable(self, end_pos: tuple[int, int] | tuple[int, int, str]) -> dict[str, any]:
        if len(end_pos) == 3:
            end_pos = end_pos[:2]
        res = super().is_capable(end_pos)
        if not res["capable"]:
            return res
        
        if self.position[1] == end_pos[1]:
            if self.board[end_pos] != EMPTY:
                res["capable"] = False
                res["reason"] = f"Pawn ({self.piece}) at position {self.position} cannot move to end position {end_pos} because it is occupied by a piece ({self.board[end_pos]})."
                return res
            if abs(self.position[0] - end_pos[0]) == 2 and \
               self.board[((self.position[0] + end_pos[0]) // 2, self.position[1])] != EMPTY:
                res["capable"] = False
                res["reason"] = f"Pawn ({self.piece}) at position {self.position} cannot move to end position {end_pos} because the path is obstructed at {((self.position[0] + end_pos[0]) // 2, self.position[1])}."
                return res
        
        if abs(self.position[0] - end_pos[0]) == 1 and abs(self.position[1] - end_pos[1]) == 1:
            if self.board[end_pos] == EMPTY and (self.board.en_passant_square == "-" or end_pos != board_to_coord(self.board.en_passant_square)):
                res["capable"] = False
                res["reason"] = f"Pawn ({self.piece}) at position {self.position} cannot capture at end position {end_pos} because it is empty ({self.board[end_pos]})."
                return res
            if self.board[end_pos].color == self.piece.color:
                res["capable"] = False
                res["reason"] = f"Pawn ({self.piece}) at position {self.position} cannot move to end position {end_pos} because it is occupied by a piece of the same color ({self.board[end_pos]})."
                return res
            
        res["capable"] = True
        return res

    def is_valid(self, end_pos: tuple[int, int] | tuple[int, int, str]) -> dict[str, any]:
        if len(end_pos) == 3:
            end_pos, promotion = end_pos[:2], end_pos[2]
        else:
            promotion = ""
        res = {"info": f"{self.piece}({self.position} -> {end_pos})", "reason": ""}
        capability = self.is_capable(end_pos)
        if not capability["capable"]:
            res["valid"] = False
            res["reason"] = capability["reason"]
            return res
        
        validity = super().is_valid(end_pos)
        if not validity["valid"]:
            res["valid"] = False
            res["reason"] = validity["reason"]
            return res
        
        if abs(self.position[0] - end_pos[0]) == 1 and abs(self.position[1] - end_pos[1]) == 1:
            if self.board[end_pos] == EMPTY and (self.board.en_passant_square == "-" or end_pos != board_to_coord(self.board.en_passant_square)):
                res["valid"] = False
                res["reason"] = f"Pawn ({self.piece}) at position {self.position} cannot capture at end position {end_pos} because it is empty ({self.board[end_pos]})."
                return res
            original_piece = self.try_move(end_pos)
            attacker_pos = self.game_eval.in_check()
            if attacker_pos:
                self.undo_move(original_piece, end_pos)
                res["valid"] = False
                res["reason"] = f"Move from {self.position} to {end_pos} puts the current player in check by {[f'{self.board[pos]}{pos}' for pos in attacker_pos]}."
                return res
            self.undo_move(original_piece, end_pos)
        
        if end_pos[0] == 7*(1-self.piece.color):
            if promotion == "":
                res["valid"] = False
                res["reason"] = f"Move from {self.position} to {end_pos} requires promotion piece. Promotion must be one of 'q', 'r', 'b', 'n'."
                return res
            if promotion not in "qrbn":
                res["valid"] = False
                res["reason"] = f"Invalid promotion {promotion}. Promotion must be one of 'q', 'r', 'b', 'n'."
                return res

        res["valid"] = True
        return res
