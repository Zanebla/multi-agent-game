import { useState, useEffect } from 'react'
import useWebSocket from 'react-use-websocket'

const WS_URL = 'ws://localhost:8000/ws'

export function useAgentWebSocket() {
  const [messageHistory, setMessageHistory] = useState<Message[]>([])

  const { sendMessage, lastMessage } = useWebSocket(WS_URL, {
    onOpen: () => console.log('WebSocket连接建立'),
    shouldReconnect: () => true,
  })

  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data)
      setMessageHistory((prev) => [...prev, data])
    }
  }, [lastMessage])

  return { messageHistory, sendAgentMessage: sendMessage }
}

interface Message {
  sender: string
  content: string
  timestamp: string
  type: 'TASK_UPDATE' | 'DIALOG'
}
