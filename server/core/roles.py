from pydantic import BaseModel

class Role(BaseModel):
    name: str
    expertise: str
    personality: str

# 预定义角色配置字典
ROLES = {
    "product_manager": Role(
        name="产品经理",
        expertise="需求分析",
        personality="严谨细致"
    ),
    "developer": Role(
        name="后端工程师",
        expertise="软件开发",
        personality="逻辑性强"
    )
}