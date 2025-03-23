from fastapi import FastAPI, WebSocket
from core.websocket import manager
from core.agents import Agent, Role
from core.coordinator import Coordinator
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware
import socketio
from pydantic import BaseModel
import asyncio
from services.llm_service import stream_response
import time
from typing import AsyncGenerator

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:3000",
                                                                    "http://127.0.0.1:3000"])
app = FastAPI()
app_asgi = socketio.ASGIApp(sio, app)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 补充响应头暴露设置
)

coordinator = Coordinator(sio)


class ProjectGoal(BaseModel):
    goal: str  # 严格匹配前端参数名


# 初始化角色
roles = {
    "product_manager": Role(
        name="产品经理",
        expertise="需求分析",
        personality="严谨细致"
    ),
    "developer": Role(
        name="后端工程师",
        expertise="软件开发",
        personality="逻辑性强"
    )
}

agents = {
    role: Agent(roles[role])
    for role in roles
}

# Socket.IO 事件处理


@sio.event
async def connect(sid, environ):
    print(f"客户端 {sid} 已连接")
    await sio.save_session(sid, {'status': 'connected'})


@sio.event
async def disconnect(sid):
    print(f"客户端 {sid} 已断开")

# 添加Socket.io事件绑定


async def stream_agent_response(
    agent_name: str,
    prompt: str,
    sid: str,
    sender_name: str,
    role: str
) -> str:
    """
    流式生成Agent响应并实时推送消息的核心函数

    参数:
    - agent_name: 要使用的Agent名称 (e.g. "product_manager")
    - prompt: 输入提示
    - sid: 客户端会话ID
    - sender_name: 消息发送者显示名称
    - role: 角色标识 (用于前端样式)

    返回完整响应内容（非生成器）
    """
    try:
        agent = agents[agent_name]
        full_content = ""
        last_chunk_time = time.time()

        # 发送开始状态
        await sio.emit('status', {
            "sender": sender_name,
            "status": "started",
            "timestamp": int(time.time() * 1000)
        }, room=sid)

        # 异步遍历流式响应
        async for chunk in agent.stream_response(prompt):
            # 更新完整内容
            full_content += chunk

            # 实时推送消息块
            await sio.emit('message', {
                "sender": sender_name,
                "content": chunk,
                "role": role,
                "isChunk": True,
                "isLastChunk": False,
                "timestamp": int(time.time() * 1000)
            }, room=sid)

            # 流量控制：如果生成速度过快，主动延迟
            current_time = time.time()
            if current_time - last_chunk_time < 0.05:  # 50ms间隔
                await asyncio.sleep(0.05 - (current_time - last_chunk_time))
            last_chunk_time = current_time

        # 发送完整消息，标记为最后一个分块
        # await sio.emit('message', {
        #     "sender": sender_name,
        #     "content": full_content,
        #     "role": role,
        #     "isChunk": False,
        #     "isLastChunk": True,
        #     "status": "complete",
        #     "timestamp": int(time.time() * 1000)
        # }, room=sid)

        # 发送完成状态（不发送完整消息）
        await sio.emit('status', {
            "sender": sender_name,
            "status": "completed",
            "role": role,
            "timestamp": int(time.time() * 1000)
        }, room=sid)
        return full_content

    except Exception as e:
        error_msg = f"{sender_name}处理失败: {str(e)}"
        # 发送错误消息
        await sio.emit('error', {
            "sender": "系统",
            "content": error_msg,
            "timestamp": int(time.time() * 1000)
        }, room=sid)

        # 重新抛出异常以便上层处理
        raise RuntimeError(error_msg) from e


@sio.event
async def start_project(sid, data):
    """处理前端发起的项目启动请求"""
    try:
        goal = data.get('goal')
        if not goal:
            await sio.emit('error', {'message': '缺少需求参数'}, room=sid)
            return

        # 1. 处理产品经理的响应（调用核心函数）
        pm_prompt = f"用户需求：{goal}\n请生成详细的需求文档"
        pm_response = await stream_agent_response(
            "product_manager",
            pm_prompt,
            sid,
            "产品经理",
            "pm"
        )

        # 2. 处理开发者的响应（调用核心函数）
        dev_prompt = f"根据以下需求编写代码：\n{pm_response}"
        dev_response = await stream_agent_response(
            "developer",
            dev_prompt,
            sid,
            "后端工程师",
            "developer"
        )

       # 可选：发送最终结果汇总（根据需求调整）
        await sio.emit('message', {
            "sender": "系统",
            "content": "项目处理完成",
            "role": "system",
            "timestamp": int(time.time() * 1000)
        }, room=sid)

    except Exception as e:
        await sio.emit('error', {'message': str(e)}, room=sid)


# @app.get("/")
# def read_root():
#     return {"message": "Multi-Agent Backend Running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=8000)
