#!/usr/bin/env python3
"""
Startup script for the Diego Chatbot backend API server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("Starting Diego Chatbot Backend API Server...")
    print("Working directory:", os.getcwd())
    
    # Check if .env file exists
    env_path = project_root / '.env'
    if not env_path.exists():
        print("Warning: .env file not found. Please create one with your API keys.")
        print("Required variables: OPENAI_API_KEY, LANGCHAIN_API_KEY")
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.api_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\nBackend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting backend server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
