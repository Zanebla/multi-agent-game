from core.agents import Agent, Role
from core.coordinator import Coordinator, Message


def test_full_flow():
    # 初始化角色
    pm_role = Role(name="产品经理", expertise="需求分析", personality="严谨")
    dev_role = Role(name="开发工程师", expertise="后端开发", personality="理性")

    pm_agent = Agent(pm_role)
    dev_agent = Agent(dev_role)

    # 初始化协调器
    coordinator = Coordinator()
    coordinator.subscribe("产品经理")
    coordinator.subscribe("开发工程师")

    # 产品经理发起需求
    pm_msg = "我们需要用户登录功能，请评估实现时间"
    coordinator.post_message(
        Message(sender="产品经理",
                content=pm_msg,
                receiver="开发工程师")
    )

    # 开发工程师处理消息
    for msg in coordinator.distribute_messages():
        if msg.receiver == "开发工程师":
            response = dev_agent.generate_response(msg.content)
            coordinator.post_message(
                Message(sender="开发工程师",
                        content=response,
                        receiver="产品经理")
            )

    assert len(coordinator.conversation_log) == 2
    print("端到端流程测试通过！")
