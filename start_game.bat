@echo off
setlocal
title Monster Hunter Game Launcher

echo.
echo ================================================================
echo                   Monster Hunter Game Launcher
echo ================================================================
echo.
echo This launcher checks that your computer has everything the game
echo needs, sets up whatever is missing, and starts the game.
echo.

REM ================================================================
REM Step 1: Find Python and Node.js - the two free programs the game
REM is built on. This must happen at the .bat level: until Python
REM exists, the Python-based setup cannot run at all.
REM
REM Note: a fresh Windows ships a fake "python" that just opens the
REM Microsoft Store. It fails the --version probe below, so it is
REM correctly treated as "not installed".
REM ================================================================

set "PYTHON_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

set "NODE_OK="
node --version >nul 2>&1
if not errorlevel 1 set "NODE_OK=1"

if defined PYTHON_CMD if defined NODE_OK goto requirements_check

echo This computer is missing free software the game is built on:
if not defined PYTHON_CMD echo    - Python  ^(runs the game's engine^)
if not defined NODE_OK echo    - Node.js ^(runs the game's interface^)
echo.

REM Prefer winget: one command, no wizard. It ships with Windows 10/11.
winget --version >nul 2>&1
if errorlevel 1 goto manual_install

echo Good news: Windows can install these for you automatically.
echo If a popup asks "Do you want to allow this app to make changes?",
echo click Yes - that popup is expected.
echo.
choice /C YN /M "Install the missing software now"
if errorlevel 2 goto manual_install
echo.

if not defined PYTHON_CMD (
    echo Installing Python - this takes a minute or two...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto winget_failed
    echo Python installed!
    echo.
    REM Marks Python handled so a later Node failure doesn't re-show
    REM Python instructions on the manual route. Never executed: every
    REM path from here exits for the close-and-rerun step.
    set "PYTHON_CMD=installed-pending-restart"
)

if not defined NODE_OK (
    echo Installing Node.js - this takes a minute or two...
    winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto winget_failed
    echo Node.js installed!
    echo.
)

echo ================================================================
echo                  Almost there - one more click
echo ================================================================
echo.
echo Freshly installed software is not visible to windows that were
echo already open, like this one.
echo.
echo Please CLOSE this window and double-click start_game.bat again.
echo.
pause
exit /b 0

:winget_failed
echo.
echo The automatic install did not work - no problem, the manual way
echo is easy too.
echo.

:manual_install
echo Here is the manual route ^(about 10 minutes^):
echo.
if not defined PYTHON_CMD (
    echo  PYTHON - the download page is opening in your browser:
    echo    1. Click the big "Download Python" button and run the file
    echo    2. IMPORTANT: on the first screen, tick the checkbox
    echo       "Add python.exe to PATH" before clicking Install
    start https://www.python.org/downloads/
    echo.
)
if not defined NODE_OK (
    echo  NODE.JS - the download page is opening in your browser:
    echo    1. Click the green "LTS" download button and run the file
    echo    2. The standard "Next, Next, Finish" answers are all correct
    start https://nodejs.org/
    echo.
)
echo When the installs finish, double-click start_game.bat again.
echo.
pause
exit /b 1

REM ================================================================
REM Step 2: Everything else (Python packages, MySQL, the database)
REM is handled by the Python-based setup.
REM ================================================================

:requirements_check
echo Checking requirements...
echo.

REM Auto-setup basics (silent unless it has something to install)
%PYTHON_CMD% -m setup.setup_environment auto
if errorlevel 1 (
    echo.
    echo Something went wrong preparing the game's Python environment.
    echo Try closing this window and running start_game.bat again - if
    echo it keeps failing, the messages above say what needs fixing.
    pause
    exit /b 1
)

%PYTHON_CMD% -m setup.check_requirements
if not errorlevel 1 goto start_game

echo.
echo Some things still need to be set up - the walkthrough will guide
echo you through each one.
echo.
set "launch_choice="
set /p launch_choice="Press Enter to run the setup walkthrough (or type S to start the game anyway, Q to quit): "
if /i "%launch_choice%"=="S" goto start_game
if /i "%launch_choice%"=="Q" goto quit_game

echo.
%PYTHON_CMD% -m setup.setup_environment
echo.
goto requirements_check

:quit_game
echo Exiting...
pause
exit /b 0

REM ================================================================
REM Step 3: Start the game (backend + frontend in their own windows)
REM ================================================================

:start_game
echo.
echo ================================================================
echo                     LAUNCHING MONSTER HUNTER GAME
echo ================================================================
echo.
echo Starting backend server...

start "Monster Hunter Backend" cmd /k "call venv\Scripts\activate.bat && python -m backend.run && pause"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo Starting frontend server...
start "Monster Hunter Frontend" cmd /c "cd frontend && npm start"

echo.
echo ================================================================
echo                        GAME IS RUNNING!
echo ================================================================
echo.
echo The game opens in your browser at:  http://localhost:3000
echo (the first start can take a minute - the two new windows show progress)
echo.
echo FIRST TIME PLAYING?
echo   Click the gear icon in the game and paste your DeepSeek API key
echo   (get one at platform.deepseek.com). That key powers all the
echo   story text. Card art is optional - add a Google Gemini key from
echo   aistudio.google.com whenever you like.
echo.
echo To stop the game: close the two server windows.
echo This launcher window can be closed now.
echo.
pause
exit /b 0
