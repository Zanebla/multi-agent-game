from typing import AsyncGenerator
from ..base_agent import BaseAgent, RoleConfig
from core.memory import AgentMemory, SessionMemory, MemoryConfig
from uuid import UUID


class ProductManager(BaseAgent):
    """产品经理角色实现"""

    def __init__(self, role: RoleConfig, session_memory: SessionMemory, session_id: UUID):
        super().__init__(
            role=role,
            session_memory=session_memory,
            session_id=session_id,
        )

    async def generate_response(self, input_prompt: str) -> AsyncGenerator[str, None]:
        """生成 PRD 文档"""
        async for chunk in self.stream_generate(input_prompt):
            yield chunk

    async def generate_prd(self, user_goal: str) -> AsyncGenerator[str, None]:
        memory_content = self.session_memory.get_text_history()
        print(f"开始生成 PRD 文档 (用户目标： {user_goal})")
        """生成需求文档专用方法"""
        enhanced_prompt = f"""
        ## 历史对话记录
        {memory_content}
        ## 原始需求
        {user_goal}

        ## 补充要求
        1. 明确功能优先级（MoSCoW法）
        2. 定义验收标准
        """
        async for chunk in self.stream_generate(enhanced_prompt):
            print(f"生成 chunk: {chunk}")
            yield chunk

    def build_system_prompt(self, user_input: str) -> str:
        base_prompt = super().build_system_prompt(user_input)
        return base_prompt + "\n4. 使用流程图或时序图说明关键流程"
