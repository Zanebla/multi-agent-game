import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional
import time
from enum import Enum

load_dotenv()
load_dotenv(override=True)

class LLMProvider(Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"

def get_client(provider: LLMProvider):
    if provider == LLMProvider.DEEPSEEK:
        return OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.getenv("ARK_API_KEY")
        )
    else:
        return OpenAI(
            base_url='https://xiaoai.plus/v1',
            api_key=os.getenv('OPENAI_API_KEY')
        )

def stream_response(
    prompt: str,
    model: str = None,
    max_tokens: int = 4000,
    provider: LLMProvider = LLMProvider.OPENAI
):
    try:
        client = get_client(provider)
        if model is None:
            model = "deepseek-v3-250324" if provider == LLMProvider.DEEPSEEK else "gpt-4o"
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
            temperature=0.7
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
    except Exception as e:
        yield f"\n[系统错误] 生成失败: {str(e)}"
