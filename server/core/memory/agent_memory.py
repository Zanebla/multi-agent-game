from datetime import datetime
from typing import Deque
from collections import deque
import time

from .entry import MemoryEntry
from .config import MemoryConfig

class AgentMemory:
    """Agent专用记忆管理系统"""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.storage: Deque[MemoryEntry] = deque(maxlen=config.max_history)
        self.last_cleanup = time.time()

    def add_entry(self, role: str, content: str):
        """添加新的记忆条目"""
        self._auto_cleanup()
        entry = MemoryEntry(
            timestamp=time.time(),
            role=role,
            content=content[:200]  # 内容截断防止过长
        )
        self.storage.append(entry)

    def get_context(self, lookback: int = 5) -> str:
        """获取格式化上下文"""
        context = []
        for entry in list(self.storage)[-lookback:]:
            dt = datetime.fromtimestamp(entry.timestamp)
            context.append(
                f"[{dt.strftime('%m/%d %H:%M')} {entry.role}]: {entry.content}"
            )
        return "\n".join(context) or "暂无对话历史"

    def _auto_cleanup(self):
        """自动清理过期条目"""
        if time.time() - self.last_cleanup > 300:  # 每5分钟清理一次
            self._remove_expired_entries()
            self.last_cleanup = time.time()

    def _remove_expired_entries(self):
        """移除过期条目"""
        now = time.time()
        self.storage = deque(
            [entry for entry in self.storage
             if now - entry.timestamp < self.config.ttl],
            maxlen=self.config.max_history
        )