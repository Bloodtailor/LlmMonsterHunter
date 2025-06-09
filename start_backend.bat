@echo off
title Monster Hunter Game - Backend Server

echo.
echo ================================================================
echo                Monster Hunter Game - Backend Server
echo ================================================================
echo.

REM Activate virtual environment
echo Activating Python virtual environment...
call backend\venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Make sure you ran setup_environment.py first
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
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

REM Change to backend directory and run the server
cd backend
python run.py

REM If we get here, the server stopped
echo.
echo Server stopped.
pause