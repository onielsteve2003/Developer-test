#!/bin/bash

# Setup script for the Problem Statement Processor

# Create required directories if they don't exist
mkdir -p problems
mkdir -p output
mkdir -p output/prompts/mutations
mkdir -p tests

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable is not set"
    echo "Please set it using: export OPENAI_API_KEY='your-api-key'"
fi

echo "Setup complete!" 