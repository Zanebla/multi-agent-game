import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    base_url='https://xiaoai.plus/v1',
    api_key=api_key
)


def generate_response(
    prompt: str,
    model: str = "gpt-4o",
    max_tokens: int = 500
) -> Optional[str]:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM API错误: {str(e)}")
        return None
