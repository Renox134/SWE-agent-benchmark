@echo off
title Initial Build Setup

echo.
echo ==================================================
echo ===           STARTING INITIAL BUILD           ===
echo ==================================================
echo.

:: --- Step 1: Initialize submodule ---
echo [1/4] Initializing SWE-agent submodule...
git submodule update --init --recursive
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize submodules.
    exit /b 1
)
echo [OK] SWE-agent submodule initialized.
echo.

:: --- Step 2: Enter agent directory ---
cd agent
echo [2/4] Entered agent directory.
echo.

:: --- Step 3: Clean-reset the agent with CRLF conversion disabled ---
echo [3/4] Clean reset the agent with CRLF conversion disabled
git config core.autocrlf false
git rm --cached -r .
git reset --hard
if %errorlevel% neq 0 (
    echo ERROR: Failed to clean reset the agent submodule.
    exit /b 1
)
echo [OK] Agent setup complete
echo.

:: --- Step 4: Create venv and install dependencies ---
cd ..
echo [4/4] Create venv and install dependencies...
echo.
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo ==================================================
echo ===           BUILD COMPLETED SUCCESSFULLY      ===
echo ==================================================
echo.
pause
