from fastapi import FastAPI
import logging
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import socketio
from pydantic import BaseModel
import asyncio
import time
from typing import AsyncGenerator
import uuid
from uuid import uuid4, UUID
import networkx as nx
from datetime import datetime

from core.message.socket_manager import SocketManager
from core.coordination.coordinator import Coordinator
from core.coordination.workflow.engine import  WorkflowEngine
from core.coordination.workflow.phases import  WorkflowPhase
from core.coordination.workflow.workflow_config import WORKFLOW_PHASES
from core.agents import ProductManager, Developer, UIDesigner
from core.agents.base_agent import RoleConfig
from core.message.schemas import AgentMessage
from services.llm_service import llm_service
from core.message.schemas import ErrorMessage

# 记忆模块
from core.memory import MemoryConfig, SessionMemory



logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:3000",
                                                                    "http://127.0.0.1:3000"])
app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 补充响应头暴露设置
)

app_asgi = socketio.ASGIApp(sio, app)

# 初始化核心组件
socket_manager = SocketManager(sio)

workflow_phases = []
for phase_config in WORKFLOW_PHASES:
    workflow_phases.append(WorkflowPhase(**phase_config))

workflow_engine = WorkflowEngine()
for phase in workflow_phases:
    workflow_engine.add_phase(phase)

# 初始化 SessionMemory 实例
session_memory = SessionMemory(
    config=MemoryConfig(max_history=10, ttl=3600),  # 显式传递配置
    socket_manager=socket_manager 
)

coordinator = Coordinator(
    socket_manager=socket_manager,
    workflow_engine=workflow_engine,
    session_memory=session_memory,  # 新增：传递 session_memory
    agent_registry={}
)


@socket_manager.sio.on('connect')
async def connect(sid, environ):
    try:
        # 从HTTP头获取自定义session_id（兼容Web端）
        custom_id = environ.get('HTTP_X_SESSION_ID') 
        # 检查是否已有session
        if custom_id:
            try:
                session_id = UUID(custom_id)
                # 检查session是否有效
                if await sio.get_session(sid):
                    logger.info(f"复用已有session: {session_id}")
                    await socket_manager.connect_client(sid, session_id)
                    # 立即通知前端会话已就绪
                    await sio.emit('session_ready', {
                        'session_id': str(session_id),
                        'status': 'resumed'
                    }, to=sid)
                    return
            except ValueError:
                pass

        session_id = uuid.uuid4()

        await socket_manager.connect_client(sid, session_id)
        await sio.save_session(sid, {
            'session_id': str(session_id),
            'created_at': datetime.now().isoformat()
        })
        logger.info(f"为新连接 {sid} 创建session: {session_id}")
        # 立即通知前端会话已创建
        await sio.emit('session_ready', {
            'session_id': str(session_id),
            'status': 'created'
        }, to=sid)
    except Exception as e:
        logger.error(f"连接处理错误: {str(e)}")
        await socket_manager.sio.disconnect(sid)


@sio.event
async def disconnect(sid):
    logger.warning(f"客户端断开连接: {sid}")
    try:
        await socket_manager.disconnect_client(sid)
    except KeyError as e:
        logger.warning(f"尝试断开不存在的会话: {e}")

# 添加Socket.io事件绑定


def create_agents(session_memory: SessionMemory, session_id: UUID):
    # 定义所有角色配置
    roles = {
        "product_manager": RoleConfig(
            name="产品经理",
            expertise="需求分析",
            personality="严谨细致"
        ),
        "developer": RoleConfig(
            name="后端工程师",
            expertise="软件开发",
            personality="逻辑性强"
        ),
        "ui_designer": RoleConfig(
            name="UI设计师",
            expertise="界面设计",
            personality="注重用户体验"
        )
    }

    agents = {}

    # 确保使用具体子类创建实例
    agent_classes = {
        "product_manager": ProductManager,
        "developer": Developer,
        "ui_designer": UIDesigner
    }

    for agent_name, agent_class in agent_classes.items():
        agents[agent_name] = agent_class(
            role=roles[agent_name],
            session_memory=session_memory,
            session_id=session_id
        )

    return agents

