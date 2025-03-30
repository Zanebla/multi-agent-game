from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Dict, Optional, List
import networkx as nx


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskPhase(BaseModel):
    """任务阶段模型"""
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    output: Optional[str] = None
    error: Optional[str] = None


class TaskContext(BaseModel):
    """任务上下文数据"""
    initial_input: str
    phase_outputs: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)


class WorkflowTask(BaseModel):
    """工作流任务模型"""
    task_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    current_phase: str = "init"
    status: TaskStatus = TaskStatus.PENDING
    phases: Dict[str, TaskPhase] = Field(default_factory=dict)
    context: TaskContext
    dependency_graph: Optional[nx.DiGraph] = None
    retry_count: int = 0
    max_retries: int = 3

    def add_phase(self, phase_name: str):
        """添加新阶段"""
        self.phases[phase_name] = TaskPhase(
            name=phase_name,
            start_time=datetime.now()
        )

    def complete_phase(self, phase_name: str, output: str):
        """标记阶段完成"""
        if phase := self.phases.get(phase_name):
            phase.end_time = datetime.now()
            phase.status = TaskStatus.COMPLETED
            phase.output = output
            self.current_phase = phase_name

    def fail_phase(self, phase_name: str, error: str):
        """标记阶段失败"""
        if phase := self.phases.get(phase_name):
            phase.end_time = datetime.now()
            phase.status = TaskStatus.FAILED
            phase.error = error

    def can_retry(self) -> bool:
        """检查是否可重试"""
        return self.retry_count < self.max_retries


class TaskDependencyGraph:
    """任务依赖图管理器"""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependency(self, from_task: str, to_task: str):
        """添加依赖关系"""
        self.graph.add_edge(from_task, to_task)

    def get_execution_order(self) -> List[List[str]]:
        """获取拓扑排序执行顺序"""
        return list(nx.topological_generations(self.graph))
