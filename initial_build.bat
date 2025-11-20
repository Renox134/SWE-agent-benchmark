@echo off
title Initial Build Setup
color 0A

echo.
echo ==================================================
echo ===           STARTING INITIAL BUILD           ===
echo ==================================================
echo.

:: --- Step 1: Initialize submodules ---
echo [1/6] Initializing SWE-agent submodule...
git submodule update --init --recursive
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize submodules.
    exit /b 1
)
echo [OK] SWE-agent submodule initialized.
echo.

:: --- Step 2: Enter agent directory ---
cd agent
echo [2/6] Entered agent directory.
echo.

:: --- Step 3: Create virtual environment ---
echo [3/6] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)
echo [OK] Virtual environment created.
echo.

:: --- Step 4: Activate environment ---
call venv\Scripts\activate
echo [4/6] Virtual environment activated.
echo.

:: --- Step 5: Install dependencies ---
echo [5/6] Installing SWE-agent in editable mode...
python -m pip install --upgrade pip
pip install --editable .
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    call venv\Scripts\deactivate
    exit /b 1
)
echo [OK] SWE-agent installation complete.
echo.

:: git config core.autocrlf false
:: git rm --cached -r .
:: git reset --hard

:: --- Step 6: Cleanup ---
call venv\Scripts\deactivate
cd ..
echo [6/6] Build environment deactivated.
echo.

python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
call venv\Scripts\deactivate

echo ==================================================
echo ===           BUILD COMPLETED SUCCESSFULLY      ===
echo ==================================================
echo.
pause
