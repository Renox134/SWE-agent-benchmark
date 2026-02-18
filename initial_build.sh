#!/usr/bin/env bash

echo
echo "=================================================="
echo "===           STARTING INITIAL BUILD           ==="
echo "=================================================="
echo

# --- Step 1: Initialize submodule ---
echo "[1/4] Initializing SWE-agent submodule..."
git submodule update --init --recursive
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize submodules."
    exit 1
fi
echo "[OK] SWE-agent submodule initialized."
echo

# --- Step 2: Enter agent directory ---
cd agent || {
    echo "ERROR: Could not enter agent directory."
    exit 1
}
echo "[2/4] Entered agent directory."
echo

# --- Step 3: Clean-reset the agent with CRLF conversion disabled ---
echo "[3/4] Clean reset the agent with CRLF conversion disabled"
git config core.autocrlf false
git rm --cached -r .
git reset --hard
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to clean reset the agent submodule."
    exit 1
fi
echo "[OK] Agent setup complete"
echo

# --- Step 4: Create venv and install dependencies ---
cd ..
echo "[4/4] Create venv and install dependencies..."
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
