# Quick Setup Guide

## 🚀 Getting Started

### Option 1: Using the startup script (Recommended)
```bash
cd frontend/chess
./start.sh
```

### Option 2: Manual startup
```bash
cd frontend/chess
python3 run.py
```

### Option 3: Direct Flask startup
```bash
cd frontend/chess
python3 app.py
```

## 📋 Prerequisites

- Python 3.8 or higher
- Backend chess modules (should be in `../../backend/src/`)

## 🔧 Installation

If you haven't installed the dependencies yet:

```bash
cd frontend/chess
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
```

## 🌐 Access the Application

Once the server is running, open your browser and go to:
```
http://localhost:5000
```

## 🎮 How to Play

1. **Register** a new account or **Login** with existing credentials
2. **Create a new game** - choose between AI opponent or friend game
3. **Play chess** - click on pieces to select and move them
4. **For AI games** - click "AI Move" button when it's the AI's turn

## 🏗️ Project Structure

```
frontend/chess/
├── app.py              # Main Flask application
├── run.py              # Startup script with checks
├── start.sh            # Shell startup script
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/             # CSS, JS, and other static files
└── README.md           # Detailed documentation
```

## 🐛 Troubleshooting

### "Module not found" errors
- Make sure you're in the `frontend/chess` directory
- Ensure the backend modules exist in `../../backend/src/`
- Install dependencies: `pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug`

### "Port already in use" error
- Change the port in `app.py` or kill the existing process
- Default port is 5000

### Database errors
- Delete `chess.db` file and restart the application
- The database will be recreated automatically

## 📱 Features

- ✅ User registration and login
- ✅ Play against AI (random moves)
- ✅ Play against friends (same account)
- ✅ Real-time game updates
- ✅ Move history tracking
- ✅ Full chess rule validation
- ✅ Responsive design for mobile/desktop
- ✅ Game state persistence

## 🔮 Future Enhancements

- Real-time multiplayer with WebSockets
- Advanced AI with minimax algorithm
- Game sharing via links
- Tournament system
- User ratings and leaderboards

---

**Happy playing! ♟️** 