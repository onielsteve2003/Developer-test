import argparse
import asyncio
from pathlib import Path
from .config import Config
from .processor import ProblemProcessor
from .exceptions import (
    ProcessingError,
    ConfigurationError,
    MutationError,
    ResourceError,
    ValidationError
)
import logging

def parse_args():
    parser = argparse.ArgumentParser(description="Problem Statement Processor")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--agent", type=str, default="gpt-4")
    parser.add_argument("--num_rounds", type=int, default=5)
    parser.add_argument("--num_problems", type=int, default=10)
    parser.add_argument("--topk_problems", type=int, default=5)
    parser.add_argument("--mutate_on_start", action="store_true")
    parser.add_argument("--openai_api_key", type=str, required=True)
    return parser.parse_args()

async def main():
    try:
        args = parse_args()
        config = Config.from_args(args)
        
        processor = ProblemProcessor(config)
        
        problems = processor.load_problems()
        
        if config.mutate_on_start:
            problems = await processor.process_round(problems)
            
        for round_num in range(config.num_rounds):
            print(f"Processing round {round_num + 1}/{config.num_rounds}")
            problems = await processor.process_round(problems)
            config.save_leaderboard(problems)
            
    except ConfigurationError as e:
        logging.error(f"Configuration error: {e}")
        return 1
    except MutationError as e:
        logging.error(f"Mutation error: {e}")
        return 1
    except ResourceError as e:
        logging.error(f"Resource error: {e}")
        return 1
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main()) 