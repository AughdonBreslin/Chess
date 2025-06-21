from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
from datetime import datetime
import sys
import os

# Add the backend/src directory to the path so we can import our chess modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from board import Board
from evaluator import GameEvaluator
from piece_info import board_to_coord, coord_to_board

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chess.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    games_drawn = db.Column(db.Integer, default=0)
    games_lost = db.Column(db.Integer, default=0)

class Game(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    white_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    black_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    game_type = db.Column(db.String(20), nullable=False)  # 'ai' or 'friend'
    fen = db.Column(db.Text, nullable=False)
    current_player = db.Column(db.String(10), nullable=False)  # 'white' or 'black'
    game_state = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    # Time control fields
    initial_time_minutes = db.Column(db.Integer, default=10)  # Initial time in minutes
    increment_seconds = db.Column(db.Integer, default=0)  # Increment in seconds
    white_time_remaining = db.Column(db.Integer, default=600)  # Time remaining in seconds
    black_time_remaining = db.Column(db.Integer, default=600)  # Time remaining in seconds
    last_move_time = db.Column(db.DateTime, nullable=True)  # When the last move was made
    winner = db.Column(db.String(10), nullable=True)  # Winner of the game

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    start_pos = db.Column(db.String(10), nullable=False)
    end_pos = db.Column(db.String(10), nullable=False)
    promotion = db.Column(db.String(1), nullable=True)
    fen_after = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all games for the current user
    user_games = Game.query.filter(
        (Game.white_player_id == current_user.id) | 
        (Game.black_player_id == current_user.id)
    ).all()
    
    # Process each game to determine if it's truly active
    active_games = []
    for game in user_games:
        # Check if game is marked as active in database
        if game.is_active:
            # Check the actual game state to see if it's really over
            try:
                stored_game_state = json.loads(game.game_state) if game.game_state else {}
                
                # Check for resignation
                is_resigned = stored_game_state.get('resignation', {}).get('resignation', False)
                
                # Check for other game-ending conditions
                is_checkmate = stored_game_state.get('checkmate', {}).get('checkmate', False)
                is_stalemate = stored_game_state.get('stalemate', {}).get('stalemate', False)
                is_fifty_move = stored_game_state.get('fifty_move_rule', {}).get('fifty_move_rule', False)
                is_threefold = stored_game_state.get('threefold_repetition', {}).get('threefold_repetition', False)
                
                # Game is truly active if none of the ending conditions are met
                if not (is_resigned or is_checkmate or is_stalemate or is_fifty_move or is_threefold):
                    active_games.append(game)
                else:
                    # Update the database to reflect that the game is actually over
                    game.is_active = False
                    db.session.commit()
                    
            except (json.JSONDecodeError, KeyError):
                # If there's an error parsing the game state, assume it's active
                active_games.append(game)
    
    # Get user statistics
    user_stats = {
        'games_played': current_user.games_played,
        'games_won': current_user.games_won,
        'games_drawn': current_user.games_drawn,
        'games_lost': current_user.games_lost,
        'win_rate': round((current_user.games_won / max(current_user.games_played, 1)) * 100, 1)
    }
    
    return render_template('dashboard.html', active_games=active_games, user_stats=user_stats)

@app.route('/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if request.method == 'POST':
        data = request.get_json()
        game_type = data.get('game_type')
        color_choice = data.get('color_choice', 'random')
        time_control = data.get('time_control', '10+0')  # Default to 10+0
        
        # Parse time control (format: "minutes+increment")
        try:
            time_parts = time_control.split('+')
            initial_minutes = int(time_parts[0])
            increment_seconds = int(time_parts[1]) if len(time_parts) > 1 else 0
        except (ValueError, IndexError):
            initial_minutes = 10
            increment_seconds = 0
        
        white_player_id = None
        black_player_id = None
        if game_type == 'friend':
            import random
            if color_choice == 'white':
                white_player_id = current_user.id
            elif color_choice == 'black':
                black_player_id = current_user.id
            else:  # random
                if random.choice([True, False]):
                    white_player_id = current_user.id
                else:
                    black_player_id = current_user.id
        else:  # AI game
            white_player_id = current_user.id
        # Create new game with starting position
        game = Game(
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            game_type=game_type,
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            current_player='white',
            game_state=json.dumps({
                'game_over': False,
                'checkmate': {'checkmate': False},
                'stalemate': {'stalemate': False},
                'fifty_move_rule': {'fifty_move_rule': False},
                'threefold_repetition': {'threefold_repetition': False}
            }),
            initial_time_minutes=initial_minutes,
            increment_seconds=increment_seconds,
            white_time_remaining=initial_minutes * 60,
            black_time_remaining=initial_minutes * 60
        )
        db.session.add(game)
        db.session.commit()
        if game_type == 'friend':
            join_link = url_for('join_game', game_id=game.id, _external=True)
            return jsonify({'game_id': game.id, 'join_link': join_link}), 201
        else:
            return jsonify({'game_id': game.id}), 201
    
    return render_template('new_game.html')

@app.route('/join/<game_id>', methods=['GET', 'POST'])
def join_game(game_id):
    game = Game.query.get_or_404(game_id)
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))
    # Only allow joining if the game is a friend game and the second player slot is open
    if game.game_type != 'friend' or (game.white_player_id and game.black_player_id):
        flash('This game is not available to join.')
        return redirect(url_for('dashboard'))
    # Assign the joining user as black if white is taken, or vice versa
    if game.white_player_id is None and current_user.id != game.black_player_id:
        game.white_player_id = current_user.id
    elif game.black_player_id is None and current_user.id != game.white_player_id:
        game.black_player_id = current_user.id
    else:
        flash('You are already part of this game or the game is full.')
        return redirect(url_for('dashboard'))
    db.session.commit()
    return redirect(url_for('game', game_id=game.id))

