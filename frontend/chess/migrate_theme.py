#!/usr/bin/env python3
"""
Migration script to add theme_preference column to User table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app import app, db, User

def migrate_theme_preference():
    """Add theme_preference column to User table."""
    with app.app_context():
        try:
            # Add the theme_preference column
            db.session.execute(text("ALTER TABLE user ADD COLUMN theme_preference VARCHAR(10) DEFAULT 'light'"))
            print("✅ Successfully added theme_preference column to User table")
            
            # Update existing users to have 'light' theme preference
            db.session.execute(text("UPDATE user SET theme_preference = 'light' WHERE theme_preference IS NULL"))
            db.session.commit()
            print("✅ Updated existing users to have 'light' theme preference")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False
        
        return True

if __name__ == '__main__':
    print("Starting theme preference migration...")
    if migrate_theme_preference():
        print("🎉 Theme preference migration completed successfully!")
    else:
        print("💥 Theme preference migration failed!")
        sys.exit(1) 