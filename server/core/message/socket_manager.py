import socketio
from typing import Dict, Optional, List, Union
from uuid import UUID
import json
import logging
from datetime import datetime
from .schemas import (
    AgentMessage,
    ErrorMessage,
)

logger = logging.getLogger(__name__)


class SocketManager:
    """Socket.IO 通信管理器"""

    def __init__(self, sio: socketio.AsyncServer):
        self.sio = socketio.AsyncServer(
            async_mode='asgi',
            cors_allowed_origins="*",  # 开发环境可以暂时允许所有来源
            logger=True,  # 启用详细日志
            engineio_logger=True
        )
        self.sessions = {}
        self.app = socketio.ASGIApp(self.sio)

    def _serialize(self, data) -> str:
        """序列化数据（处理UUID和datetime）"""
        return json.dumps(data, default=str)

    async def connect_client(self, sid: str, session_id: UUID):
        """处理客户端连接"""
        try:
            # 先检查socket是否存在
            if not self.sio.manager.is_connected(sid):
                raise ConnectionError(f"Socket {sid} 未连接")
                
            # 保存会话信息
            self.sessions[sid] = str(session_id)
            self.sio.enter_room(sid, str(session_id))
            
            # 保存到socket.io会话
            await self.sio.save_session(sid, {
                'session_id': str(session_id),
                'connected_at': datetime.now().isoformat()
            })
            
            logger.info(f"客户端 {sid} 连接到会话 {session_id}")
        except Exception as e:
            logger.error(f"连接处理失败: {str(e)}")
            raise

    async def disconnect_client(self, sid: str):
        """处理客户端断开"""
        session = await self.sio.get_session(sid)
        if session_id := session.get("session_id"):
            self.sessions[session_id].last_active = datetime.now()
            logger.info(f"客户端 {sid} 从会话 {session_id} 断开")

    async def send_message(self, session_id: UUID, message: AgentMessage) -> None: 
        """统一消息发送入口"""
        if not isinstance(message, AgentMessage):
            raise TypeError("message参数必须是AgentMessage实例")
        payload = {
        'sender': message.sender,
        'content': message.content,
        'isChunk': message.is_chunk,
        'isLastChunk': message.is_last_chunk,
        'role': message.role.name,  # 英文角色标识
        'timestamp': message.timestamp.isoformat(),
        'status': 'streaming' if not message.is_last_chunk else 'complete'
        }
        await self.sio.emit('message', payload, room=str(session_id))

    async def send_status(self, session_id: UUID, status: Dict):
        """发送状态更新"""
        self._validate_session(session_id)
        await self._emit_to_room(
            "system_status",
            status,
            room=str(session_id)
        )

    async def send_error(self, session_id: Union[UUID, str], error: ErrorMessage):
        """发送错误消息"""
        try:
            # 允许传入字符串或UUID
            session_id_str = str(session_id) if isinstance(session_id, UUID) else session_id
            await self.sio.emit('error', {
            'error_code': error.error_code,
            'error_msg': error.error_msg,
            'timestamp': datetime.now().isoformat()
            }, room=session_id_str)
        except Exception as e:
            logger.error(f"发送错误消息失败: {str(e)}")

    async def _emit_to_room(self, event: str, data: dict, room: str):
        """通用房间消息发送"""
        try:
            await self.sio.emit(
                event,
                self._serialize(data),
                room=room
            )
            logger.debug(f"成功发送 {event} 到房间 {room}")
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}", exc_info=True)
            raise

    def _update_session_activity(self, session_id: UUID):
        """更新会话活跃时间"""
        if session := self.sessions.get(session_id):
            session.last_active = datetime.now()

    def get_active_sessions(self) -> List[Dict]:
        """获取活跃会话列表"""
        return [{
            'session_id': s.session_id,
            'last_active': s.last_active
        } for s in self.sessions.values()
        if (datetime.now() - s.last_active).total_seconds() < 300]