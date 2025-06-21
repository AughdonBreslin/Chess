#!/bin/bash

# Chess Game Web Application Startup Script

echo "🎯 Chess Game Web Application"
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the frontend/chess directory"
    exit 1
fi

# Check if backend exists
if [ ! -d "../../backend/src" ]; then
    echo "❌ Backend directory not found. Make sure the backend/src directory exists"
    exit 1
fi

echo "✅ Environment check passed"
echo "🚀 Starting Flask application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo "================================"

# Start the application
python3 run.py 