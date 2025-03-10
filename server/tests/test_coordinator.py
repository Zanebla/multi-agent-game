from core.coordinator import Coordinator, Message
from datetime import datetime


def test_message_flow():
    coordinator = Coordinator()

    # 角色订阅
    coordinator.subscribe("产品经理")
    coordinator.subscribe("开发工程师")

    # 发送测试消息
    coordinator.post_message(Message("系统", "项目启动", receiver=None))
    coordinator.post_message(Message("产品经理", "需要增加登录功能", receiver="开发工程师"))

    # 验证消息分发
    messages = list(coordinator.distribute_messages())
    assert len(messages) == 3  # 1广播消息分发给2订阅者 + 1定向消息
    print("消息分发测试通过!")


if __name__ == "__main__":
    test_message_flow()
