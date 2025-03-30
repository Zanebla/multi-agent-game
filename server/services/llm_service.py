import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional
import time
from typing import AsyncGenerator
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # 检查日志系统配置
        if not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            logger.info("日志系统已初始化")  # 添加调试日志
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY环境变量未设置")  # 将错误信息也记录日志
            raise ValueError("OPENAI_API_KEY环境变量未设置")
        logger.info("正在初始化LLM客户端")  # 添加客户端初始化日志
        self.client = AsyncOpenAI(
            base_url='https://xiaoai.plus/v1',  # 修正基础URL
            api_key=api_key
        )
        logger.info("LLM客户端初始化完成")  # 添加完成日志
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def stream_response(
        self,
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """增强版的流式响应生成"""
        try:
            logger.info("正在调用LLM API...")
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True,
                temperature=temperature
            )
            logger.info("API请求成功，开始流式处理")  # 新增日志

            has_content = False  # 用于跟踪是否已经接收到内容
            async for chunk in response:
                if content := getattr(chunk.choices[0].delta, 'content', ''):
                    has_content = True
                    yield content
                
            if not has_content:
                yield "[错误] LLM未返回有效内容"

        except Exception as e:
            logger.error(f"LLM API调用失败: {str(e)}")
            yield f"\n[系统错误] 生成失败: {str(e)}"


# 单例实例
llm_service = LLMService()
