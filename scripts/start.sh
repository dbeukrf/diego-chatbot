#!/bin/bash

echo "🚀 Starting Diego Chatbot Terminal..."
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "LANGCHAIN_API_KEY=your_key_here"
    echo
    read -p "Press Enter to continue..."
fi

# Start the application
echo "Starting both frontend and backend..."
npm run start:all
