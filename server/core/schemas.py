# 新建 core/schemas.py 存放数据模型
from pydantic import BaseModel
from datetime import datetime


class RoleSchema(BaseModel):
    name: str
    expertise: str
    personality: str


class MessageSchema(BaseModel):
    sender: str
    content: str
    receiver: str | None = None
    timestamp: datetime = datetime.now()
    sid: str | None = None


class TaskNodeSchema(BaseModel):
    id: str
    description: str
    parent_id: str | None = None
    assigned_to: str
    status: str = "pending"
