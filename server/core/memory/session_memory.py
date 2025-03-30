from uuid import UUID
from typing import Dict, List
from .config import MemoryConfig
from .agent_memory import AgentMemory
from core.message.schemas import AgentMessage

class SessionMemory:
    """存储会话级所有代理的历史响应"""

    def __init__(self, config: MemoryConfig = None, socket_manager=None):
        self.config = config
        self.socket_manager = socket_manager
        self.agent_memories = {}
        self.history = []

    def get_agent_memory(self, agent_name: str, session_id: UUID) -> AgentMemory:
        """获取指定代理和会话ID的记忆实例"""
        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = {}
        if session_id not in self.agent_memories[agent_name]:
            self.agent_memories[agent_name][session_id] = AgentMemory(
                config=self.config)
        return self.agent_memories[agent_name][session_id]

    def add_response(self, agent_name: str, response: str):
        """记录代理的响应到历史中"""
        if not isinstance(response, str):
            raise ValueError("响应内容必须是字符串")

        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = []
        elif not isinstance(self.agent_memories[agent_name], list):
            self.agent_memories[agent_name] = [self.agent_memories[agent_name]]
        self.agent_memories[agent_name].append(response)

    def get_session_memory(self) -> Dict[str, List[str]]:
        """获取当前会话所有代理的历史记录"""
        return self.agent_memories

    def get_all(self) -> List[AgentMessage]:
        """获取所有消息作为AgentMessage对象列表"""
        messages = []
        for msg in self.history:
            messages.append(AgentMessage(
                sender=msg.sender,
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp,
                msg_type=msg.msg_type
            ))
        return messages

    def get_text_history(self) -> str:
        """返回纯文本历史记录"""
        return "\n".join([msg.content for msg in self.get_all()])

    def get_json_history(self) -> List[dict]:
        return [msg.dict() for msg in self.get_all()]