from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, AsyncGenerator, Callable
import socketio
import asyncio
import logging
# internal modules
from .schemas import MessageSchema, TaskNodeSchema

logger = logging.getLogger(__name__)


class Coordinator:
    """协调中心核心类，负责：
    1. 消息路由与分发
    2. 任务状态跟踪
    3. 错误恢复机制
    4. 工作流协调
    """

    def __init__(self, message_handler: Callable):
        self.message_queue: List[MessageSchema] = []
        self.message_handler = message_handler

    async def post_message(self, message: Message):
        """异步处理消息"""
        self.message_queue.append(message)
        self.conversation_log.append(message)

        # 立即触发分发
        await self.distribute_messages()

    async def distribute_messages(self):
        """异步消息分发"""
        while self.message_queue:
            msg = self.message_queue.pop(0)
            if msg.receiver:
                await self._send_private(msg)
            else:
                await self._broadcast(msg)

    async def _send_private(self, msg: Message):
        """发送私密消息"""
        if msg.sid:
            await self.sio.emit('agent_message', {
                'sender': msg.sender,
                'content': msg.content,
                'receiver': msg.receiver
            }, room=msg.sid)

    async def _broadcast(self, msg: Message):
        """广播给所有订阅者"""
        await self.sio.emit('agent_message', {
            'sender': msg.sender,
            'content': msg.content
        })
