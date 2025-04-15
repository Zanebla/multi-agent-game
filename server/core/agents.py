from pydantic import BaseModel
from typing import AsyncGenerator, Optional
from services.llm_service import stream_response, LLMProvider
import time
import asyncio
from .roles import Role

class Agent:
    def __init__(self, role: Role):
        self.role = role
        self.active_stream: Optional[AsyncGenerator] = None  

    def generate_prompt(self, input_text: str) -> str:
        return f"""
        【角色设定】
        您是一个专业的{self.role.name}，擅长{self.role.expertise}。
        性格特征：{self.role.personality}
        
        【当前任务】
        请根据以下输入生成符合角色的回复：
        {input_text}

        【回复要求】
        1. 使用{self.role.expertise}领域的专业术语
        2. 保持{self.role.personality}的表达风格
        3. 结构化输出（分点说明）
        """

    async def stream_response(self, input_text: str) -> AsyncGenerator[str, None]:
        """异步流式生成响应"""
        try:
            prompt = self.generate_prompt(input_text)
            start_time = time.monotonic()
            chunk_count = 0

            async for chunk in self._async_stream_wrapper(prompt, self.provider):
                yield chunk
                chunk_count += 1

                await self._adjust_speed(start_time, chunk_count)

        except Exception as e:
            yield f"\n⚠️ {self.role.name}响应异常: {str(e)}"
            raise

    async def _async_stream_wrapper(self, prompt: str, provider: LLMProvider) -> AsyncGenerator[str, None]:
        """异步流式生成适配器"""
        buffer = []
        for chunk in stream_response(prompt, provider=provider):  # 假设stream_response是同步生成器
            buffer.append(chunk)

            if any(c in chunk for c in ('。', '!', '?', '\n')):
                yield ''.join(buffer)
                buffer.clear()
                await asyncio.sleep(0)  # 关键：让出事件循环

        if buffer:  # 处理剩余内容
            yield ''.join(buffer)

    async def _adjust_speed(self, start_time: float, count: int):
        """动态调整生成速度"""
        elapsed = time.monotonic() - start_time

        # 前3秒快速推送（0-3秒）
        if elapsed < 3:
            delay = max(0.03, 0.1 - count*0.002)
        # 中期稳定速度（3-10秒）
        elif elapsed < 10:
            delay = 0.08
        # 后期放缓（10秒后）
        else:
            delay = 0.12

        await asyncio.sleep(delay)
