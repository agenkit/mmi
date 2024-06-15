#!/bin/bash

# This script opens a new Konsole window and runs the main.py Python script.

# Path to your main.py file
PYTHON_SCRIPT="./main.py"

# Full path to the Python interpreter
PYTHON_PATH="/home/c/miniconda3/bin/python3"

# Command to open a new Konsole window and run the Python script
konsole -e $PYTHON_PATH "$PYTHON_SCRIPT"