@app.route('/game/<game_id>')
@login_required
def game(game_id):
    game = Game.query.get_or_404(game_id)
    # Allow access if user is a player or if joining as second player in a friend game
    if (game.white_player_id != current_user.id and game.black_player_id != current_user.id):
        # If friend game and one slot is open, allow joining
        if game.game_type == 'friend' and (game.white_player_id is None or game.black_player_id is None):
            return redirect(url_for('join_game', game_id=game.id))
        flash('You are not authorized to view this game')
        return redirect(url_for('dashboard'))
    return render_template('game.html', game=game)

@app.route('/api/game/<game_id>/state')
@login_required
def get_game_state(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.white_player_id != current_user.id and game.black_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Evaluate current chess position
    board = Board(game.fen)
    evaluator = GameEvaluator(board)
    game_state = evaluator.is_game_over()
    
    # Check for resignation (separate from chess evaluation)
    stored_game_state = json.loads(game.game_state) if game.game_state else {}
    is_resigned = stored_game_state.get('resignation', {}).get('resignation', False)
    
    # Update game state in database only if not resigned
    if not is_resigned:
        game.game_state = json.dumps(game_state)
        db.session.commit()
    
    # Add resignation info to response if applicable
    response_data = {
        'fen': game.fen,
        'current_player': 'white' if board.current_player == 0 else 'black',
        'game_state': clean_game_state(game_state),
        'board': board_to_dict(board),
        'is_resigned': is_resigned,
        'white_player_id': game.white_player_id,
        'black_player_id': game.black_player_id,
        'time_control': {
            'initial_time_minutes': game.initial_time_minutes,
            'increment_seconds': game.increment_seconds,
            'white_time_remaining': game.white_time_remaining,
            'black_time_remaining': game.black_time_remaining,
            'last_move_time': game.last_move_time.isoformat() if game.last_move_time else None
        }
    }
    
    if is_resigned:
        response_data['resignation_info'] = stored_game_state.get('resignation', {})
    
    return jsonify(response_data)

@app.route('/api/game/<game_id>/move', methods=['POST'])
@login_required
def make_move(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.white_player_id != current_user.id and game.black_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    start_pos = data.get('start_pos')
    end_pos = data.get('end_pos')
    promotion = data.get('promotion')
    
    print(f"Move request: {start_pos} -> {end_pos}")
    
    # Convert algebraic notation to coordinates
    start_coord = board_to_coord(start_pos)
    end_coord = board_to_coord(end_pos)
    
    print(f"Converted coordinates: {start_coord} -> {end_coord}")
    
    if promotion:
        end_coord = end_coord + (promotion,)
    
    board = Board(game.fen)
    evaluator = GameEvaluator(board)
    
    print(f"Current player in board: {board.current_player}")
    print(f"Piece at start position {start_coord}: {board[start_coord]}")
    print(f"Piece color: {board[start_coord].color}")
    print(f"Current player color: {board.current_player}")
    
    # Validate move
    validity = evaluator.is_valid(start_coord, end_coord)
    print(f"Move validity: {validity}")
    
    if not validity['valid']:
        return jsonify({'error': validity['reason']}), 400
    
    # Make move
    board.move(start_coord, end_coord)
    
    # Record move
    move = Move(
        game_id=game_id,
        player_id=current_user.id,
        start_pos=start_pos,
        end_pos=end_pos,
        promotion=promotion,
        fen_after=board.to_fen()
    )
    db.session.add(move)
    
    # Update game
    game.fen = board.to_fen()
    game.current_player = 'white' if board.current_player == 0 else 'black'
    game.updated_at = datetime.utcnow()
    
    # Update time control
    current_time = datetime.utcnow()
    if game.last_move_time:
        # Calculate time used for the move
        time_used = (current_time - game.last_move_time).total_seconds()
        
        # Deduct time from the player who just moved
        if board.current_player == 0:  # White just moved, so black's time is running
            game.black_time_remaining = max(0, game.black_time_remaining - time_used)
            # Add increment to white's time
            game.white_time_remaining += game.increment_seconds
        else:  # Black just moved, so white's time is running
            game.white_time_remaining = max(0, game.white_time_remaining - time_used)
            # Add increment to black's time
            game.black_time_remaining += game.increment_seconds
    
    game.last_move_time = current_time
    
    # Check for time flag
    if game.white_time_remaining <= 0:
        game_state = {
            'game_over': True,
            'checkmate': {'checkmate': False},
            'stalemate': {'stalemate': False},
            'fifty_move_rule': {'fifty_move_rule': False},
            'threefold_repetition': {'threefold_repetition': False},
            'time_flag': {'time_flag': True, 'winner': 'black'}
        }
        game.winner = 'black'
        game.is_active = False
    elif game.black_time_remaining <= 0:
        game_state = {
            'game_over': True,
            'checkmate': {'checkmate': False},
            'stalemate': {'stalemate': False},
            'fifty_move_rule': {'fifty_move_rule': False},
            'threefold_repetition': {'threefold_repetition': False},
            'time_flag': {'time_flag': True, 'winner': 'white'}
        }
        game.winner = 'white'
        game.is_active = False
    else:
        # Check game state
        game_state = evaluator.is_game_over()
        if game_state['game_over']:
            game.is_active = False
            if game_state['checkmate']['checkmate']:
                game.winner = 'black' if board.current_player == 0 else 'white'
    
    game.game_state = json.dumps(game_state)
    
    # Update user stats
    if game.winner and game.white_player_id and game.black_player_id:
        white_user = User.query.get(game.white_player_id)
        black_user = User.query.get(game.black_player_id)
        
        if game.winner == 'white':
            white_user.games_won += 1
            black_user.games_lost += 1
        else:
            black_user.games_won += 1
            white_user.games_lost += 1
        
        white_user.games_played += 1
        black_user.games_played += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'fen': game.fen,
        'current_player': game.current_player,
        'game_state': clean_game_state(game_state),
        'board': board_to_dict(board),
        'time_control': {
            'initial_time_minutes': game.initial_time_minutes,
            'increment_seconds': game.increment_seconds,
            'white_time_remaining': game.white_time_remaining,
            'black_time_remaining': game.black_time_remaining,
            'last_move_time': game.last_move_time.isoformat() if game.last_move_time else None
        }
    })

