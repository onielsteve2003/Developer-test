# Problem Statement Processor Documentation

## Overview

The Problem Statement Processor is a Python application that leverages OpenAI's GPT models to automatically process, mutate, and manage problem statements. It follows an evolutionary approach where problems go through multiple rounds of mutations and evaluations to generate diverse and high-quality variants.

## Architecture

### Core Components

1. **Problem Management**
   - `Problem` class handles individual problem statements with tracking metadata
   - Reference implementation:

```1:28:src/problem.py
from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Problem:
    id: UUID
    content: str
    score: float = 0.0
    parent_id: Optional[UUID] = None
    mutations: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.mutations is None:
            self.mutations = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def create(cls, content: str, parent_id: Optional[UUID] = None) -> 'Problem':
        return cls(
            id=uuid4(),
            content=content,
            parent_id=parent_id,
            score=0.0
        )
```

2; **Mutation System**

- `MutationHandler` manages different mutation strategies using OpenAI's API
- Supported strategies: rephrase, expand, simplify, add_constraints
- Reference implementation:

```1:45:src/mutation.py
import openai
from typing import List
from pathlib import Path
from .problem import Problem

class MutationHandler:
    def __init__(self, config):
        self.config = config
        self.prompt_dir = Path("output/prompts/mutations")
        openai.api_key = config.openai_api_key
        
    def load_prompt(self, mutation_type: str) -> str:
        prompt_path = self.prompt_dir / f"{mutation_type}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text()
    
    async def mutate(self, problem: Problem, mutation_type: str) -> Problem:
        prompt_template = self.load_prompt(mutation_type)
        prompt = prompt_template.format(problem=problem.content)
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.config.agent,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": problem.content}
                ]
            )
            new_content = response['choices'][0]['message']['content']
            new_problem = Problem.create(
                content=new_content,
                parent_id=problem.id
            )
            new_problem.mutations = problem.mutations + [mutation_type]
            return new_problem
        except Exception as e:
            raise RuntimeError(f"Mutation failed: {str(e)}")
    # Add the 'add_constraints' strategy
    mutation_types = [
        "rephrase",
        "expand", 
        "simplify",
        "add_constraints"
 
```

3; **Processing Pipeline**

- `ProblemProcessor` orchestrates the entire workflow
- Handles loading, processing, evaluation, and saving of problems
- Reference implementation:

