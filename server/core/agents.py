from pydantic import BaseModel
from typing import List
from services.llm_service import generate_response


class Role(BaseModel):
    name: str
    expertise: str
    personality: str


class Agent:
    def __init__(self, role: Role):
        self.role = role
        self.memory: List[str] = []

    def generate_prompt(self, input_text: str) -> str:
        memory_context = " | ".join(self.memory[-3:]) if self.memory else "无"
        prompt = f"""
        # 角色设定
        你是一个专业的{self.role.name}，擅长{self.role.expertise}。
        你的性格特征：{self.role.personality}
        
        # 对话背景
        近期对话记录：
        {memory_context}
        
        # 当前任务
        请根据以下输入生成符合角色的回复：
        {input_text}
        """
        return prompt.strip()

    def generate_response(self, input_text: str) -> str:
        prompt = self.generate_prompt(input_text)
        response = generate_response(prompt)
        self.memory.append(f"{self.role.name}收到：{input_text}")
        self.memory.append(f"{self.role.name}回复：{response}")
        return response or "暂时无法回应"
