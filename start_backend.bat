@echo off
title Monster Hunter Game - Backend Server

echo.
echo ================================================================
echo                Monster Hunter Game - Backend Server
echo ================================================================
echo.

REM The venv is created by the setup that start_game.bat runs - judge
REM by the interpreter inside it, not the folder
if not exist "venv\Scripts\python.exe" (
    echo The game's Python environment is not set up yet.
    echo Run start_game.bat first - it sets everything up for you.
    pause
    exit /b 1
)

echo Activating Python virtual environment...
call venv\Scripts\activate.bat

echo Virtual environment activated
echo.

REM Start the Flask backend
echo Starting Flask backend server...
echo Server will be available at: http://localhost:5000
echo.
echo Available endpoints:
echo   GET  /api/health      - Health check
echo   GET  /api/game/status - Game status
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

REM Run the server
python -m backend.run

REM If we get here, the server stopped
echo.
echo Server stopped.
pause