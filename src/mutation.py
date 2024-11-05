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
    ]

    # Implement the add_constraints method
    async def add_constraints(self, problem: Problem) -> Problem:
        prompt_template = self.load_prompt("add_constraints")
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
            new_problem.mutations = problem.mutations + ["add_constraints"]
            return new_problem
        except Exception as e:
            raise RuntimeError(f"Mutation failed: {str(e)}")