@app.route('/api/game/<game_id>/ai_move')
@login_required
def ai_move(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.game_type != 'ai':
        return jsonify({'error': 'This is not an AI game'}), 400
    
    if game.white_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    board = Board(game.fen)
    evaluator = GameEvaluator(board)
    
    # Simple AI: find a random valid move
    import random
    
    valid_moves = []
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece.color == board.current_player:
                for move in piece.moves((i, j)):
                    if evaluator.is_valid((i, j), move)['valid']:
                        valid_moves.append(((i, j), move))
    
    if not valid_moves:
        return jsonify({'error': 'No valid moves available'}), 400
    
    # Choose random move
    start_coord, end_coord = random.choice(valid_moves)
    
    # Convert to algebraic notation
    start_pos = coord_to_board(start_coord)
    end_pos = coord_to_board(end_coord[:2])
    promotion = end_coord[2] if len(end_coord) > 2 else None
    
    # Make move
    board.move(start_coord, end_coord)
    
    # Record move
    move = Move(
        game_id=game_id,
        player_id=None,  # AI move
        start_pos=start_pos,
        end_pos=end_pos,
        promotion=promotion,
        fen_after=board.to_fen()
    )
    db.session.add(move)
    
    # Update game
    game.fen = board.to_fen()
    game.current_player = 'white' if board.current_player == 0 else 'black'
    game.updated_at = datetime.utcnow()
    
    # Update time control
    current_time = datetime.utcnow()
    if game.last_move_time:
        # Calculate time used for the move
        time_used = (current_time - game.last_move_time).total_seconds()
        
        # Deduct time from the player who just moved
        if board.current_player == 0:  # White just moved, so black's time is running
            game.black_time_remaining = max(0, game.black_time_remaining - time_used)
            # Add increment to white's time
            game.white_time_remaining += game.increment_seconds
        else:  # Black just moved, so white's time is running
            game.white_time_remaining = max(0, game.white_time_remaining - time_used)
            # Add increment to black's time
            game.black_time_remaining += game.increment_seconds
    
    game.last_move_time = current_time
    
    # Check for time flag
    if game.white_time_remaining <= 0:
        game_state = {
            'game_over': True,
            'checkmate': {'checkmate': False},
            'stalemate': {'stalemate': False},
            'fifty_move_rule': {'fifty_move_rule': False},
            'threefold_repetition': {'threefold_repetition': False},
            'time_flag': {'time_flag': True, 'winner': 'black'}
        }
        game.winner = 'black'
        game.is_active = False
    elif game.black_time_remaining <= 0:
        game_state = {
            'game_over': True,
            'checkmate': {'checkmate': False},
            'stalemate': {'stalemate': False},
            'fifty_move_rule': {'fifty_move_rule': False},
            'threefold_repetition': {'threefold_repetition': False},
            'time_flag': {'time_flag': True, 'winner': 'white'}
        }
        game.winner = 'white'
        game.is_active = False
    else:
        # Check game state
        game_state = evaluator.is_game_over()
        if game_state['game_over']:
            game.is_active = False
            if game_state['checkmate']['checkmate']:
                game.winner = 'black' if board.current_player == 0 else 'white'
    
    game.game_state = json.dumps(game_state)
    
    # Update user stats
    if game.winner and game.white_player_id and game.black_player_id:
        white_user = User.query.get(game.white_player_id)
        black_user = User.query.get(game.black_player_id)
        
        if game.winner == 'white':
            white_user.games_won += 1
            black_user.games_lost += 1
        else:
            black_user.games_won += 1
            white_user.games_lost += 1
        
        white_user.games_played += 1
        black_user.games_played += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'fen': game.fen,
        'current_player': game.current_player,
        'game_state': clean_game_state(game_state),
        'board': board_to_dict(board),
        'ai_move': {
            'start_pos': start_pos,
            'end_pos': end_pos,
            'promotion': promotion
        },
        'time_control': {
            'initial_time_minutes': game.initial_time_minutes,
            'increment_seconds': game.increment_seconds,
            'white_time_remaining': game.white_time_remaining,
            'black_time_remaining': game.black_time_remaining,
            'last_move_time': game.last_move_time.isoformat() if game.last_move_time else None
        }
    })

