#!/bin/bash

# Example script showing different ways to run the processor

# Basic run with default settings
echo "Running with default settings..."
python -m src.main --openai_api_key=$OPENAI_API_KEY

# Run with custom parameters
echo "Running with custom parameters..."
python -m src.main \
    --seed=42 \
    --agent=gpt-4 \
    --num_rounds=3 \
    --num_problems=5 \
    --topk_problems=3 \
    --mutate_on_start \
    --openai_api_key=$OPENAI_API_KEY

# Run with different configurations for testing
echo "Running test configuration..."
python -m src.main \
    --seed=123 \
    --agent=gpt-3.5-turbo \
    --num_rounds=2 \
    --num_problems=3 \
    --topk_problems=2 \
    --openai_api_key=$OPENAI_API_KEY 