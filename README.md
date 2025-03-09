# 多智能体协作游戏开发平台

## 项目概述

通过多角色 AI 智能体（产品经理/程序员/设计师等）协作开发小游戏的模拟系统，包含：

- 基于 LLM 的多角色对话引擎
- 任务分解与状态跟踪
- 实时聊天室前端

## 技术栈

- **后端**: Python + FastAPI
- **前端**: Next.js + TypeScript
- **AI 模型**: OpenAI GPT-3.5/4

## 快速启动

```bash
# 后端
cd server
pip install -r requirements.txt
uvicorn main:app --reload

# 前端
cd client
npm install
npm run dev
```
