import pytest
import os
from dotenv import load_dotenv

# 加载测试环境变量
load_dotenv(dotenv_path=".env.test")

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("ARK_API_KEY", "test_key")