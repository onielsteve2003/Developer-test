#!/bin/bash

# Add project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Script to run tests with different configurations

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run basic tests
echo "Running basic tests..."
pytest

# Run with coverage report
echo "Running tests with coverage..."
pytest --cov=src tests/

# Run with verbose output
echo "Running verbose tests..."
pytest -v

# Run specific test categories
echo "Running processor tests..."
pytest tests/test_processor.py
echo "Running mutation tests..."
pytest tests/test_mutation.py
echo "Running problem tests..."
pytest tests/test_problem.py 