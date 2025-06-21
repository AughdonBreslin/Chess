#!/usr/bin/env python3
"""
Migration script to add AI difficulty column to existing games.
"""

import sqlite3
import os

def migrate_ai_difficulty():
    """Add AI difficulty column to existing games."""
    
    # Path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'chess.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the Flask app first to create the database.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the ai_difficulty column already exists
        cursor.execute("PRAGMA table_info(game)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ai_difficulty' not in columns:
            print("Adding ai_difficulty column to game table...")
            
            # Add the ai_difficulty column with default value 4
            cursor.execute("ALTER TABLE game ADD COLUMN ai_difficulty INTEGER DEFAULT 4")
            
            # Update existing AI games to have the default difficulty
            cursor.execute("UPDATE game SET ai_difficulty = 4 WHERE ai_difficulty IS NULL")
            
            conn.commit()
            print("Successfully added AI difficulty column to game table.")
        else:
            print("AI difficulty column already exists in game table.")
        
        # Show current AI games and their difficulties
        cursor.execute("SELECT id, game_type, ai_difficulty FROM game WHERE game_type = 'ai'")
        ai_games = cursor.fetchall()
        
        print("\nCurrent AI games and their difficulties:")
        print("-" * 50)
        for game_id, game_type, difficulty in ai_games:
            print(f"Game {game_id[:8]}...: {difficulty}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_ai_difficulty() 