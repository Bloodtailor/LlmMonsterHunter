@echo off
title Monster Hunter Game Launcher

echo.
echo ================================================================
echo                   Monster Hunter Game Launcher
echo ================================================================
echo.
echo Checking requirements...
echo.

REM Step 1: Auto-setup basic backend (silent unless installing)
python -m setup.setup_environment auto
if errorlevel 1 (
    echo ERROR: Basic backend setup failed
    pause
    exit /b 1
)

REM Step 2: Check all requirements (summary mode)
python -m setup.check_requirements
set requirements_result=%errorlevel%

REM Step 3: Handle requirements result
echo.
if %requirements_result%==0 (
    echo All requirements met! Starting game...
    goto start_game
)

echo Some requirements are missing.
echo.

:ask_choice
set /p choice="Do you want to (S)tart anyway, (R)un setup, or (Q)uit? [S/R/Q]: "

if /i "%choice%"=="S" goto start_anyway
if /i "%choice%"=="R" goto run_setup  
if /i "%choice%"=="Q" goto quit_game

echo Invalid choice. Please enter S, R, or Q.
goto ask_choice

:start_anyway
echo Starting game with missing requirements...
goto start_game

:run_setup
echo.
echo Running interactive setup...
python -m setup.setup_environment
echo.
echo Setup complete! You can now run this launcher again.
pause
exit /b 0

:quit_game
echo Exiting...
pause
exit /b 0

:start_game
echo.
echo ================================================================
echo                     LAUNCHING MONSTER HUNTER GAME
echo ================================================================
echo.
echo Starting backend server...

REM Start backend in a new window
start "Monster Hunter Backend" cmd /k "call venv\Scripts\activate.bat && python -m backend.run && pause"

REM Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo Starting frontend server...

REM Start frontend in a new window  
start "Monster Hunter Frontend" cmd /c "cd frontend && npm start"

echo.
echo ================================================================
echo                        GAME IS RUNNING!
echo ================================================================
echo.
echo 🎮 Game Interface: http://localhost:3000
echo 🔧 Backend API:   http://localhost:5000
echo.
echo Two new windows should have opened:
echo   1. Backend Server (Flask API)
echo   2. Frontend Server (React App)
echo.
echo 💡 Tips:
echo   - Wait for both servers to fully load
echo   - The React app will open in your browser automatically
echo   - Close server windows or press Ctrl+C to stop the game
echo.
echo This launcher window can be closed now.
echo Press any key to exit launcher...
pause > nul
exit /b 0