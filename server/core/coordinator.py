from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    sender: str          # 发送者角色名
    content: str         # 消息内容
    receiver: Optional[str] = None  # 接收者（None表示广播）
    timestamp: datetime = datetime.now()


class Coordinator:
    def __init__(self):
        self.message_queue = []       # 待处理消息队列
        self.conversation_log = []    # 完整对话记录
        self.subscribers = set()      # 订阅者列表（角色名）

    def post_message(self, message: Message):
        """将消息加入队列并记录日志"""
        self.message_queue.append(message)
        self.conversation_log.append(message)

    def get_next_message(self) -> Optional[Message]:
        """获取并移除下一条消息"""
        if self.message_queue:
            return self.message_queue.pop(0)
        return None

    def subscribe(self, role_name: str):
        """角色订阅消息"""
        self.subscribers.add(role_name)

    def distribute_messages(self):
        """分发消息给订阅者"""
        while msg := self.get_next_message():
            if msg.receiver:  # 定向消息
                if msg.receiver in self.subscribers:
                    yield msg
            else:  # 广播消息
                for sub in self.subscribers:
                    yield Message(
                        sender=msg.sender,
                        content=msg.content,
                        receiver=sub
                    )
