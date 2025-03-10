from fastapi import FastAPI, WebSocket
from core.websocket import manager

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理前端消息
            await manager.broadcast({
                "sender": "System",
                "content": "New message received",
                "type": "notification"
            })
    except websocket.exceptions.ConnectionClosedOK:
        manager.disconnect(websocket)


@app.get("/")
def read_root():
    return {"message": "Multi-Agent Backend Running!"}
