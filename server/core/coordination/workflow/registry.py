from typing import Dict
from .phases import WorkflowPhase
from .engine import WorkflowEngine

class WorkflowRegistry:
    """工作流注册表，管理预定义工作流"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowEngine] = {}

    def register_workflow(self, name: str, workflow: WorkflowEngine):
        """注册工作流"""
        if workflow.validate_workflow():
            self.workflows[name] = workflow
        else:
            raise ValueError("无效的工作流定义")

    def get_workflow(self, name: str) -> WorkflowEngine:
        """获取已注册的工作流"""
        return self.workflows.get(name)

    def list_workflows(self) -> Dict[str, List[str]]:
        """列出所有工作流及其阶段"""
        return {
            name: list(workflow.graph.nodes)
            for name, workflow in self.workflows.items()
        }