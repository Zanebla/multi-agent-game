import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, MagicMock
import pytest
from core.agents import Agent
from core.roles import Role

@pytest.fixture
def mock_role():
    return Role(name="测试角色", expertise="测试领域", personality="严谨")

@pytest.fixture
def agent(mock_role):
    return Agent(mock_role)

@pytest.mark.asyncio
async def test_agent_generate_prompt(agent):
    prompt = agent.generate_prompt("测试输入")
    assert "测试角色" in prompt
    assert "测试领域" in prompt
    assert "测试输入" in prompt

@pytest.mark.asyncio
async def test_agent_stream_response(agent, monkeypatch):
    # 修改异步生成器mock以接收参数
    async def mock_stream(prompt, provider):
        yield "测试"
        yield "响应"
    
    monkeypatch.setattr(agent, "_async_stream_wrapper", mock_stream)
    
    chunks = []
    async for chunk in agent.stream_response("测试输入"):
        chunks.append(chunk)
    
    assert len(chunks) == 2
    assert "".join(chunks) == "测试响应"