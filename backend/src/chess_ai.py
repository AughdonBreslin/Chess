"""
Chess AI implementation with minimax algorithm, alpha-beta pruning, and position evaluation.
"""

import random
import math
from typing import List, Tuple, Optional, Dict, Any
from board import Board
from evaluator import GameEvaluator
from piece_info import Color, BLACK, WHITE, EMPTY, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
from pieces import ChessPiece
from piece_info import coord_to_board, board_to_coord

# Piece values for material counting
PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 900,
    KING: 20000
}

# Position tables for positional evaluation
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_MIDDLE_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

KING_END_TABLE = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

class ChessAI:
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.transposition_table = {}
        self.nodes_evaluated = 0
        self.opening_book = self._load_opening_book()
    
    def _load_opening_book(self) -> Dict[str, List[Tuple[str, str]]]:
        """Load a simple opening book with common moves."""
        return {
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
                ("e2", "e4"),  # 1. e4
                ("d2", "d4"),  # 1. d4
                ("g1", "f3"),  # 1. Nf3
                ("c2", "c4"),  # 1. c4
            ],
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": [
                ("e7", "e5"),  # 1...e5
                ("c7", "c5"),  # 1...c5
                ("e7", "e6"),  # 1...e6
                ("d7", "d6"),  # 1...d6
            ],
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": [
                ("d7", "d5"),  # 1...d5
                ("g8", "f6"),  # 1...Nf6
                ("e7", "e6"),  # 1...e6
                ("c7", "c6"),  # 1...c6
            ]
        }
    
    def get_best_move(self, board: Board, evaluator: GameEvaluator) -> Tuple[Tuple[int, int], Tuple[int, int, Optional[str]]]:
        """Get the best move for the current position."""
        self.nodes_evaluated = 0
        
        # Check opening book first
        fen = board.to_fen()
        if fen in self.opening_book:
            book_moves = self.opening_book[fen]
            if book_moves:
                # Choose a random book move
                start_pos, end_pos = random.choice(book_moves)
                start_coord = board_to_coord(start_pos)
                end_coord = board_to_coord(end_pos)
                return start_coord, end_coord
        
        # Get all valid moves
        valid_moves = self._get_valid_moves(board, evaluator)
        if not valid_moves:
            return None, None
        
        # Order moves for better alpha-beta pruning
        ordered_moves = self._order_moves(board, valid_moves, evaluator)
        
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Find the best move using minimax with alpha-beta pruning
        for start_coord, end_coord in ordered_moves:
            # Make move
            original_piece = board[end_coord[:2]]
            board.move(start_coord, end_coord)
            
            # Evaluate position
            value = self._minimax(board, self.depth - 1, False, alpha, beta, evaluator)
            
            # Undo move
            board.undo_move(start_coord, end_coord, original_piece)
            
            if value > best_value:
                best_value = value
                best_move = (start_coord, end_coord)
            
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # Beta cutoff
        
        return best_move
    
    def _get_valid_moves(self, board: Board, evaluator: GameEvaluator) -> List[Tuple[Tuple[int, int], Tuple[int, int, Optional[str]]]]:
        """Get all valid moves for the current player."""
        valid_moves = []
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != EMPTY and piece.color == board.current_player:
                    for move in piece.moves((i, j)):
                        if evaluator.is_valid((i, j), move)['valid']:
                            valid_moves.append(((i, j), move))
        return valid_moves
    
    def _order_moves(self, board: Board, moves: List[Tuple], evaluator: GameEvaluator) -> List[Tuple]:
        """Order moves to improve alpha-beta pruning efficiency."""
        move_scores = []
        
        for start_coord, end_coord in moves:
            score = 0
            
            # Captures get higher priority
            if board[end_coord[:2]] != EMPTY:
                score += 10 * PIECE_VALUES[board[end_coord[:2]].type] - PIECE_VALUES[board[start_coord].type]
            
            # Pawn moves to center
            if board[start_coord].type == PAWN:
                if end_coord[1] in [3, 4]:  # Center files
                    score += 20
            
            # Knight and bishop development
            if board[start_coord].type in [KNIGHT, BISHOP]:
                if start_coord[0] in [0, 7]:  # Starting rank
                    score += 15
            
            # King safety (avoid moving king in middle game)
            if board[start_coord].type == KING:
                score -= 50
            
            move_scores.append((score, (start_coord, end_coord)))
        
        # Sort by score (highest first)
        move_scores.sort(reverse=True)
        return [move for score, move in move_scores]
    
    def _minimax(self, board: Board, depth: int, maximizing: bool, alpha: float, beta: float, evaluator: GameEvaluator) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        self.nodes_evaluated += 1
        
        # Check for terminal states
        game_state = evaluator.is_game_over()
        if game_state['game_over']:
            if game_state['checkmate']['checkmate']:
                return float('-inf') if maximizing else float('inf')
            elif game_state['stalemate']['stalemate'] or game_state['fifty_move_rule']['fifty_move_rule']:
                return 0
        
        # Check transposition table
        fen = board.to_fen()
        if fen in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[fen]
            if stored_depth >= depth:
                return stored_value
        
        # Leaf node evaluation
        if depth == 0:
            value = self._evaluate_position(board)
            self.transposition_table[fen] = (depth, value)
            return value
        
        valid_moves = self._get_valid_moves(board, evaluator)
        if not valid_moves:
            return 0
        
        if maximizing:
            max_eval = float('-inf')
            for start_coord, end_coord in valid_moves:
                original_piece = board[end_coord[:2]]
                board.move(start_coord, end_coord)
                eval_score = self._minimax(board, depth - 1, False, alpha, beta, evaluator)
                board.undo_move(start_coord, end_coord, original_piece)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            self.transposition_table[fen] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for start_coord, end_coord in valid_moves:
                original_piece = board[end_coord[:2]]
                board.move(start_coord, end_coord)
                eval_score = self._minimax(board, depth - 1, True, alpha, beta, evaluator)
                board.undo_move(start_coord, end_coord, original_piece)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            self.transposition_table[fen] = (depth, min_eval)
            return min_eval
    
    def _evaluate_position(self, board: Board) -> float:
        """Evaluate the current position."""
        score = 0
        
        # Material and positional evaluation
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != EMPTY:
                    piece_value = PIECE_VALUES[piece.type]
                    positional_bonus = self._get_positional_value(piece, i, j, board)
                    
                    if piece.color == WHITE:
                        score += piece_value + positional_bonus
                    else:
                        score -= piece_value + positional_bonus
        
        # Additional evaluation factors
        score += self._evaluate_mobility(board)
        score += self._evaluate_king_safety(board)
        score += self._evaluate_pawn_structure(board)
        
        return score
    
    def _get_positional_value(self, piece: ChessPiece, row: int, col: int, board: Board) -> int:
        """Get positional value for a piece."""
        if piece.type == PAWN:
            table = PAWN_TABLE
        elif piece.type == KNIGHT:
            table = KNIGHT_TABLE
        elif piece.type == BISHOP:
            table = BISHOP_TABLE
        elif piece.type == ROOK:
            table = ROOK_TABLE
        elif piece.type == QUEEN:
            table = QUEEN_TABLE
        elif piece.type == KING:
            # Use endgame table if few pieces remain
            if self._is_endgame(board):
                table = KING_END_TABLE
            else:
                table = KING_MIDDLE_TABLE
        else:
            return 0
        
        # Flip table for black pieces
        if piece.color == BLACK:
            row = 7 - row
            col = 7 - col
        
        return table[row][col]
    
    def _is_endgame(self, board: Board) -> bool:
        """Check if the position is an endgame."""
        piece_count = 0
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != EMPTY and piece.type != PAWN and piece.type != KING:
                    piece_count += 1
        return piece_count <= 4
    
    def _evaluate_mobility(self, board: Board) -> float:
        """Evaluate piece mobility."""
        white_mobility = 0
        black_mobility = 0
        
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != EMPTY:
                    moves = len(piece.moves((i, j)))
                    if piece.color == WHITE:
                        white_mobility += moves
                    else:
                        black_mobility += moves
        
        return (white_mobility - black_mobility) * 2
    
    def _evaluate_king_safety(self, board: Board) -> float:
        """Evaluate king safety."""
        score = 0
        
        # Find kings
        white_king_pos = board.find_piece(KING, WHITE)
        black_king_pos = board.find_piece(KING, BLACK)
        
        if white_king_pos:
            # Penalize king in center during middle game
            if not self._is_endgame(board):
                center_distance = abs(white_king_pos[0] - 3.5) + abs(white_king_pos[1] - 3.5)
                score -= center_distance * 10
        
        if black_king_pos:
            if not self._is_endgame(board):
                center_distance = abs(black_king_pos[0] - 3.5) + abs(black_king_pos[1] - 3.5)
                score += center_distance * 10
        
        return score
    
    def _evaluate_pawn_structure(self, board: Board) -> float:
        """Evaluate pawn structure."""
        score = 0
        
        # Doubled pawns penalty
        for col in range(8):
            white_pawns = 0
            black_pawns = 0
            for row in range(8):
                piece = board[row][col]
                if piece == PAWN:
                    if piece.color == WHITE:
                        white_pawns += 1
                    else:
                        black_pawns += 1
            
            if white_pawns > 1:
                score -= (white_pawns - 1) * 20
            if black_pawns > 1:
                score += (black_pawns - 1) * 20
        
        return score
    
    def clear_transposition_table(self):
        """Clear the transposition table to free memory."""
        self.transposition_table.clear() 