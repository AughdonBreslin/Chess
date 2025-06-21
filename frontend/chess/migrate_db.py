#!/usr/bin/env python3
"""
Database migration script to add games_lost column to User table.
"""

import sqlite3
import os

def migrate_database():
    """Add games_lost column to User table if it doesn't exist."""
    db_path = 'instance/chess.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the app first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if games_lost column exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'games_lost' not in columns:
        print("Adding games_lost column to User table...")
        cursor.execute("ALTER TABLE user ADD COLUMN games_lost INTEGER DEFAULT 0")
        conn.commit()
        print("Migration completed successfully!")
    else:
        print("games_lost column already exists. No migration needed.")
    
    conn.close()

if __name__ == "__main__":
    migrate_database() 