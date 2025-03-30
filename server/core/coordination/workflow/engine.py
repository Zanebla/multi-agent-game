from typing import Dict, List, Optional
from pydantic import BaseModel
import networkx as nx
from .phases import WorkflowPhase

class WorkflowEngine:
    """工作流引擎，负责管理阶段执行顺序和转换"""
    
    def __init__(self, phases=None):
        self.graph = nx.DiGraph()
        self.phases: Dict[str, WorkflowPhase] = {}
        self.start_phase: Optional[str] = None

        if phases:
            for phase in phases:
                self.add_phase(phase)

    def add_phase(self, phase: WorkflowPhase):
        """添加工作流阶段"""
        self.phases[phase.name] = phase
        self.graph.add_node(phase.name)
        
        if not self.start_phase:
            self.start_phase = phase.name

    def add_transition(self, from_phase: str, to_phase: str):
        """添加阶段转换关系"""
        if from_phase in self.phases and to_phase in self.phases:
            self.graph.add_edge(from_phase, to_phase)

    def get_first_phase(self) -> Optional[WorkflowPhase]:
        """获取第一个工作流阶段"""
        if not self.start_phase:
            return None
        return self.phases.get(self.start_phase)

    def get_next_phase(self, current_phase: WorkflowPhase) -> Optional[WorkflowPhase]:
        """获取当前阶段的下一个阶段"""
        successors = list(self.graph.successors(current_phase.name))
        if not successors:
            return None
        return self.phases.get(successors[0])

    def validate_workflow(self) -> bool:
        """验证工作流有效性"""
        return nx.is_directed_acyclic_graph(self.graph)