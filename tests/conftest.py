import sys
import os
from unittest.mock import MagicMock, AsyncMock
import pytest

# Set dummy API key to prevent OpenAI client initialization error during import
os.environ["OPENAI_API_KEY"] = "dummy"

# Global patch for chainlit

# Global patch for chainlit
# This applies to all tests and ensures src.app can be imported without a running Chainlit server.
mock_cl = MagicMock()
mock_cl.on_chat_start = lambda f: f
mock_cl.on_message = lambda f: f
sys.modules["chainlit"] = mock_cl

@pytest.fixture
def mock_cl_fixture():
    """
    Function-scoped fixture to provide and reset the global chainlit mock.
    """
    # Reset mock state before each test
    mock_cl.reset_mock()
    
    # Configure default behaviors usually expected by app code
    mock_cl.user_session = MagicMock()
    mock_cl.user_session.get = MagicMock(return_value=None)
    
    message_instance = AsyncMock()
    mock_cl.Message.return_value = message_instance
    
    return mock_cl