```11:198:src/processor.py
class ProblemProcessor:
    """
    Core processor for managing problem mutations and evolution.
    
    This class handles the loading, processing, and saving of problems,
    as well as managing the mutation workflow through multiple rounds.
    
    Attributes:
        config: Configuration object containing processing parameters
        mutation_handler: Handler for applying mutations to problems
    """
    
    def __init__(self, config):
        """
        Initialize the processor with configuration.
        
        Args:
            config: Configuration object with processing parameters
        """
        self.config = config
        self.mutation_handler = MutationHandler(config)
        random.seed(config.seed)
        logging.basicConfig(
            filename='processing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def load_problems(self) -> List[Problem]:
        """
        Load problems from the problems.txt file.
        
        Returns:
            List[Problem]: List of initialized Problem objects
            
        Raises:
            FileNotFoundError: If problems.txt is not found
        """
        problems_path = Path("problems/problems.txt")
        if not problems_path.exists():
            raise FileNotFoundError("problems.txt not found")
            
        with open(problems_path) as f:
            return [Problem.create(line.strip()) for line in f if line.strip()]
    ...
    async def process_round(self, problems: List[Problem]) -> List[Problem]:
        """
        Process a single round of problem mutations.
        
        Args:
            problems: List of problems to process
            
        Returns:
            List[Problem]: Top-k problems after mutation and scoring
            
        Note:
            This method applies random mutations to selected problems
            and retains only the top-performing variants.
        """
        logging.info(f"Starting processing round with {len(problems)} problems")
        
        with tqdm(total=len(problems), desc="Processing problems") as pbar:
            selected_problems = random.sample(
                problems, 
                min(self.config.num_problems, len(problems))
            )
            
            mutation_types = ["rephrase", "expand", "simplify"]
            new_problems = []
            
            for problem in selected_problems:
                mutation_type = random.choice(mutation_types)
                try:
                    new_problem = await self.mutation_handler.mutate(problem, mutation_type)
                    new_problems.append(new_problem)
                    self.save_problem(new_problem)
                except Exception as e:
                    print(f"Error processing problem {problem.id}: {str(e)}")
                
                pbar.update(1)
        logging.info(f"Round completed. Generated {len(new_problems)} new variants")
        return sorted(
            new_problems + problems,
            key=lambda x: x.score,
            reverse=True
        )[:self.config.topk_problems]
    def evaluate_problem(self, problem: Problem) -> float:
        """
        Evaluate problem quality based on multiple factors.
        
        Factors considered:
        - Complexity (based on word count and structure)
        - Clarity (based on readability metrics)
        - Diversity (compared to other problems)
        - Mutation history
        
        Returns:
            float: Score between 0 and 1
        """
        # Implement actual scoring logic
        factors = {
            'complexity': self._calculate_complexity(problem),
            'clarity': self._calculate_clarity(problem),
            'diversity': self._calculate_diversity(problem),
            'mutation_quality': len(problem.mutations) / 10
        }
        
        return sum(factors.values()) / len(factors)
    
    def _calculate_complexity(self, problem: Problem) -> float:
        """
        Calculate problem complexity based on:
        - Word count
        - Technical terms
        - Nested requirements
        """
        words = problem.content.split()
        word_count = len(words)
        
        # Basic complexity based on length
        length_score = min(word_count / 100, 1.0)
        
        # Technical complexity based on keywords
        technical_terms = ['implement', 'design', 'optimize', 'algorithm', 'system']
        tech_score = sum(1 for word in words if word.lower() in technical_terms) / len(technical_terms)
        
        # Nested complexity based on bullet points or numbered lists
        nested_score = problem.content.count('\n- ') / 10
        
        return (length_score + tech_score + nested_score) / 3
    def _calculate_clarity(self, problem: Problem) -> float:
        """
        Calculate problem clarity based on:
        - Sentence structure
        - Readability
        - Formatting
        """
        # Readability score
        readability = textstat.flesch_reading_ease(problem.content) / 100
        
        # Structure score based on paragraphs
        paragraphs = problem.content.count('\n\n') + 1
        structure_score = min(paragraphs / 5, 1.0)
        
        # Format score based on consistent formatting
        format_score = 1.0 if problem.content.strip() == problem.content else 0.8
        
        return (readability + structure_score + format_score) / 3
    
    def _calculate_diversity(self, problem: Problem) -> float:
        """
        Calculate problem diversity based on:
        - Uniqueness compared to other problems
        - Variety of concepts
        - Innovation in approach
        """
        # Implement actual diversity calculation using NLP techniques
        # For now, use a simplified scoring based on mutation history
        mutation_variety = len(set(problem.mutations))
        return min(mutation_variety / 3, 1.0)
    
    async def cleanup(self):
        """Ensure proper cleanup of resources"""
        try:
            await self.mutation_handler.close()
            # Add any other cleanup needed
        except Exception as e:
            logging.error(f"Cleanup error: {e}")
```

## Installation

1. Clone the repository and set up the environment:

```bash
git clone <repository-url>
cd problem-processor
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

2; Set up your OpenAI API key:

```bash
export OPENAI_API_KEY='your-api-key-here'  # On Linux/Mac
set OPENAI_API_KEY='your-api-key-here'     # On Windows
```

## Usage

### Basic Usage

Run the processor with default settings:

```bash
python -m src.main --openai_api_key=$OPENAI_API_KEY
```

### Advanced Usage

Customize processing parameters:

```bash
python -m src.main \
    --seed=42 \
    --agent=gpt-4 \
    --num_rounds=3 \
    --num_problems=5 \
    --topk_problems=3 \
    --mutate_on_start \
    --openai_api_key=$OPENAI_API_KEY
```

### Command Line Arguments

- `--seed`: Integer seed for random operations
- `--agent`: AI agent to use (e.g., gpt-4)
- `--num_rounds`: Number of processing rounds
- `--num_problems`: Number of problems to process per round
- `--topk_problems`: Number of top-performing problems to retain
- `--mutate_on_start`: Flag to determine if mutation occurs at start
- `--openai_api_key`: OpenAI API key

## Configuration

### Directory Structure

```text
problem-processor/
├── problems/
│   └── problems.txt         # Input problem statements
├── output/                  # Processed problem outputs
├── prompts/
│   └─ mutations/          # Mutation prompt templates
├── scripts/                # Utility scripts
├── src/
│   ├── __init__.py
│   ├── process_problems.py # Main entry point
│   ├── processor.py        # Core processing logic
│   ├── mutation.py         # Mutation handling
│   ├── problem.py         # Problem data structure
│   └── config.py          # Configuration management
├── tests/                  # Unit tests
├── leaderboard.yaml       # Result tracking
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

### Mutation Strategies

The system supports multiple mutation strategies, each with its own prompt template:

1. **Rephrase**
   - Maintains core requirements while improving clarity
   - Reference implementation:

