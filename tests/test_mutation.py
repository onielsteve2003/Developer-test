import pytest
from unittest.mock import Mock, patch
from src.mutation import MutationHandler
from src.problem import Problem
from pathlib import Path

@pytest.fixture
def config():
    config = Mock()
    config.agent = "gpt-4"
    config.openai_api_key = "test-key"
    return config

@pytest.fixture
def handler(config):
    return MutationHandler(config)

def test_load_prompt(handler, tmp_path):
    # Create a temporary prompt file
    prompt_dir = tmp_path / "output/prompts/mutations"
    prompt_dir.mkdir(parents=True)
    prompt_file = prompt_dir.joinpath("test.txt")
    prompt_file.write_text("Test prompt content")
    
    # Patch the prompt directory
    handler.prompt_dir = prompt_dir
    
    content = handler.load_prompt("test")
    assert content == "Test prompt content"

def test_load_prompt_missing_file(handler):
    with pytest.raises(FileNotFoundError):
        handler.load_prompt("nonexistent")

@pytest.mark.asyncio(scope="function")
async def test_mutate(handler):
    problem = Problem.create("Test problem")
    
    # Mock OpenAI response
    mock_response = {
        'choices': [{
            'message': {
                'content': 'Mutated content'
            }
        }]
    }
    
    with patch('openai.ChatCompletion.acreate', return_value=mock_response):
        mutated = await handler.mutate(problem, "rephrase")
        
        assert mutated.content == "Mutated content"
        assert mutated.parent_id == problem.id
        assert "rephrase" in mutated.mutations 