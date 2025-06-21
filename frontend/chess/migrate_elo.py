#!/usr/bin/env python3
"""
Migration script to add ELO rating column to existing users.
"""

import sqlite3
import os

def migrate_elo_ratings():
    """Add ELO rating column to existing users and set default values."""
    
    # Path to the database file
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'chess.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the Flask app first to create the database.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the elo_rating column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'elo_rating' not in columns:
            print("Adding elo_rating column to user table...")
            
            # Add the elo_rating column with default value 1200
            cursor.execute("ALTER TABLE user ADD COLUMN elo_rating INTEGER DEFAULT 1200")
            
            # Update existing users to have the default ELO rating
            cursor.execute("UPDATE user SET elo_rating = 1200 WHERE elo_rating IS NULL")
            
            conn.commit()
            print("Successfully added ELO rating column to user table.")
        else:
            print("ELO rating column already exists in user table.")
        
        # Show current users and their ELO ratings
        cursor.execute("SELECT username, elo_rating FROM user")
        users = cursor.fetchall()
        
        print("\nCurrent users and their ELO ratings:")
        print("-" * 40)
        for username, elo_rating in users:
            print(f"{username}: {elo_rating}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_elo_ratings() 