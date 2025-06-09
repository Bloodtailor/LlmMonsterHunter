@echo off
title Monster Hunter Game - React Frontend

echo.
echo ================================================================
echo              Monster Hunter Game - React Frontend
echo ================================================================
echo.

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ❌ Frontend dependencies not installed
    echo.
    echo Installing React dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        echo Make sure Node.js and npm are installed
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
    echo.
    cd ..
)

echo ✅ Frontend dependencies found
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