from dataclasses import dataclass
from typing import Optional
import yaml
from pathlib import Path
from datetime import datetime
from .exceptions import ValidationError

@dataclass
class Config:
    seed: int
    agent: str
    num_rounds: int
    num_problems: int
    topk_problems: int
    mutate_on_start: bool
    openai_api_key: str
    current_round: int = 0

    @classmethod
    def from_args(cls, args) -> 'Config':
        # Add validation
        if args.num_rounds < 1:
            raise ValidationError("num_rounds must be positive")
        if args.num_problems < 1:
            raise ValidationError("num_problems must be positive")
        if args.topk_problems < 1:
            raise ValidationError("topk_problems must be positive")
        if args.topk_problems > args.num_problems:
            raise ValidationError("topk_problems cannot exceed num_problems")
        
        return cls(
            seed=args.seed,
            agent=args.agent,
            num_rounds=args.num_rounds,
            num_problems=args.num_problems,
            topk_problems=args.topk_problems,
            mutate_on_start=args.mutate_on_start,
            openai_api_key=args.openai_api_key
        )

    def save_leaderboard(self, problems: list, path: str = "leaderboard.yaml"):
        data = {
            "timestamp": datetime.now().isoformat(),
            "round_number": self.current_round,
            "problems": [
                {
                    "id": str(p.id),
                    "score": p.score,
                    "mutations": p.mutations,
                    "quality_metrics": {}
                } for p in sorted(problems, key=lambda x: x.score, reverse=True)
            ]
        }
        with open(path, 'w') as f:
            yaml.dump(data, f) 