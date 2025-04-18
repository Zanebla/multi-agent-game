import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, MagicMock
import pytest
from services.websocket_service import WebSocketService

@pytest.fixture
def mock_sio():
    sio = MagicMock()
    sio.emit = AsyncMock()
    sio.save_session = AsyncMock()  # 添加save_session的mock
    return sio

@pytest.fixture
def mock_agents():
    return {"PM": MagicMock(), "SDE": MagicMock()}

@pytest.fixture
def ws_service(mock_sio, mock_agents):
    return WebSocketService(mock_sio, mock_agents)

@pytest.mark.asyncio
async def test_handle_connect(ws_service):
    await ws_service.handle_connect("test_sid", {})
    ws_service.sio.save_session.assert_called_once()

@pytest.mark.asyncio
async def test_stream_agent_response(ws_service, mock_agents):
    # 修改异步生成器mock以接收参数
    async def mock_stream(prompt):
        yield "测试"
        yield "响应"
    
    mock_agent = mock_agents["PM"]
    mock_agent.stream_response = mock_stream
    
    response = await ws_service.stream_agent_response("PM", "测试输入", "test_sid", "conv123")
    assert response == "测试响应"
    ws_service.sio.emit.assert_called()