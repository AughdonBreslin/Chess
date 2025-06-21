# Chess Game Web Application

A modern web-based chess application built with Flask, featuring user accounts, AI opponents, and friend-to-friend gameplay.

## Features

- **User Authentication**: Register and login system with secure password hashing
- **AI Opponent**: Play against a chess AI with random move selection
- **Friend Games**: Create games to play against friends
- **Real-time Game State**: Live updates of game board and status
- **Move History**: Track all moves made during the game
- **Game Validation**: Full chess rule validation including check, checkmate, stalemate
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, intuitive interface with Bootstrap styling

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Navigate to the chess frontend directory:**
   ```bash
   cd frontend/chess
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   The database will be automatically created when you run the application for the first time.

## Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Register a new account and start playing!**

## Project Structure

```
frontend/chess/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── new_game.html     # New game creation
│   └── game.html         # Chess game interface
├── static/               # Static files
│   ├── css/
│   │   ├── style.css     # General styles
│   │   └── chess.css     # Chess-specific styles
│   └── js/
│       └── main.js       # General JavaScript utilities
└── README.md            # This file
```

## API Endpoints

### Authentication
- `GET /register` - Registration page
- `POST /register` - Create new user account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Game Management
- `GET /dashboard` - User dashboard with active games
- `GET /new_game` - New game creation page
- `POST /new_game` - Create new game
- `GET /game/<game_id>` - Game interface

### Game API
- `GET /api/game/<game_id>/state` - Get current game state
- `POST /api/game/<game_id>/move` - Make a move
- `GET /api/game/<game_id>/ai_move` - Trigger AI move

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp
- `games_played`: Total games played
- `games_won`: Games won
- `games_drawn`: Games drawn

### Game
- `id`: Unique game identifier
- `white_player_id`: White player user ID
- `black_player_id`: Black player user ID (null for AI games)
- `game_type`: 'ai' or 'friend'
- `fen`: Current board position in FEN notation
- `current_player`: 'white' or 'black'
- `game_state`: JSON string of game state
- `created_at`: Game creation timestamp
- `updated_at`: Last update timestamp
- `is_active`: Whether game is still active

### Move
- `id`: Primary key
- `game_id`: Associated game ID
- `player_id`: Player who made the move (null for AI)
- `start_pos`: Starting position (e.g., 'e2')
- `end_pos`: Ending position (e.g., 'e4')
- `promotion`: Promotion piece if applicable
- `fen_after`: Board state after move
- `created_at`: Move timestamp

## Game Features

### Chess Rules Implemented
- All standard chess piece movements
- Castling (kingside and queenside)
- En passant captures
- Pawn promotion
- Check and checkmate detection
- Stalemate detection
- Fifty-move rule
- Threefold repetition

### AI Opponent
The current AI implementation uses random move selection from all valid moves. This provides a basic opponent for practice games.

### Friend Games
Friend games are designed for two human players. Currently, both players need to use the same account or implement a sharing mechanism.

## Security Features

- Password hashing using Werkzeug's security functions
- Session management with Flask-Login
- CSRF protection (built into Flask)
- Input validation and sanitization
- SQL injection protection through SQLAlchemy ORM

## Development

### Adding New Features
1. Create new routes in `app.py`
2. Add corresponding templates in `templates/`
3. Update static files as needed
4. Test thoroughly

### Database Migrations
The application uses SQLAlchemy with automatic table creation. For production, consider using Flask-Migrate for proper database migrations.

### Styling
- Main styles: `static/css/style.css`
- Chess-specific styles: `static/css/chess.css`
- Uses Bootstrap 5 for responsive design

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the correct directory and have activated the virtual environment
2. **Database errors**: Delete `chess.db` and restart the application to recreate the database
3. **Port already in use**: Change the port in `app.py` or kill the existing process

### Debug Mode
The application runs in debug mode by default. For production, set `debug=False` in `app.py`.

## Future Enhancements

- [ ] Real-time multiplayer with WebSockets
- [ ] Advanced AI with minimax algorithm
- [ ] Game analysis and move suggestions
- [ ] Tournament system
- [ ] User ratings and leaderboards
- [ ] Game sharing via links
- [ ] Mobile app version
- [ ] Dark mode theme
- [ ] Sound effects and animations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License. 