@app.route('/api/game/<game_id>/resign', methods=['POST'])
@login_required
def resign_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.white_player_id != current_user.id and game.black_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not game.is_active:
        return jsonify({'error': 'Game is already over'}), 400
    
    # Determine the winner (the player who didn't resign)
    if game.white_player_id == current_user.id:
        winner = 'black'
        winner_id = game.black_player_id
        loser_id = game.white_player_id
    else:
        winner = 'white'
        winner_id = game.white_player_id
        loser_id = game.black_player_id
    
    # Update game state
    game.is_active = False
    game.winner = winner  # Set the winner field
    game.game_state = json.dumps({
        'game_over': True,
        'checkmate': {'checkmate': False},
        'stalemate': {'stalemate': False},
        'fifty_move_rule': {'fifty_move_rule': False},
        'threefold_repetition': {'threefold_repetition': False},
        'resignation': {'resignation': True, 'winner': winner}
    })
    
    # Update user statistics
    if winner_id and loser_id:
        winner_user = User.query.get(winner_id)
        loser_user = User.query.get(loser_id)
        if winner_user:
            winner_user.games_won += 1
            winner_user.games_played += 1
        if loser_user:
            loser_user.games_lost += 1
            loser_user.games_played += 1
    elif loser_id:  # AI game - only update the human player's stats
        loser_user = User.query.get(loser_id)
        if loser_user:
            loser_user.games_lost += 1
            loser_user.games_played += 1
    
    # Record the resignation move
    move = Move(
        game_id=game_id,
        player_id=current_user.id,
        start_pos='resign',
        end_pos='resign',
        promotion=None,
        fen_after=game.fen
    )
    db.session.add(move)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{winner.capitalize()} wins by resignation',
        'winner': winner
    })

