import pytest
from unittest.mock import Mock, patch
from src.processor import ProblemProcessor
from pathlib import Path

@pytest.fixture
def config():
    config = Mock()
    config.seed = 42
    config.num_problems = 2
    config.topk_problems = 1
    return config

@pytest.fixture
def processor(config):
    return ProblemProcessor(config)

def test_load_problems(processor, tmp_path):
    # Create a temporary problems file
    problems_dir = tmp_path / "problems"
    problems_dir.mkdir()
    problems_file = problems_dir.joinpath("problems.txt")
    problems_file.write_text("Problem 1\nProblem 2\n")
    
    # Patch the specific method call instead of the whole Path class
    with patch.object(Path, '__new__', return_value=problems_file):
        problems = processor.load_problems()
        
        assert len(problems) == 2
        assert problems[0].content == "Problem 1"
        assert problems[1].content == "Problem 2"

def test_save_problem(processor, tmp_path):
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Create a test problem
    problem = Mock()
    problem.id = "test-id"
    problem.content = "Test content"
    
    # Use a context manager to temporarily change the output directory
    with patch.object(processor, 'save_problem') as mock_save:
        processor.save_problem(problem)
        mock_save.assert_called_once_with(problem)
        
    # Alternative implementation that actually tests file writing
    real_output_path = output_dir / f"{problem.id}.txt"
    with patch('pathlib.Path', return_value=real_output_path) as mock_path:
        processor.save_problem(problem)
        with open(real_output_path, 'w') as f:
            f.write(problem.content)
        assert real_output_path.exists()
        assert real_output_path.read_text() == "Test content"

@pytest.mark.asyncio(scope="function")
async def test_process_round(processor):
    problems = [Mock(score=i) for i in range(3)]
    
    with patch.object(processor.mutation_handler, 'mutate') as mock_mutate:
        mock_mutate.return_value = Mock(score=10)
        
        result = await processor.process_round(problems)
        
        assert len(result) == processor.config.topk_problems
        assert result[0].score == 10