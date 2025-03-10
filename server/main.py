from fastapi import FastAPI, WebSocket
from core.websocket import manager
from core.agents import Agent, Role
from core.coordinator import Coordinator
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware
import socketio
from pydantic import BaseModel

# 创建 Socket.IO 实例
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app_asgi = socketio.ASGIApp(sio, app)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 补充响应头暴露设置
)

coordinator = Coordinator()

# 初始化角色
roles = {
    "product_manager": Role(
        name="产品经理",
        expertise="需求分析",
        personality="严谨细致"
    ),
    "developer": Role(
        name="后端工程师",
        expertise="Python开发",
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


@sio.event
async def disconnect(sid):
    print(f"客户端 {sid} 已断开")

# 添加请求体模型


class ProjectGoal(BaseModel):
    goal: str  # 严格匹配前端参数名


@app.post("/start-project")
async def start_project(goal_data: ProjectGoal):
    """启动项目流程"""
    goal = goal_data.goal  # 正确获取参数
    # 1. 产品经理生成需求文档
    pm_prompt = f"用户需求：{goal}\n请生成详细的需求文档"
    pm_response = agents["product_manager"].generate_response(pm_prompt)

    # 2. 触发开发者任务
    dev_prompt = f"根据以下需求编写代码：\n{pm_response}"
    dev_response = agents["developer"].generate_response(dev_prompt)

    return {
        "pm": pm_response,
        "dev": dev_response
    }


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)

        # 处理消息逻辑
        response = {
            "sender": "系统",
            "content": f"已收到：{message['content']}"
        }
        await websocket.send_text(json.dumps(response))


@app.get("/")
def read_root():
    return {"message": "Multi-Agent Backend Running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=8000)
