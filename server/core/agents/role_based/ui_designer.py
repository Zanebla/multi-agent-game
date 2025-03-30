from typing import AsyncGenerator
from ..base_agent import BaseAgent, RoleConfig
from core.memory import SessionMemory
from uuid import UUID


class UIDesigner(BaseAgent):
    """UI设计师角色实现"""

    def __init__(
            self,
            role: RoleConfig,
            session_memory: SessionMemory,
            session_id: UUID
    ):
        super().__init__(
            role=role,
            session_memory=session_memory,
            session_id=session_id
        )

    def build_system_prompt(self, user_input: str) -> str:
        base_prompt = super().build_system_prompt(user_input)
        return f"""
        {base_prompt}
        4. 使用具体色号（如#FFFFFF）
        5. 说明动效参数（时长/缓动函数）
        6. 包含响应式布局方案
        """

    async def generate_response(self, spec: str) -> AsyncGenerator[str, None]:
        """生成设计规范专用方法"""
        prompt = f"""
        根据以下需求创建设计规范：
        {spec}

        包含：
        1. 字体层级系统
        2. 间距规则（8pt网格）
        3. 交互状态设计
        """
        async for chunk in self.stream_generate(prompt):
            yield chunk
