import socketio
import asyncio
import time
from typing import AsyncGenerator

class WebSocketService:
    def __init__(self, sio, agents):
        self.sio = sio
        self.agents = agents

    async def stream_agent_response(
        self,
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
          agent = self.agents[agent_name]
          full_content = ""
          last_chunk_time = time.time()

          await self.sio.emit('status', {
              "sender": sender_name,
              "status": "started",
              "timestamp": int(time.time() * 1000)
          }, room=sid)

          async for chunk in agent.stream_response(prompt):
              full_content += chunk

              await self.sio.emit('message', {
                  "sender": sender_name,
                  "content": chunk,
                  "role": role,
                  "isChunk": True,
                  "isLastChunk": False,
                  "timestamp": int(time.time() * 1000)
              }, room=sid)

              current_time = time.time()
              if current_time - last_chunk_time < 0.05: 
                  await asyncio.sleep(0.05 - (current_time - last_chunk_time))
              last_chunk_time = current_time

          await self.sio.emit('status', {
              "sender": sender_name,
              "status": "completed",
              "role": role,
              "timestamp": int(time.time() * 1000)
          }, room=sid)
          return full_content

      except Exception as e:
          error_msg = f"{sender_name}处理失败: {str(e)}"
          # 发送错误消息
          await self.sio.emit('error', {
              "sender": "系统",
              "content": error_msg,
              "timestamp": int(time.time() * 1000)
          }, room=sid)

          # 重新抛出异常以便上层处理
          raise RuntimeError(error_msg) from e
        

    async def handle_start_project(self, sid, data):
      """处理前端发起的项目启动请求"""
      try:
          goal = data.get('goal')
          if not goal:
              await self.sio.emit('error', {'message': '缺少需求参数'}, room=sid)
              return

          # 1. 处理产品经理的响应（调用核心函数）
          pm_prompt = f"用户需求：{goal}\n请生成详细的需求文档"
          pm_response = await self.stream_agent_response(
              "product_manager",
              pm_prompt,
              sid,
              "产品经理",
              "pm"
          )

          # 2. 处理开发者的响应（调用核心函数）
          dev_prompt = f"根据以下需求编写代码：\n{pm_response}"
          dev_response = await self.stream_agent_response(
              "developer",
              dev_prompt,
              sid,
              "后端工程师",
              "developer"
          )

        # 可选：发送最终结果汇总（根据需求调整）
          await self.sio.emit('message', {
              "sender": "系统",
              "content": "项目处理完成",
              "role": "system",
              "timestamp": int(time.time() * 1000)
          }, room=sid)

      except Exception as e:
          await self.sio.emit('error', {'message': str(e)}, room=sid)

    async def handle_connect(self, sid, environ):
        """连接事件处理"""
        print(f"客户端 {sid} 已连接")
        await self.sio.save_session(sid, {'status': 'connected'})

    async def handle_disconnect(self, sid):
        """断开事件处理"""
        print(f"客户端 {sid} 已断开")