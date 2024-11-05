import pytest
from uuid import UUID
from datetime import datetime
from src.problem import Problem

def test_problem_creation():
    content = "Test problem content"
    problem = Problem.create(content)
    
    assert isinstance(problem.id, UUID)
    assert problem.content == content
    assert problem.score == 0.0
    assert problem.parent_id is None
    assert isinstance(problem.mutations, list)
    assert len(problem.mutations) == 0
    assert isinstance(problem.created_at, datetime)

def test_problem_with_parent():
    parent_id = UUID('12345678-1234-5678-1234-567812345678')
    problem = Problem.create("Test content", parent_id)
    
    assert problem.parent_id == parent_id

def test_mutations_list():
    problem = Problem.create("Test content")
    problem.mutations.append("rephrase")
    
    assert "rephrase" in problem.mutations
    assert len(problem.mutations) == 1 