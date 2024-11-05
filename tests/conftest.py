import pytest

# Remove the event_loop fixture and instead configure pytest-asyncio globally
def pytest_configure(config):
    """Configure pytest-asyncio to use function scope by default."""
    config.option.asyncio_mode = "strict"
    
# If you need to customize the event loop policy, use this instead
@pytest.fixture(scope="session")
def event_loop_policy():
    """Customize the event loop policy if needed."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy() 