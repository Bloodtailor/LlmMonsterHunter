@echo off
REM Monster Hunter Game - Main Launcher
REM Automatically checks requirements and starts the game

title Monster Hunter Game Launcher

echo.
echo ================================================================
echo                   Monster Hunter Game Launcher
echo ================================================================
echo.

REM Step 1: Run basic backend setup automatically
echo [1/4] Setting up basic backend environment...
python setup/basic_backend.py
if errorlevel 1 (
    echo ERROR: Basic backend setup failed
    pause
    exit /b 1
)

REM Step 2: Check all requirements
echo.
echo [2/4] Checking system requirements...
python check_requirements.py
set "requirements_result=%errorlevel%"

REM Step 3: Decide what to do based on requirements
echo.
if %requirements_result%==0 (
    echo [3/4] All requirements met! Starting game...
    goto :start_game
) else (
    echo [3/4] Some requirements are missing.
    echo.
    set /p "user_choice=Do you want to (S)tart anyway, (R)un setup, or (Q)uit? [S/R/Q]: "
    
    if /i "%user_choice%"=="S" (
        echo Starting game with missing requirements...
        goto :start_game
    ) else if /i "%user_choice%"=="R" (
        echo Running interactive setup...
        python setup_environment.py
        echo.
        echo Setup complete! You can now run this launcher again.
        pause
        exit /b 0
    ) else (
        echo Exiting...
        pause
        exit /b 0
    )
)

:start_game
echo.
echo [4/4] Launching Monster Hunter Game...
echo.
echo ================================================================
echo                        GAME IS RUNNING!
echo                    (Placeholder for actual game)
echo ================================================================
echo.
echo Backend would start: python backend/run.py
echo Frontend would start: cd frontend && npm start
echo Game URL: http://localhost:3000
echo.
echo Press Ctrl+C to stop the game when it's actually implemented.
pause
exit /b 0