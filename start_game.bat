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
python setup/basic_backend.py auto
if errorlevel 1 (
    echo ERROR: Basic backend setup failed
    pause
    exit /b 1
)

REM Step 2: Check all requirements (summary mode)
python check_requirements.py summary
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
python setup_environment.py
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
echo Launching Monster Hunter Game...
echo.
echo ================================================================
echo                        GAME IS RUNNING!
echo                    (Placeholder for actual game)
echo ================================================================
echo.
echo Backend would start: 
echo Frontend would start: 
echo Game URL: http://localhost:3000
echo.
echo Press Ctrl+C to stop the game when it's actually implemented.
pause
exit /b 0