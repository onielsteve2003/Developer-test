#!/bin/bash

# Clean script to remove generated files and reset the workspace

# Clean output directory but preserve prompt templates
find output -type f ! -path "output/prompts/mutations/*" -delete

# Clean logs
rm -f processing.log

# Clean pycache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Clean test cache
rm -rf .pytest_cache
rm -rf .coverage

echo "Cleanup complete!" 