```1:19:output/prompts/mutations/rephrase.txt
description: "Rephrase the problem while maintaining its core requirements"
template: |
  You are a technical problem curator. Rephrase the following problem statement to be clearer and more precise, while keeping the same technical requirements:

  Original problem:
  {problem}

  Rules for rephrasing:
  1. Maintain the same difficulty level
  2. Keep all core requirements
  3. Use clear, unambiguous language
  4. Preserve any specific constraints
  5. Ensure technical accuracy

  Please provide the rephrased version only, without explanations or additional notes.

examples:
  - input: "Given an array of integers, find the longest increasing subsequence."
  - output: "Implement a function that takes an integer array and returns the length of the longest strictly increasing subsequence of numbers within the array."
```

2; **Expand**

- Adds additional requirements while maintaining coherence
- Reference implementation:

```1:15:output/prompts/mutations/expand.txt
description: "Expand the problem with additional requirements"
template: |
  As a technical problem designer, expand the following problem with additional meaningful requirements:

  Original problem:
  {problem}

  Rules for expansion:
  1. Add 2-3 new relevant requirements
  2. Ensure additions are logically connected
  3. Maintain problem coherence
  4. Keep difficulty increase reasonable
  5. Add practical use cases if applicable

  Provide the expanded version only, without explanations.
```

3; **Simplify**

- Reduces complexity while preserving core concepts
- Reference implementation:

```1:15:output/prompts/mutations/simplify.txt
description: "Simplify the problem while maintaining its core concept"
template: |
  As a problem simplification expert, modify the following problem to be more approachable while keeping its fundamental concept:

  Original problem:
  {problem}

  Rules for simplification:
  1. Reduce the number of requirements
  2. Remove advanced features if present
  3. Focus on the core problem
  4. Keep it technically meaningful
  5. Maintain at least one clear challenge

  Provide only the simplified version, without explanations.
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest tests/test_processor.py
pytest tests/test_mutation.py
pytest tests/test_problem.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Error Handling

The system implements comprehensive error handling for:

1. **Input Validation**
   - Missing/malformed problems.txt
   - Invalid configuration parameters
   - Malformed problem statements

2. **API Operations**
   - OpenAI API failures
   - Rate limiting handling
   - Response validation

3. **File Operations**
   - File not found errors
   - Permission issues
   - I/O errors

4. **Process Management**
   - Subprocess execution errors
   - Resource cleanup
   - Timeout handling

Example error handling implementation:

```python:src/main.py
try:
    processor.run()
except FileNotFoundError as e:
    logging.error(f"Required file not found: {e}")
    sys.exit(1)
except OpenAIError as e:
    logging.error(f"OpenAI API error: {e}")
    sys.exit(1)
