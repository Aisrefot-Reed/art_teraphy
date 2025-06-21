#!/bin/bash

# Art Therapist Bot Startup Script
# This script starts both the ML API and Telegram Bot processes

echo "🎨 Starting Art Therapist Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.template to .env and configure it."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start ML API in background
echo "🤖 Starting ML API on port 8001..."
cd src
python ml_api.py &
ML_API_PID=$!

# Wait a bit for ML API to start
sleep 5

# Start Telegram Bot
echo "📱 Starting Telegram Bot..."
python bot.py &
BOT_PID=$!

echo "✅ Both processes started successfully!"
echo "ML API PID: $ML_API_PID"
echo "Bot PID: $BOT_PID"
echo ""
echo "To stop the bot, run: kill $ML_API_PID $BOT_PID"
echo "Or use Ctrl+C to stop this script"

# Wait for processes
wait

