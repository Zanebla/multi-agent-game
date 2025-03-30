from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from .message_types import RoleConfig

class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"
    CODE = "code"
    ERROR = "error"

class BaseMessage(BaseModel):
    """消息基础模型"""
    session_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentMessage(BaseMessage):
    """Agent消息体"""
    sender: str
    content: str
    role: 'RoleConfig'
    msg_type: MessageType = MessageType.TEXT
    is_chunk: bool = Field(default=False) 
    is_last_chunk: bool = Field(default=False)
    metadata: Dict = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ErrorMessage(BaseMessage):
    """错误消息"""
    error_code: str
    error_msg: str