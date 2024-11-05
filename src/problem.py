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