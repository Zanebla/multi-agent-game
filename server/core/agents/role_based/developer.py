from typing import AsyncGenerator
from ..base_agent import BaseAgent, RoleConfig
from core.memory import SessionMemory
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


class Developer(BaseAgent):
    """开发者角色实现"""

    def __init__(self, role: RoleConfig, session_memory: SessionMemory, session_id: UUID):
        super().__init__(role, session_memory, session_id)

    def build_system_prompt(self, user_input: str) -> str:
        base_prompt = super().build_system_prompt(user_input)
        return f"""
        {base_prompt}
        5. 包含必要的错误处理
        6. 添加代码注释（使用中文）
        7. 必须输出完整代码
        """

    async def generate_response(self, prd_document: str) -> AsyncGenerator[str, None]:
        memory_content = self.session_memory.get_text_history()

        """输出代码"""

        prompt = f"""
        根据之前的讨论内容：
        {memory_content}
        并详细阅读以下PRD：
        {prd_document}
        输出代码

        要求：
        1. 只输出满足要求的代码，不要输出其他内容
        """
        async for chunk in self.stream_generate(prompt):
            yield chunk
