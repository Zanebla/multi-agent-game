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
from core.agents import Agent, Role
from core.coordinator import Coordinator
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

@sio.event
async def connect(sid, environ):
    await ws_service.handle_connect(sid, environ)

@sio.event 
async def disconnect(sid):
    await ws_service.handle_disconnect(sid)

@sio.event
async def start_project(sid, data):
    await ws_service.handle_start_project(sid, data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=8000)
