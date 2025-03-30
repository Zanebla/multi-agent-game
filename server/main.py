# external modules
from fastapi import FastAPI, WebSocket
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware
import socketio
from pydantic import BaseModel
import asyncio
import time
from typing import AsyncGenerator
# internal modules
# from core.websocket import manager
from core.agents import Agent, Role
from core.coordinator import Coordinator
# from services.llm_service import stream_response
from services.websocket_service import WebSocketService
from core.roles import ROLES as roles
from core.schemas import ProjectGoal

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=["http://localhost:3000",
                                                                    "http://127.0.0.1:3000"])
app = FastAPI()
app_asgi = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  
)

coordinator = Coordinator(sio)

agents = {
    role: Agent(roles[role])
    for role in roles
}


ws_service = WebSocketService(sio, agents)

# @sio.event
# async def connect(sid, environ):
#     print(f"客户端 {sid} 已连接")
#     await sio.save_session(sid, {'status': 'connected'})


# @sio.event
# async def disconnect(sid):
#     print(f"客户端 {sid} 已断开")


# async def stream_agent_response(
#     agent_name: str,
#     prompt: str,
#     sid: str,
#     sender_name: str,
#     role: str
# ) -> str:
    # try:
    #     agent = agents[agent_name]
    #     full_content = ""
    #     last_chunk_time = time.time()

    #     await sio.emit('status', {
    #         "sender": sender_name,
    #         "status": "started",
    #         "timestamp": int(time.time() * 1000)
    #     }, room=sid)

    #     async for chunk in agent.stream_response(prompt):
    #         full_content += chunk

    #         await sio.emit('message', {
    #             "sender": sender_name,
    #             "content": chunk,
    #             "role": role,
    #             "isChunk": True,
    #             "isLastChunk": False,
    #             "timestamp": int(time.time() * 1000)
    #         }, room=sid)

    #         current_time = time.time()
    #         if current_time - last_chunk_time < 0.05: 
    #             await asyncio.sleep(0.05 - (current_time - last_chunk_time))
    #         last_chunk_time = current_time

    #     await sio.emit('status', {
    #         "sender": sender_name,
    #         "status": "completed",
    #         "role": role,
    #         "timestamp": int(time.time() * 1000)
    #     }, room=sid)
    #     return full_content

    # except Exception as e:
    #     error_msg = f"{sender_name}处理失败: {str(e)}"
    #     # 发送错误消息
    #     await sio.emit('error', {
    #         "sender": "系统",
    #         "content": error_msg,
    #         "timestamp": int(time.time() * 1000)
    #     }, room=sid)

    #     # 重新抛出异常以便上层处理
    #     raise RuntimeError(error_msg) from e

@sio.event
async def connect(sid, environ):
    await ws_service.handle_connect(sid, environ)

@sio.event 
async def disconnect(sid):
    await ws_service.handle_disconnect(sid)

@sio.event
async def start_project(sid, data):
    """处理前端发起的项目启动请求"""
    # try:
    #     goal = data.get('goal')
    #     if not goal:
    #         await sio.emit('error', {'message': '缺少需求参数'}, room=sid)
    #         return

    #     # 1. 处理产品经理的响应（调用核心函数）
    #     pm_prompt = f"用户需求：{goal}\n请生成详细的需求文档"
    #     pm_response = await stream_agent_response(
    #         "product_manager",
    #         pm_prompt,
    #         sid,
    #         "产品经理",
    #         "pm"
    #     )

    #     # 2. 处理开发者的响应（调用核心函数）
    #     dev_prompt = f"根据以下需求编写代码：\n{pm_response}"
    #     dev_response = await stream_agent_response(
    #         "developer",
    #         dev_prompt,
    #         sid,
    #         "后端工程师",
    #         "developer"
    #     )

    #    # 可选：发送最终结果汇总（根据需求调整）
    #     await sio.emit('message', {
    #         "sender": "系统",
    #         "content": "项目处理完成",
    #         "role": "system",
    #         "timestamp": int(time.time() * 1000)
    #     }, room=sid)

    # except Exception as e:
    #     await sio.emit('error', {'message': str(e)}, room=sid)

    await ws_service.handle_start_project(sid, data)

# @app.get("/")
# def read_root():
#     return {"message": "Multi-Agent Backend Running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=8000)
