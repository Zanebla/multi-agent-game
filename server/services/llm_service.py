import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional
import time

load_dotenv()
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    api_key=api_key
)


def stream_response(
    prompt: str,
    model: str = "gpt-4o",
    max_tokens: int = 2000
    # ) -> Optional[str]:
):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
            temperature=0.7
        )
        # return response.choices[0].message.content
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"\n[系统错误] 生成失败: {str(e)}"
