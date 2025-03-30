from pydantic import BaseModel

class MemoryConfig(BaseModel):
    """记忆系统配置"""
    max_history: int = 10  # 最大历史条目数
    ttl: int = 3600       # 条目有效期(秒)