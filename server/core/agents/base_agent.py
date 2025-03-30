from pydantic import BaseModel, Field
from typing import AsyncGenerator, Optional, List, Dict
import asyncio
import logging
from uuid import UUID
from datetime import datetime

from services.llm_service import llm_service
from core.memory import AgentMemory, SessionMemory
from core.message.schemas import AgentMessage
from core.agents.role_config import RoleConfig

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Agent基类，提供多Agent系统中的通用功能实现
    主要职责：
    1. 管理Agent生命周期
    2. 处理与LLM的交互
    3. 管理消息流式生成和发送
    4. 维护会话记忆和上下文
    """

    def __init__(
        self,
        role: RoleConfig,
        session_memory: SessionMemory,
        session_id: UUID,
    ):
        self.role = role
        self.session_memory = session_memory
        self.session_id = session_id
        self.memory = self.session_memory.get_agent_memory(
            self.role.name, self.session_id
        )

    async def _send_response(self, content: str, is_last: bool = False):
        """统一发送响应消息到前端"""
        message = AgentMessage(
            sender=self.role.name,
            content=content,
            is_chunk=True,
            is_last_chunk=is_last,
            role=self.role,
            timestamp=datetime.now(),
            msg_type="text"
        )
        
        # 通过session_memory获取socket_manager
        socket_manager = self.session_memory.socket_manager
        if socket_manager:
            await socket_manager.send_message(self.session_id, message)
        else:
            logger.error("SocketManager不可用，无法发送消息")

    def get_session_memory(self) -> Dict[str, List[str]]:
        """获取当前会话所有代理的历史记录"""
        return self.session_memory.get_session_memory()

    def build_system_prompt(self, user_input: str) -> str:
        """构建系统级提示模板"""
        memory_context = self.memory.get_context()
        return f"""
        # 角色设定
        你是一位专业的{self.role.name}，擅长{self.role.expertise}
        性格特征：{self.role.personality}

        # 任务要求
        1. 使用{self.role.expertise}领域的专业术语
        2. 保持{self.role.personality}的表述风格
        3. 结构化输出（代码/分点说明）
        {self._get_role_specific_requirement()}

        # 对话上下文
        {memory_context}

        # 用户输入
        {user_input}
        """

    def _get_role_specific_requirement(self) -> str:
        """角色特定要求（子类可覆盖）"""
        if "developer" in self.role.expertise.lower():
            return "必须输出可运行代码（包含完整实现）"
        return ""

    async def stream_generate(
        self,
        user_input: str,
        session_id: Optional[UUID] = None
    ) -> AsyncGenerator[str, None]:
        print(f"开始流式生成响应...")
        """流式生成响应（带全生命周期管理）"""
        try:
            # 记录输入事件
            self._log_activity(session_id, "收到输入", user_input)

            response_buffer = []
            async for chunk in self._stream_with_control(user_input, session_id):
                if not chunk.content.strip():
                    continue
                response_buffer.append(chunk.content)
                yield chunk

            if not response_buffer:
                error_msg = "Agent未生成有效响应"
                self._log_error(session_id, error_msg)
                yield AgentMessage(
                    sender=self.role.name,
                    content=error_msg,
                    msg_type="error"
                )
            # 记录响应完成事件
            self._log_activity(session_id, "响应完成", "响应完成")

        except Exception as e:
            self._log_error(session_id, e)
            yield f"⚠️ {self.role.name}响应异常: {str(e)}"
            raise

    async def _stream_with_control(
        self,
        user_input: str,
        session_id: Optional[UUID]
    ) -> AsyncGenerator[AgentMessage, None]:
        """带流量控制的流式生成"""
        prompt = self.build_system_prompt(user_input)
        buffer = []
        retry_count = 0
        MAX_RETRY = 3

        async for raw_chunk in self._call_llm(prompt):
            if raw_chunk.strip():  # 过滤空内容
                buffer.append(raw_chunk)
                retry_count = 0
            else:
                retry_count += 1
                if retry_count >= MAX_RETRY:
                    logger.error("连续空分块超过阈值，强制终止")
                    break

            if self._is_sentence_end(raw_chunk):
                content = self._flush_buffer(buffer)
                message = AgentMessage(
                    sender=self.role.name,
                    content=content,
                    msg_type="text",
                    receiver="user",
                    role=self.role,
                    timestamp=datetime.now(),
                    is_chunk=True,
                    is_last_chunk=False
                )
                yield message  # 返回对象而非原始字符串
                await self._dynamic_delay()

        if buffer:
            content = self._flush_buffer(buffer)
            message = AgentMessage(
                sender=self.role.name,
                content=content,
                role=self.role,
                timestamp=datetime.now(),
                msg_type="text",
            )
            yield message

    async def _call_llm(self, prompt: str) -> AsyncGenerator[str, None]:
        """调用LLM服务"""
        try:
            async for chunk in llm_service.stream_response(prompt):
                yield chunk
        except ConnectionError as e:
            logger.error(f"LLM连接失败: {str(e)}")
            yield f"\n🚨 服务暂时不可用，请稍后重试"

    def _is_sentence_end(self, text: str) -> bool:
        """判断自然断句点"""
        delimiters = {'。', '!', '?', '\n', '；', '：'}
        return any(c in text for c in delimiters)

    def _flush_buffer(self, buffer: List[str]) -> str:
        """清空缓冲区并返回内容"""
        content = "".join(buffer)
        buffer.clear()
        return content

    async def _dynamic_delay(self):
        """动态响应延迟"""
        await asyncio.sleep(0.08)  # 默认80ms间隔

    def _log_activity(self, session_id: Optional[UUID], action: str, content: str):

        log_entry = f"[{self.role.name}] {action}: {content[:50]}..."
        if session_id:
            self.memory.add_context(session_id, self.role.name, log_entry)
        logger.info(log_entry)

    def _log_error(self, session_id: Optional[str], error: Exception):
        error_msg = f"[{self.role.name}] 处理失败: {str(error)}"
        if session_id:
            self.memory.add_context(session_id, self.role.name, error_msg)
        logger.error(error_msg)
