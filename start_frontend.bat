@echo off
title Monster Hunter Game - React Frontend

echo.
echo ================================================================
echo              Monster Hunter Game - React Frontend
echo ================================================================
echo.

REM Node.js is installed by start_game.bat's bootstrap - check before
REM npm so the error is "run the launcher", not a cryptic npm failure
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed on this computer.
    echo Run start_game.bat first - it can install it for you.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Frontend dependencies not installed
    echo.
    echo Installing React dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
    echo.
    cd ..
)

echo Frontend dependencies found
echo.

REM Start the React development server
echo Starting React development server...
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo Important: Make sure the backend is running first!
echo   Backend should be at: http://localhost:5000
echo   Run start_backend.bat in another window
echo.
echo Press Ctrl+C to stop the frontend server
echo ================================================================
echo.

REM Change to frontend directory and start the server
cd frontend
npm start

REM If we get here, the server stopped
echo.
echo Frontend server stopped.
pause