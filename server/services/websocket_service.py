import socketio
import asyncio
import time
from typing import AsyncGenerator
from core.roles import ROLES

class WebSocketService:
    def __init__(self, sio, agents):
        self.sio = sio
        self.agents = agents

    async def stream_agent_response(
        self,
        role: str,
        prompt: str,
        sid: str,
    ) -> str:
      """
      流式生成Agent响应并实时推送消息的核心函数

      参数:
      - role: 角色标识 (PM/SDE)
      - prompt: 输入提示
      - sid: 客户端会话ID
      """
      try:
          agent = self.agents.get(role)
          if not agent:
            raise ValueError(f"Agent role {role} not found")

          role_config = ROLES.get(role)
          if not role_config:
            raise ValueError(f"Role config for {role} not found")
          full_content = ""
          last_chunk_time = time.time()

          await self.sio.emit('status', {
              "sender": role,
              "status": "started",
              "role": role,
              "timestamp": int(time.time() * 1000)
          }, room=sid)

          async for chunk in agent.stream_response(prompt):
              full_content += chunk

              await self.sio.emit('message', {
                  "sender": role,
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
              "sender": role_config.name,
              "status": "completed",
              "role": role,
              "timestamp": int(time.time() * 1000)
          }, room=sid)
          return full_content

      except Exception as e:
          error_msg = f"{role.name}处理失败: {str(e)}"
          await self.sio.emit('error', {
              "sender": "SYS",
              "content": error_msg,
              "role": "SYS",
              "timestamp": int(time.time() * 1000)
          }, room=sid)

          raise RuntimeError(error_msg) from e
        

    async def handle_start_project(self, sid, data):
      """处理前端发起的项目启动请求"""
      try:
          goal = data.get('goal')
          if not goal:
              await self.sio.emit('error', {'message': '缺少需求参数'}, room=sid)
              return

          pm_prompt = f"用户需求：{goal}\n请生成详细的需求文档(不用输出代码)"
          pm_response = await self.stream_agent_response(
              "PM",
              pm_prompt,
              sid,
          )

          dev_prompt = f"""
          根据以下需求编写代码：
          {pm_response}
          输出要求：
          输出要求：
          1. 输出完整的HTML文件，包含<!DOCTYPE html>声明
          2. 必须包含<style>标签内的CSS和<script>标签内的JS
          3. 不要包含任何解释性文字
          4. 确保代码可直接在浏览器中运行
          5. 提供默认的页面标题和基本布局
          """
          dev_response = await self.stream_agent_response(
              "SDE",
              dev_prompt,
              sid,
          )

        # 发送完整代码给前端
          await self.sio.emit('full_code', {
              'code': dev_response,
              'role': 'SDE'
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