from pydantic import BaseModel

class Role(BaseModel):
    name: str
    expertise: str
    personality: str

ROLES = {
    "PM": Role(
        name="PM",
        expertise="需求分析",
        personality="严谨细致"
    ),
    "SDE": Role(
        name="SDE",
        expertise="软件开发",
        personality="逻辑性强"
    )
}