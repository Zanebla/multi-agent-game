from pydantic import BaseModel
from typing import AsyncGenerator, List, Optional
from services.llm_service import stream_response
import time
import asyncio
from .roles import Role

class Agent:
    def __init__(self, role: Role):
        self.role = role
        self.memory: List[str] = []
        self.active_stream: Optional[AsyncGenerator] = None  

    def generate_prompt(self, input_text: str) -> str:
        memory_context = "\n".join(
            self.memory[-3:]) if self.memory else "无近期对话"
        return f"""
        【角色设定】
        您是一个专业的{self.role.name}，擅长{self.role.expertise}。
        性格特征：{self.role.personality}
        
        【对话背景】
        近期对话记录：
        {memory_context}
        
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
            self._update_memory(f"输入接收：{input_text[:50]}...")
            start_time = time.monotonic()
            chunk_count = 0

            async for chunk in self._async_stream_wrapper(prompt):
                # 流量控制：每5个chunk更新一次记忆
                if chunk_count % 5 == 0:
                    self._update_memory(f"生成进度: {len(chunk)}字符")

                # 实时返回内容
                yield chunk
                chunk_count += 1

                # 动态速度控制（快开头慢收尾）
                await self._adjust_speed(start_time, chunk_count)

            self._update_memory(f"回复完成: {chunk_count}个片段")

        except Exception as e:
            self._update_memory(f"生成失败：{str(e)}")
            yield f"\n⚠️ {self.role.name}响应异常: {str(e)}"
            raise

    def _update_memory(self, content: str):
        """优化记忆存储策略"""
        timestamp = time.strftime("%m/%d %H:%M")
        entry = f"[{timestamp}] {self.role.name} - {content}"

        if len(self.memory) >= 10:
            self.memory = self.memory[2:]  
        self.memory.append(entry)

    async def _async_stream_wrapper(self, prompt: str) -> AsyncGenerator[str, None]:
        """异步流式生成适配器"""
        buffer = []
        for chunk in stream_response(prompt):  # 假设stream_response是同步生成器
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
