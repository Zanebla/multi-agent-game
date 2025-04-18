import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
import pytest
from services.llm_service import stream_response, LLMProvider

@pytest.mark.parametrize("provider", [LLMProvider.OPENAI, LLMProvider.DEEPSEEK])
def test_stream_response(provider):
    with patch("services.llm_service.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta = MagicMock(content="测试")
        
        mock_client.chat.completions.create.return_value = [mock_chunk]
        
        response = list(stream_response("测试提示", provider=provider))
        assert len(response) > 0
        assert "测试" in response[0]