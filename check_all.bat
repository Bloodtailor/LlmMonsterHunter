@echo off
title Monster Hunter Game - Pre-Push Checks

echo.
echo ================================================================
echo            Monster Hunter Game - Pre-Push Checks
echo ================================================================
echo.
echo Runs the same seven checks GitHub runs on a pull request.
echo All green here means a green PR.
echo.

REM The venv is created by the setup that start_game.bat runs - judge
REM by the interpreter inside it, not the folder
if not exist "venv\Scripts\python.exe" (
    echo The game's Python environment is not set up yet.
    echo Run start_game.bat first - it sets everything up for you.
    pause
    exit /b 1
)

REM MySQL must be running for the offline suites to connect
venv\Scripts\python.exe tools\check_all.py
set CHECK_RESULT=%ERRORLEVEL%

echo.
if %CHECK_RESULT% NEQ 0 (
    echo ================================================================
    echo  Something needs fixing before you push. Details are above.
    echo ================================================================
) else (
    echo ================================================================
    echo  Everything passed - safe to push.
    echo ================================================================
)

echo.
pause
exit /b %CHECK_RESULT%