def clean_game_state(game_state):
    """Clean game state to ensure JSON serialization"""
    def clean_value(value):
        if isinstance(value, tuple):
            return list(value)
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        elif isinstance(value, dict):
            return {key: clean_value(val) for key, val in value.items()}
        elif isinstance(value, bool):
            return value  # Preserve boolean values
        elif hasattr(value, '__str__'):
            return str(value)
        else:
            return value
    
    return clean_value(game_state)

def board_to_dict(board):
    """Convert board to dictionary representation for JSON"""
    board_dict = []
    # Flip the board so white pieces appear at the bottom (row 0) and correct file order
    for i in range(7, -1, -1):  # Start from row 7 and go down to row 0
        row = []
        for j in range(7, -1, -1):  # Start from col 7 and go down to col 0 (flip columns too)
            piece = board[i][j]
            if piece.type == 0:  # Empty
                row.append(None)
            else:
                row.append({
                    'type': piece.type.value,  # Convert enum to string value for JSON serialization
                    'color': 'white' if piece.color == 0 else 'black',
                    'symbol': str(piece)
                })
        board_dict.append(row)
    return board_dict

@app.route('/api/games/history')
@login_required
def get_game_history():
    """Get user's game history with optional filtering"""
    filter_type = request.args.get('filter', 'all')
    
    # Base query for games where user participated and are not active
    base_query = Game.query.filter(
        (Game.white_player_id == current_user.id) | (Game.black_player_id == current_user.id),
        Game.is_active == False
    )
    
    # Add filter conditions
    if filter_type == 'won':
        games = base_query.filter(
            ((Game.white_player_id == current_user.id) & (Game.winner == 'white')) |
            ((Game.black_player_id == current_user.id) & (Game.winner == 'black'))
        ).all()
    elif filter_type == 'lost':
        games = base_query.filter(
            ((Game.white_player_id == current_user.id) & (Game.winner == 'black')) |
            ((Game.black_player_id == current_user.id) & (Game.winner == 'white'))
        ).all()
    elif filter_type == 'drawn':
        games = base_query.filter(Game.winner == None).all()
    else:  # 'all'
        games = base_query.all()
    
    # Convert to list of dictionaries
    game_list = []
    for game in games:
        # Determine user's color
        user_color = 'white' if game.white_player_id == current_user.id else 'black'
        
        # Determine opponent
        if game.game_type == 'ai':
            opponent = 'AI'
        else:
            if game.white_player_id == current_user.id:
                opponent_user = User.query.get(game.black_player_id)
                opponent = opponent_user.username if opponent_user else 'Unknown'
            else:
                opponent_user = User.query.get(game.white_player_id)
                opponent = opponent_user.username if opponent_user else 'Unknown'
        
        # Determine result
        if game.winner == 'white' and game.white_player_id == current_user.id:
            result = 'Won'
        elif game.winner == 'black' and game.black_player_id == current_user.id:
            result = 'Won'
        elif game.winner == 'white' and game.black_player_id == current_user.id:
            result = 'Lost'
        elif game.winner == 'black' and game.white_player_id == current_user.id:
            result = 'Lost'
        elif game.winner is None:
            result = 'Drawn'
        else:
            result = 'Unknown'
        
        # Debug logging
        print(f"Game {game.id}: winner={game.winner}, white_player={game.white_player_id}, black_player={game.black_player_id}, current_user={current_user.id}, result={result}")
        
        game_dict = {
            'id': game.id,
            'white_player_id': game.white_player_id,
            'black_player_id': game.black_player_id,
            'game_type': game.game_type,
            'fen': game.fen,
            'current_player': game.current_player,
            'game_state': game.game_state,
            'created_at': game.created_at.isoformat() if game.created_at else None,
            'updated_at': game.updated_at.isoformat() if game.updated_at else None,
            'is_active': game.is_active,
            'initial_time_minutes': game.initial_time_minutes,
            'increment_seconds': game.increment_seconds,
            'white_time_remaining': game.white_time_remaining,
            'black_time_remaining': game.black_time_remaining,
            'last_move_time': game.last_move_time.isoformat() if game.last_move_time else None,
            'winner': game.winner,
            'user_color': user_color,
            'opponent': opponent,
            'result': result
        }
        game_list.append(game_dict)
    
    # Sort by created_at descending
    game_list.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'games': game_list})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 