from pydantic import BaseModel
from typing import Optional, Dict, List


class TaskNode(BaseModel):
    """任务节点定义"""
    id: str               # 唯一标识符（如"T1"）
    description: str      # 任务描述（如"设计登录界面"）
    parent_id: Optional[str] = None  # 父任务ID
    assigned_to: str      # 负责角色（如"UI设计师"）
    status: str = "pending"  # 任务状态（pending/in-progress/done）
    children: List[str] = []  # 子任务ID列表


class TaskTree:
    """任务树管理器"""

    def __init__(self, root_description: str):
        self.tasks: Dict[str, TaskNode] = {}
        self._create_root(root_description)

    def _create_root(self, desc: str):
        """创建根任务"""
        root_task = TaskNode(
            id="T0",
            description=desc,
            assigned_to="项目经理"
        )
        self.tasks[root_task.id] = root_task

    def add_subtask(self, parent_id: str, description: str, assignee: str) -> str:
        """添加子任务"""
        if parent_id not in self.tasks:
            raise ValueError(f"父任务 {parent_id} 不存在")

        new_id = f"T{len(self.tasks)}"

        new_task = TaskNode(
            id=new_id,
            description=description,
            parent_id=parent_id,
            assigned_to=assignee
        )

        # 更新父子关系
        self.tasks[parent_id].children.append(new_id)
        self.tasks[new_id] = new_task

        return new_id
