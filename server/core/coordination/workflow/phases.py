from pydantic import BaseModel
from typing import Dict, Any

class WorkflowPhase(BaseModel):
    """工作流阶段定义"""
    
    name: str  # 阶段名称
    agent: str  # 负责此阶段的Agent
    input: str  # 输入模板
    output: str  # 输出上下文键名
    description: str = ""  # 阶段描述
    metadata: Dict[str, Any] = {}  # 附加元数据

    def format_input(self, context: Dict[str, Any]) -> str:
        """格式化输入模板"""
        return self.input.format(**context)