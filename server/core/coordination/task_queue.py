import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4, UUID

@dataclass
class Task:
    """任务数据结构"""
    id: UUID
    session_id: UUID
    created_at: datetime
    phase: str
    context: Dict[str, str]
    status: str = "pending"  # pending/running/completed/failed

class TaskQueue:
    """异步任务队列管理器"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active_tasks: Dict[UUID, Task] = {}
        self.completed_tasks: Dict[UUID, Task] = {}

    async def add_task(self, session_id: UUID, phase: str, context: Dict[str, str]) -> UUID:
        """添加新任务到队列"""
        task = Task(
            id=uuid4(),
            session_id=session_id,
            created_at=datetime.now(),
            phase=phase,
            context=context
        )
        await self.queue.put(task)
        self.active_tasks[task.id] = task
        return task.id

    async def get_task(self) -> Task:
        """获取下一个待处理任务"""
        return await self.queue.get()

    def mark_completed(self, task_id: UUID):
        """标记任务完成"""
        if task := self.active_tasks.pop(task_id, None):
            task.status = "completed"
            self.completed_tasks[task_id] = task

    def mark_failed(self, task_id: UUID, error: str):
        """标记任务失败"""
        if task := self.active_tasks.get(task_id):
            task.status = "failed"
            task.context["error"] = error
            self.completed_tasks[task_id] = task

    def get_task_status(self, task_id: UUID) -> Optional[str]:
        """获取任务状态"""
        if task := self.active_tasks.get(task_id):
            return task.status
        if task := self.completed_tasks.get(task_id):
            return task.status
        return None