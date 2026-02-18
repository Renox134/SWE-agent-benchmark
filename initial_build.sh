#!/usr/bin/env bash

echo
echo "=================================================="
echo "===           STARTING INITIAL BUILD           ==="
echo "=================================================="
echo

# --- Step 1: Initialize submodule ---
echo "[1/2] Initializing SWE-agent submodule..."
git submodule update --init --recursive
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize submodules."
    exit 1
fi
echo "[OK] SWE-agent submodule initialized."
echo

# --- Step 2: Create venv and install dependencies ---
cd ..
echo "[2/2] Create venv and install dependencies..."
echo

python3 -m venv venv || {
    echo "ERROR: Failed to create virtual environment."
    exit 1
}

source venv/bin/activate || {
    echo "ERROR: Failed to activate virtual environment."
    exit 1
}

pip install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies."
    exit 1
}

echo "=================================================="
echo "===        BUILD COMPLETED SUCCESSFULLY        ==="
echo "=================================================="
echo

read -p "Press Enter to continue..."
