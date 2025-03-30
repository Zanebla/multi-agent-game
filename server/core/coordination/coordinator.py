from __future__ import annotations
from typing import Optional, Dict,  AsyncGenerator
import socketio
import asyncio
import logging
from uuid import UUID
import async_timeout
from datetime import datetime

from core.message.socket_manager import SocketManager
from core.coordination.workflow.engine import WorkflowEngine
from core.agents.base_agent import BaseAgent
from core.memory import SessionMemory
from core.message.schemas import ErrorMessage, AgentMessage

logger = logging.getLogger(__name__)

class Coordinator:
    """工作流协调器，负责管理多Agent协作流程
    
    主要功能：
    1. 按阶段执行工作流
    2. 处理Agent间通信
    3. 管理超时和错误处理
    4. 维护会话上下文
    """

    DEFAULT_TIMEOUT = 30  # 默认阶段超时时间(秒)
    PHASE_TIMEOUTS = {    # 各阶段自定义超时配置
        "需求分析": 60,
        "开发实现": 60,
        "页面美化": 60,
        "最终开发实现": 60
    }
    def __init__(
        self,
        socket_manager: SocketManager,
        workflow_engine: WorkflowEngine,
        session_memory: SessionMemory,
        agent_registry: Dict[str, BaseAgent] = None
    ):
    
        """初始化协调器
        Args:
            socket_manager: Socket通信管理器
            workflow_engine: 工作流引擎
            session_memory: 会话记忆管理器
            agent_registry: Agent注册表
        """
        self.socket_manager = socket_manager
        self.workflow_engine = workflow_engine
        self.session_memory = session_memory 
        self.agent_registry = agent_registry or {}

    async def handle_project(self, session_id: UUID, context: dict):
        """处理完整项目工作流
        
        Args:
            session_id: 会话唯一标识
            context: 初始上下文数据
        """
        context = initial_context.copy()
        current_phase = self.workflow_engine.get_first_phase()

        while current_phase:
            timeout = self.PHASE_TIMEOUTS.get(current_phase.name, self.DEFAULT_TIMEOUT)

            # 验证Agent是否存在
            if current_phase.agent not in self.agent_registry:
                error_msg = f"未注册的Agent: {current_phase.agent}"
                logger.error(error_msg)
                await self._handle_phase_error(
                    session_id,
                    current_phase,
                    error_msg
                )
                break

            try:
                final_response = await self._execute_phase(
                    session_id,
                    self.agent_registry[current_phase.agent],  # 获取Agent实例
                    current_phase.format_input(context),
                    current_phase,
                    timeout
                )
                
                if not final_response.strip():
                    raise ValueError("空响应内容")
                    
                # 更新上下文并进入下一阶段
                context[current_phase.output] = final_response
                current_phase = self.workflow_engine.get_next_phase(current_phase)
                
            except Exception as e:
                logger.error(f"阶段执行失败: {str(e)}", exc_info=True)
                await self._handle_phase_error(session_id, current_phase, str(e))
                break

        logger.info(f"会话 {session_id} 工作流完成")

    async def _execute_phase(
        self,
        session_id: UUID,
        agent: BaseAgent, 
        input_prompt: str,
        phase: WorkflowPhase,
        timeout: int 
    ):
        """执行单个工作流阶段
        Args:
            session_id: 会话ID
            agent: 当前执行的Agent实例
            input_prompt: 格式化后的输入提示
            phase: 工作流阶段
            timeout: 超时时间(秒)

        Returns:
            阶段最终响应内容
        """
        final_response = ""
        empty_count = 0
        
        async with async_timeout.timeout(timeout):
            async for message in agent.generate_response(input_prompt):
                # 消息格式标准化处理
                if not isinstance(message, AgentMessage):
                    message = AgentMessage(
                        sender=agent.role.name,
                        content=str(message),
                        is_chunk=True,
                        is_last_chunk=False,
                        role=agent.role,
                        timestamp=datetime.now(),
                        msg_type="text"
                    )
                elif isinstance(message.content, dict):  # 新增字典类型检查
                    # 处理字典中的UUID对象
                    message.content = str({k: str(v) if isinstance(v, UUID) else v for k, v in message.content.items()})
                elif not isinstance(message.content, str):
                    message.content = str(message.content)

                if not message.content.strip():
                    empty_count += 1
                    if empty_count > 3:
                        raise ValueError("连续收到空响应")
                    continue
            
            # 发送当前消息块
            await self.socket_manager.send_message(session_id, message)
            final_response += message.content
            await asyncio.sleep(0.05)  # 小延迟以确保消息发送
        
        # 发送阶段完成标记
        await self._send_completion_message(session_id, agent)
        
        # 记录到会话记忆
        self.session_memory.add_response(agent.role.name, final_response)
        return final_response

    async def _send_completion_message(self, session_id: UUID, agent: BaseAgent):
            """发送阶段完成标记消息"""
            completion_msg = AgentMessage(
                sender=agent.role.name,
                content="",
                is_chunk=True,
                is_last_chunk=True,
                role=agent.role,
                timestamp=datetime.now(),
                msg_type="text"
            )
            await self.socket_manager.send_message(session_id, completion_msg)
            
    async def _handle_phase_error(
        self,
        session_id: UUID,
        phase,
        error_msg: str
    ):
        """统一处理阶段错误"""
        await self.socket_manager.send_error(
            session_id,
            ErrorMessage("PHASE_ERROR", error_msg)
        )
        await self.socket_manager.send_status(
            session_id,
            StatusMessage(
                phase=phase.name,
                status="failed",
                content=error_msg,
                level="error"
            )
        )