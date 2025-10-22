#!/usr/bin/env python3
"""
Startup script for the Diego Chatbot backend API server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting Diego Chatbot Backend API Server...")
    print("📍 Working directory:", os.getcwd())
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found. Please create one with your API keys.")
        print("   Required variables: OPENAI_API_KEY, LANGCHAIN_API_KEY")
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
