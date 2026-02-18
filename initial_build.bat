@echo off
title Initial Build Setup

echo.
echo ==================================================
echo ===           STARTING INITIAL BUILD           ===
echo ==================================================
echo.

:: --- Step 1: Initialize submodule ---
echo [1/2] Initializing SWE-agent submodule...
git submodule update --init --recursive
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize submodules.
    exit /b 1
)
echo [OK] SWE-agent submodule initialized.
echo.

:: --- Step 4: Create venv and install dependencies ---
echo [1/2] Create venv and install dependencies...
echo.
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo ==================================================
echo ===           BUILD COMPLETED SUCCESSFULLY      ===
echo ==================================================
echo.
pause
