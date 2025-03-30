from typing import Dict

WORKFLOW_PHASES: list[Dict] = [
    {
        "name": "需求分析",
        "agent": "product_manager",
        "input": "用户需求：{goal}",
        "output": "prd_document",
        "next": "开发实现",
    },
    {
        "name": "开发实现",
        "agent": "developer",
        "input": "根据需求实现代码：{prd_document}",
        "output": "initial_code",
        "next": "页面美化",
    },
    {
        "name": "页面美化",
        "agent": "ui_designer",
        "input": "根据初始代码提出美化建议：{initial_code}",
        "output": "design_suggestion",
        "next": "最终开发实现",
    },
    {
        "name": "最终开发实现",
        "agent": "developer",
        "input": "根据美化建议更新代码：{design_suggestion}",
        "output": "final_code",
        "next": None,
    },
]
