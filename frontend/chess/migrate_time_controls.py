#!/usr/bin/env python3
"""
Database migration script to add time control columns to Game table.
"""

import sqlite3
import os

def migrate_database():
    """Add time control columns to Game table if they don't exist."""
    db_path = 'instance/chess.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the app first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if time control columns exist
    cursor.execute("PRAGMA table_info(game)")
    columns = [column[1] for column in cursor.fetchall()]
    
    new_columns = [
        ('initial_time_minutes', 'INTEGER DEFAULT 10'),
        ('increment_seconds', 'INTEGER DEFAULT 0'),
        ('white_time_remaining', 'INTEGER DEFAULT 600'),
        ('black_time_remaining', 'INTEGER DEFAULT 600'),
        ('last_move_time', 'DATETIME'),
        ('winner', 'VARCHAR(10)')
    ]
    
    added_columns = []
    for column_name, column_type in new_columns:
        if column_name not in columns:
            print(f"Adding {column_name} column to Game table...")
            cursor.execute(f"ALTER TABLE game ADD COLUMN {column_name} {column_type}")
            added_columns.append(column_name)
    
    if added_columns:
        conn.commit()
        print(f"Migration completed successfully! Added columns: {', '.join(added_columns)}")
    else:
        print("All time control columns already exist. No migration needed.")
    
    conn.close()

if __name__ == "__main__":
    migrate_database() 