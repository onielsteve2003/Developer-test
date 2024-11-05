import asyncio
from typing import List
from pathlib import Path
import random
from .problem import Problem
from .mutation import MutationHandler
import logging
from tqdm import tqdm
import textstat

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
    
    def save_problem(self, problem: Problem):
        """
        Save a problem to the output directory.
        
        Args:
            problem: Problem object to save
            
        Raises:
            IOError: If writing to output directory fails
        """
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{problem.id}.txt"
        with open(output_path, "w") as f:
            f.write(problem.content)
    
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
                    new_problem.score = self.evaluate_problem(new_problem)
                    new_problems.append(new_problem)
                    self.save_problem(new_problem)
                except Exception as e:
                    print(f"Error processing problem {problem.id}: {str(e)}")
                
                pbar.update(1)
                
        logging.info(f"Round completed. Generated {len(new_problems)} new variants")
        
        for problem in problems:
            if problem.score == 0:
                problem.score = self.evaluate_problem(problem)
                
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
    
    def handle_errors(self):
        """
        Handle specific error cases:
        - Missing/malformed problems.txt
        - API failures
        - File I/O issues
        - Subprocess errors
        """
        pass