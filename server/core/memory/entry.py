from pydantic import BaseModel, Field

class MemoryEntry(BaseModel):
    """记忆条目数据模型"""
    timestamp: float
    role: str
    content: str
    metadata: dict = Field(default_factory=dict)