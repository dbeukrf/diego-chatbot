@echo off
echo Starting Diego Chatbot Terminal...
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please create a .env file with your API keys:
    echo OPENAI_API_KEY=your_key_here
    echo LANGCHAIN_API_KEY=your_key_here
    echo.
    pause
)

REM Start the application
echo Starting both frontend and backend...
npm run start:all

pause
