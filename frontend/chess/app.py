from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
from datetime import datetime, timezone
import sys
import os

# Add the backend/src directory to the path so we can import our chess modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))

from board import Board
from evaluator import GameEvaluator
from piece_info import board_to_coord, coord_to_board, EMPTY

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
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    games_drawn = db.Column(db.Integer, default=0)
    games_lost = db.Column(db.Integer, default=0)
    elo_rating = db.Column(db.Integer, default=1200)  # Starting ELO rating
    theme_preference = db.Column(db.String(10), default='light')  # 'light' or 'dark'

class Game(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    white_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    black_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    game_type = db.Column(db.String(20), nullable=False)  # 'ai' or 'friend'
    fen = db.Column(db.Text, nullable=False)
    current_player = db.Column(db.String(10), nullable=False)  # 'white' or 'black'
    game_state = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    # Time control fields
    initial_time_minutes = db.Column(db.Integer, default=10)  # Initial time in minutes
    increment_seconds = db.Column(db.Integer, default=0)  # Increment in seconds
    white_time_remaining = db.Column(db.Integer, default=600)  # Time remaining in seconds
    black_time_remaining = db.Column(db.Integer, default=600)  # Time remaining in seconds
    last_move_time = db.Column(db.DateTime, nullable=True)  # When the last move was made
    winner = db.Column(db.String(10), nullable=True)  # Winner of the game
    ai_difficulty = db.Column(db.Integer, default=4)  # AI search depth (1-6)

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    start_pos = db.Column(db.String(10), nullable=False)
    end_pos = db.Column(db.String(10), nullable=False)
    promotion = db.Column(db.String(1), nullable=True)
    fen_after = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
    # Get active games for the current user
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
    
    return render_template('dashboard.html', active_games=active_games, datetime=datetime.now(timezone.utc))

@app.route('/profile')
@login_required
def profile():
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
        'win_rate': round((current_user.games_won / max(current_user.games_played, 1)) * 100, 1),
        'elo_rating': current_user.elo_rating
    }
    
    return render_template('profile.html', active_games=active_games, user_stats=user_stats, datetime=datetime.now(timezone.utc))