except IOError as e:
    logging.error(f"I/O error: {e}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit(1)
```

## Evaluation Metrics

Problems are evaluated based on multiple factors:

- Complexity (word count, technical terms)
- Clarity (readability metrics)
- Diversity (compared to other variants)
- Mutation history

Reference implementation:

```116:190:src/processor.py
    def evaluate_problem(self, problem: Problem) -> float:
        """
        Evaluate problem quality based on multiple factors.
        
        Factors considered:
        - Complexity (based on word count and structure)
        - Clarity (based on readability metrics)
        - Diversity (compared to other problems)
        - Mutation history
        
        Returns:
            float: Score between 0 and 1
        """
        # Implement actual scoring logic
        factors = {
            'complexity': self._calculate_complexity(problem),
            'clarity': self._calculate_clarity(problem),
            'diversity': self._calculate_diversity(problem),
            'mutation_quality': len(problem.mutations) / 10
        }
        
        return sum(factors.values()) / len(factors)
    
    def _calculate_complexity(self, problem: Problem) -> float:
        """
        Calculate problem complexity based on:
        - Word count
        - Technical terms
        - Nested requirements
        """
        words = problem.content.split()
        word_count = len(words)
        
        # Basic complexity based on length
        length_score = min(word_count / 100, 1.0)
        
        # Technical complexity based on keywords
        technical_terms = ['implement', 'design', 'optimize', 'algorithm', 'system']
        tech_score = sum(1 for word in words if word.lower() in technical_terms) / len(technical_terms)
        
        # Nested complexity based on bullet points or numbered lists
        nested_score = problem.content.count('\n- ') / 10
        
        return (length_score + tech_score + nested_score) / 3
    def _calculate_clarity(self, problem: Problem) -> float:
        """
        Calculate problem clarity based on:
        - Sentence structure
        - Readability
        - Formatting
        """
        # Readability score
        readability = textstat.flesch_reading_ease(problem.content) / 100
        
        # Structure score based on paragraphs
        paragraphs = problem.content.count('\n\n') + 1
        structure_score = min(paragraphs / 5, 1.0)
        
        # Format score based on consistent formatting
        format_score = 1.0 if problem.content.strip() == problem.content else 0.8
        
        return (readability + structure_score + format_score) / 3
    
    def _calculate_diversity(self, problem: Problem) -> float:
        """
        Calculate problem diversity based on:
        - Uniqueness compared to other problems
        - Variety of concepts
        - Innovation in approach
        """
        # Implement actual diversity calculation using NLP techniques
        # For now, use a simplified scoring based on mutation history
        mutation_variety = len(set(problem.mutations))
        return min(mutation_variety / 3, 1.0)
```

## Dependencies

Required packages:

- argparse: Command-line argument parsing
- dataclasses: Structured data management  
- os, random, re, subprocess, time, uuid: System operations
- yaml: Configuration and result storage
- nbformat: Jupyter notebook handling (if applicable)
- openai: OpenAI API integration
- typing: Type annotations

## Result Tracking

The system maintains:

1. **Leaderboard** (leaderboard.yaml)
   - Records problem names and scores
   - Updated after each processing round
   - Tracks mutation history

2. **Processing Logs** (processing.log)
   - Detailed processing steps
   - Mutation operations
   - Error tracking

## Testing

### Test Coverage

The test suite covers:

- Problem mutation functions
- File handling operations
- Configuration management
- Processing workflow
- Error handling scenarios

### Running Tests

```bash
# Run all tests with coverage report
pytest --cov=src tests/

# Run specific test categories
pytest tests/test_processor.py
pytest tests/test_mutation.py
pytest tests/test_problem.py
```

### Writing Tests

When contributing new features:

1. Add corresponding test cases
2. Ensure >80% code coverage
3. Test error handling scenarios
4. Include integration tests where appropriate

## Utility Scripts

### Clean Script

The `scripts/clean.sh` utility script helps maintain a clean development environment:

```bash
# Usage
./scripts/clean.sh

# Or with specific options
./scripts/clean.sh --all    # Remove all generated files
./scripts/clean.sh --cache  # Remove only cache files
```

Functions:

- Removes Python cache files (`*.pyc`, `__pycache__`)
- Cleans up output directory
- Resets leaderboard.yaml
- Removes log files
- Cleans temporary processing files

Example implementation:

```bash:scripts/clean.sh
#!/bin/bash

# Remove Python cache
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -r {} +

# Clean output directory
rm -rf output/*

# Reset leaderboard
echo "problems: []" > leaderboard.yaml

# Remove logs
rm -f processing.log

# Clean temp files
rm -f ./*.tmp
```

Note: Run this script before committing code or when you want to start fresh.

## Quick Start

1. **Setup Environment**

```bash
./scripts/setup.sh
```

This will:

- Create Python virtual environment
- Install dependencies
- Set up directory structure
- Configure initial settings

2; **Run the Processor**

```bash
./scripts/run.sh
```

This provides an interactive way to:

- Choose processing mode (basic/advanced)
- Set OpenAI API key
- Select mutation strategies
- Start processing

The `scripts/` directory contains several utilities to make development and usage easier:

### 1. Setup Script (`setup.sh`)

```bash
./scripts/setup.sh [--dev] [--prod]
```

Functions:

- Creates Python virtual environment
- Installs required dependencies
- Sets up directory structure
- Configures initial settings
- `--dev` flag installs development dependencies
- `--prod` flag optimizes for production

### 2. Run Script (`run.sh`)

```bash
./scripts/run.sh [--interactive] [--config=path/to/config]
```

Functions:

- Interactive mode for easy configuration
- Loads environment variables
- Validates OpenAI API key
- Provides processing mode selection
- Handles common runtime scenarios

### 3. Clean Script (`clean.sh`)

```bash
./scripts/clean.sh [--all] [--cache] [--output]
```

Functions:

- Removes Python cache (`*.pyc`, `__pycache__`)
- Cleans output directory
- Resets leaderboard.yaml
- Removes log files
- Cleans temporary files

### 4. Development Helper (`dev.sh`)

```bash
./scripts/dev.sh [command]
```

Commands:

- `test`: Run test suite with coverage
- `lint`: Run code linting
- `format`: Format code with black
- `check`: Run all checks (test, lint, type-check)
- `docs`: Generate documentation

Example implementations:

```bash:scripts/setup.sh
#!/bin/bash
set -e

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
if [[ "$1" == "--dev" ]]; then
    pip install -r requirements-dev.txt
else
    pip install -r requirements.txt
fi

# Create directory structure
mkdir -p problems output prompts/mutations

# Initialize config
if [[ ! -f config.yaml ]]; then
    cp config.example.yaml config.yaml
fi

echo "Setup complete! Run './scripts/run.sh' to start processing"
```