@sio.event
async def start_project(sid, data):
    
    print("---- 收到前端请求，后端开始运行 ----")
    print(f"接收到的参数类型: {type(data)}")  # 记录数据类型
    print(f"原始data内容: {data!r}")

    # 测试发送一条消息
    await sio.emit('message', {
        'sender': '系统',
        'content': '测试消息',
        'isChunk': False,
        'timestamp': datetime.now().isoformat()
    }, to=sid)
    try:
        session = await sio.get_session(sid)
        session_id = UUID(session['session_id'])
        logger.info(f"处理请求 session_id={session_id}")
        if not session or 'session_id' not in session:
            # 创建新会话
            session_id = uuid.uuid4()
            await sio.save_session(sid, {
                'session_id': str(session_id),
                'created_at': datetime.now().isoformat()
            })
            session = await sio.get_session(sid)
            logger.info(f"为新连接 {sid} 创建会话: {session_id}")
        else:
            # 从现有会话中获取 session_id
            session_id = UUID(session['session_id'])
            logger.info(f"为现有连接 {sid} 恢复会话: {session_id}")
        
        # 确保session_id是UUID类型
        if not isinstance(session_id, UUID):
            session_id = UUID(session_id)
        # session_id_str = session.get('session_id')

        # 添加会话ID验证
        # if not session_id_str:
        #     raise ValueError("会话ID不存在")

        # session_id = UUID(session_id_str)

        # 新增类型校验
        if not isinstance(data, dict):
            raise TypeError("期望接收到字典格式数据")

        # 新增参数校验
        if not (goal := data.get('goal')):
            error = ErrorMessage(
                error_code="MISSING_PARAMETER",
                error_msg="缺少必要参数'goal'"
            )
            await socket_manager.send_error(session_id, error)
            return

        # 初始化任务上下文
        initial_context = {
            "goal": goal,
            "phase_output": {},
            "metadata": {
                "source": "web",
                "priority": "high"
            }
        }

        # 创建 Agents 并注册到协调器
        agents = create_agents(session_memory, session_id)
        print("创建代理成功")
        coordinator.agent_registry = agents

        # 启动协调器处理任务
        await coordinator.handle_project(session_id, {"goal": data["goal"]})

    except ValueError as e:
        logger.error(f"会话ID错误: {str(e)}")
        error = ErrorMessage(
            error_code="INVALID_SESSION",
            error_msg=f"无效会话: {str(e)}"
        )
        # 直接使用当前sid发送错误，而不是UUID
        await sio.emit('error', {
            'error': 'SESSION_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, to=sid)
    except TypeError as e:
        # 类型错误特殊处理
        error = ErrorMessage(
            error_code="DATA_TYPE_ERROR",
            error_msg=str(e)
        )
        await socket_manager.send_error(session_id, error)
    except Exception as e:
        logger.error(f"处理请求错误: {str(e)}")
        # 直接发送错误到特定客户端
        await sio.emit('error', {
            'error': 'SESSION_ERROR',
            'message': str(e),
            'time_stamp': datetime.datetime.now().isoformat()
        }, to=sid)
        error = ErrorMessage(
            error_code="INTERNAL_ERROR",
            error_msg=f"处理请求时出错: {str(e)}"
        )
        await socket_manager.send_error(UUID(int=0), error)  # 使用默认UUID

@app.get("/test_stream/{sid}")
async def test_stream(sid: str):
    """测试流式接口"""
    from core.messaging.schemas import AgentMessage
    from core.agents.base_agent import RoleConfig
    test_role = RoleConfig(name="测试角色", expertise="测试", personality="测试")
    chunks = ["这是", "一个", "测试", "流式", "响应"]
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        message = AgentMessage(
            sender=test_role.name,
            content=chunk,
            is_chunk=True,
            is_last_chunk=is_last,
            role=test_role,
            timestamp=datetime.now()
        )
        await socket_manager.send_message(UUID(sid), message)
        await asyncio.sleep(0.5)

@app.get("/health")
def health_check():
    return {"status": "ok", "active_sessions": len(socket_manager.get_active_sessions())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=8000)