@app.route('/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if request.method == 'POST':
        data = request.get_json()
        game_type = data.get('game_type')
        color_choice = data.get('color_choice', 'random')
        time_control = data.get('time_control', '10+0')  # Default to 10+0
        ai_difficulty = data.get('ai_difficulty', 4)  # Default to depth 4
        
        # Parse time control (format: "minutes+increment")
        try:
            time_parts = time_control.split('+')
            initial_minutes = int(time_parts[0])
            increment_seconds = int(time_parts[1]) if len(time_parts) > 1 else 0
        except (ValueError, IndexError):
            initial_minutes = 10
            increment_seconds = 0
        
        # Validate AI difficulty
        ai_difficulty = max(1, min(6, int(ai_difficulty)))  # Clamp between 1 and 6
        
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
            black_time_remaining=initial_minutes * 60,
            ai_difficulty=ai_difficulty
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
    
    # Calculate current time remaining if game is active and has a last move time
    if game.is_active and game.last_move_time:
        current_time = datetime.now(timezone.utc)
        # Make the database datetime timezone-aware if it isn't already
        last_move_time = game.last_move_time
        if last_move_time.tzinfo is None:
            last_move_time = last_move_time.replace(tzinfo=timezone.utc)
        time_elapsed = (current_time - last_move_time).total_seconds()
        
        # Calculate current time remaining for both players
        white_time_remaining = game.white_time_remaining
        black_time_remaining = game.black_time_remaining
        
        # Deduct time from the player whose turn it currently is
        if board.current_player == 0:  # White's turn
            white_time_remaining = max(0, white_time_remaining - time_elapsed)
        else:  # Black's turn
            black_time_remaining = max(0, black_time_remaining - time_elapsed)
        
        # Update the time control data with calculated values
        response_data['time_control']['white_time_remaining'] = white_time_remaining
        response_data['time_control']['black_time_remaining'] = black_time_remaining
    
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
    print(f"Promotion parameter: {promotion} (type: {type(promotion)})")
    
    # Convert algebraic notation to coordinates
    start_coord = board_to_coord(start_pos)
    end_coord = board_to_coord(end_pos)
    
    print(f"Converted coordinates: {start_coord} -> {end_coord}")
    
    if promotion:
        end_coord = end_coord + (promotion,)
        print(f"Added promotion to end_coord: {end_coord}")
    
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
    game.updated_at = datetime.now(timezone.utc)
    
    # Update time control
    current_time = datetime.now(timezone.utc)
    if game.last_move_time:
        # Calculate time used for the move
        # Make the database datetime timezone-aware if it isn't already
        last_move_time = game.last_move_time
        if last_move_time.tzinfo is None:
            last_move_time = last_move_time.replace(tzinfo=timezone.utc)
        time_used = (current_time - last_move_time).total_seconds()
        
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
        white_user = db.session.get(User, game.white_player_id)
        black_user = db.session.get(User, game.black_player_id)
        
        if game.winner == 'white':
            white_user.games_won += 1
            black_user.games_lost += 1
        else:
            black_user.games_won += 1
            white_user.games_lost += 1
        
        white_user.games_played += 1
        black_user.games_played += 1
        
        # Update ELO ratings for friend games
        if game.game_type == 'friend':
            if game.winner == 'white':
                update_player_ratings(game.white_player_id, game.black_player_id, is_draw=False)
            else:
                update_player_ratings(game.black_player_id, game.white_player_id, is_draw=False)
    
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
    
    # Check if the current user is authorized to play this game
    if game.white_player_id != current_user.id and game.black_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if it's the AI's turn to move
    # For AI games, the AI plays the opposite color of the human player
    human_color = 'white' if game.white_player_id == current_user.id else 'black'
    ai_color = 'black' if human_color == 'white' else 'white'
    
    if game.current_player != ai_color:
        return jsonify({'error': 'Not AI turn'}), 400
    
    board = Board(game.fen)
    evaluator = GameEvaluator(board)
    
    # Get all valid moves for the AI
    valid_moves = []
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != EMPTY and piece.color == board.current_player:
                for move in piece.moves((i, j)):
                    if evaluator.is_valid((i, j), move)['valid']:
                        valid_moves.append(((i, j), move))
    
    if not valid_moves:
        return jsonify({'error': 'No valid moves available'}), 400
    
    # Choose a random move
    import random
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
    game.updated_at = datetime.now(timezone.utc)
    
    # Update time control
    current_time = datetime.now(timezone.utc)
    if game.last_move_time:
        # Calculate time used for the move
        # Make the database datetime timezone-aware if it isn't already
        last_move_time = game.last_move_time
        if last_move_time.tzinfo is None:
            last_move_time = last_move_time.replace(tzinfo=timezone.utc)
        time_used = (current_time - last_move_time).total_seconds()
        
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
    
    # Update user stats for AI games
    if game.winner and game.game_type == 'ai':
        human_player_id = game.white_player_id if game.white_player_id else game.black_player_id
        human_user = db.session.get(User, human_player_id)
        
        if human_user:
            human_user.games_played += 1
            if game.winner == human_color:
                human_user.games_won += 1
            else:
                human_user.games_lost += 1
    
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
        winner_user = db.session.get(User, winner_id)
        loser_user = db.session.get(User, loser_id)
        if winner_user:
            winner_user.games_won += 1
            winner_user.games_played += 1
        if loser_user:
            loser_user.games_lost += 1
            loser_user.games_played += 1
        
        # Update ELO ratings for friend games
        if game.game_type == 'friend':
            update_player_ratings(winner_id, loser_id, is_draw=False)
    elif loser_id:  # AI game - only update the human player's stats
        loser_user = db.session.get(User, loser_id)
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

@app.route('/api/game/<game_id>/check_time_flag')
@login_required
def check_time_flag(game_id):
    """Check if a player has run out of time and end the game if so."""
    game = Game.query.get_or_404(game_id)
    
    # Check if user is part of this game
    if game.white_player_id != current_user.id and game.black_player_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Only check time flags for active games
    if not game.is_active:
        return jsonify({'game_over': True, 'game_state': json.loads(game.game_state)})
    
    # Calculate current time remaining for both players
    current_time = datetime.now(timezone.utc)
    white_time_remaining = game.white_time_remaining
    black_time_remaining = game.black_time_remaining
    
    if game.last_move_time:
        # Make the database datetime timezone-aware if it isn't already
        last_move_time = game.last_move_time
        if last_move_time.tzinfo is None:
            last_move_time = last_move_time.replace(tzinfo=timezone.utc)
        time_elapsed = (current_time - last_move_time).total_seconds()
        
        # Deduct time from the player whose turn it currently is
        if game.current_player == 'white':
            white_time_remaining = max(0, white_time_remaining - time_elapsed)
        else:
            black_time_remaining = max(0, black_time_remaining - time_elapsed)
    
    # Check for time flag
    if white_time_remaining <= 0:
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
        game.game_state = json.dumps(game_state)
        
        # Update user stats
        if game.white_player_id and game.black_player_id:
            white_user = db.session.get(User, game.white_player_id)
            black_user = db.session.get(User, game.black_player_id)
            
            black_user.games_won += 1
            white_user.games_lost += 1
            white_user.games_played += 1
            black_user.games_played += 1
            
            # Update ELO ratings for friend games
            if game.game_type == 'friend':
                update_player_ratings(game.black_player_id, game.white_player_id, is_draw=False)
        
        db.session.commit()
        
        return jsonify({
            'game_over': True,
            'game_state': clean_game_state(game_state),
            'winner': 'black'
        })
        
    elif black_time_remaining <= 0:
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
        game.game_state = json.dumps(game_state)
        
        # Update user stats
        if game.white_player_id and game.black_player_id:
            white_user = db.session.get(User, game.white_player_id)
            black_user = db.session.get(User, game.black_player_id)
            
            white_user.games_won += 1
            black_user.games_lost += 1
            white_user.games_played += 1
            black_user.games_played += 1
            
            # Update ELO ratings for friend games
            if game.game_type == 'friend':
                update_player_ratings(game.white_player_id, game.black_player_id, is_draw=False)
        
        db.session.commit()
        
        return jsonify({
            'game_over': True,
            'game_state': clean_game_state(game_state),
            'winner': 'white'
        })
    
    # No time flag, return current time remaining
    return jsonify({
        'game_over': False,
        'white_time_remaining': white_time_remaining,
        'black_time_remaining': black_time_remaining
    })

@app.route('/api/user/theme', methods=['POST'])
@login_required
def update_theme():
    """Update user's theme preference."""
    data = request.get_json()
    theme = data.get('theme')
    
    if theme not in ['light', 'dark']:
        return jsonify({'error': 'Invalid theme. Must be "light" or "dark"'}), 400
    
    try:
        current_user.theme_preference = theme
        db.session.commit()
        return jsonify({'success': True, 'theme': theme})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update theme preference'}), 500

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
                opponent_user = db.session.get(User, game.black_player_id)
                opponent = opponent_user.username if opponent_user else 'Unknown'
            else:
                opponent_user = db.session.get(User, game.white_player_id)
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

# ELO Rating Functions
def calculate_elo_change(player_rating, opponent_rating, result, k_factor=32):
    """
    Calculate ELO rating change for a player.
    
    Args:
        player_rating: Current rating of the player
        opponent_rating: Current rating of the opponent
        result: 1 for win, 0.5 for draw, 0 for loss
        k_factor: K-factor for rating volatility (default 32)
    
    Returns:
        Rating change (can be positive or negative)
    """
    expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    rating_change = k_factor * (result - expected_score)
    return round(rating_change)

def update_player_ratings(winner_id, loser_id, is_draw=False):
    """
    Update ELO ratings for both players after a game.
    
    Args:
        winner_id: ID of the winning player (None if draw)
        loser_id: ID of the losing player (None if draw)
        is_draw: True if the game was a draw
    """
    if is_draw:
        # For draws, both players get 0.5 points
        if winner_id and loser_id:
            winner = db.session.get(User, winner_id)
            loser = db.session.get(User, loser_id)
            if winner and loser:
                winner_change = calculate_elo_change(winner.elo_rating, loser.elo_rating, 0.5)
                loser_change = calculate_elo_change(loser.elo_rating, winner.elo_rating, 0.5)
                
                winner.elo_rating += winner_change
                loser.elo_rating += loser_change
                
                db.session.commit()
    else:
        # For wins/losses
        if winner_id and loser_id:
            winner = db.session.get(User, winner_id)
            loser = db.session.get(User, loser_id)
            if winner and loser:
                winner_change = calculate_elo_change(winner.elo_rating, loser.elo_rating, 1)
                loser_change = calculate_elo_change(loser.elo_rating, winner.elo_rating, 0)
                
                winner.elo_rating += winner_change
                loser.elo_rating += loser_change
                
                db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 