#!/usr/bin/env python3
"""
Chess Game Web Application Startup Script
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'flask_sqlalchemy', 'flask_login', 'werkzeug']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nTo install missing packages, run:")
        print("pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_backend():
    """Check if backend chess modules are accessible"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/src'))
        from board import Board
        from evaluator import GameEvaluator
        from piece_info import board_to_coord, coord_to_board
        print("✅ Backend chess modules are accessible")
        return True
    except ImportError as e:
        print(f"❌ Cannot import backend modules: {e}")
        print("Make sure the backend/src directory exists and contains the chess modules")
        return False

def main():
    """Main startup function"""
    print("🎯 Chess Game Web Application")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check backend
    if not check_backend():
        sys.exit(1)
    
    print("\n🚀 Starting Flask application...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 