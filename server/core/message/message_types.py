from pydantic import BaseModel, Field

class RoleConfig(BaseModel):
    """消息系统中使用的角色配置模型（完整版）"""
    name: str = Field(..., min_length=2, description="角色名称")
    expertise: str = Field("通用领域", description="专业领域")
    personality: str = Field("中立", description="性格特征")