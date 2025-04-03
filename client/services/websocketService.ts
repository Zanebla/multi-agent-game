import { io, Socket } from 'socket.io-client'
import { Message } from '../types/message.types'

let messageId = 0
export const createMessage = (msg: Omit<Message, 'id'>): Message => ({
  id: messageId++,
  ...msg,
  displayContent: msg.displayContent || '',
  status: 'streaming',
})

export const initWebSocket = (
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>,
  onFullCodeReceived: (code: string) => void,
  setIsLoading: (loading: boolean) => void
): Socket => {
  const socket = io('http://localhost:8000', {
    path: '/socket.io/',
    transports: ['websocket'],
  })

  socket
    .on('connect', () => console.log('Connected to WebSocket'))
    .on('message', (data: any) => {
      const message = typeof data === 'string' ? JSON.parse(data) : data

      setMessages((prev) => {
        if (message.isChunk) {
          const existingMsg = prev.find(
            (m) =>
              m.sender === message.sender &&
              m.role === message.role &&
              m.status === 'streaming'
          )
          if (existingMsg) {
            return prev.map((m) =>
              m.id === existingMsg.id
                ? {
                    ...m,
                    content: m.content + message.content,
                    displayContent: m.displayContent + message.content,
                    status: message.isLastChunk ? 'complete' : 'streaming',
                  }
                : m
            )
          } else {
            const newMessage = createMessage({
              sender: message.sender,
              content: message.content,
              displayContent: '',
              role: message.role,
              timestamp: message.timestamp || Date.now(),
              status: 'streaming',
            })
            return [...prev, newMessage]
          }
        } else {
          const newMessage = createMessage({
            sender: message.sender,
            content: message.content,
            displayContent: message.content,
            role: message.role,
            status: 'complete',
            timestamp: message.timestamp || Date.now(),
          })
          return [...prev, newMessage]
        }
      })
    })

    .on('full_code', (data: { code: string }) => {
      onFullCodeReceived(data.code)
      setIsLoading(false)
      setMessages((prev) => [
        ...prev,
        createMessage({
          sender: 'SYS',
          content: '代码已生成，点击运行按钮查看结果',
          displayContent:
            'The code has been generated. Click the Start Game to try it out.',
          role: 'SYS',
          timestamp: Date.now(),
          status: 'complete',
        }),
      ])
    })

    .on('error', (err) => {
      console.error('Socket error details:', {
        message: err.message,
        stack: err.stack,
        rawError: err,
      })
      setMessages((prev) => [
        ...prev,
        createMessage({
          sender: 'SYS',
          content: `系统错误: ${err.message}`,
          displayContent: '',
          role: 'SYS',
          timestamp: Date.now(),
          status: 'complete',
        }),
      ])
    })

  return socket
}

export const sendMessage = (
  socket: Socket | null,
  content: string,
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>,
  setInputText: (text: string) => void,
  setIsLoading: (loading: boolean) => void
) => {
  if (!content.trim() || !socket) return

  const userMessage = createMessage({
    sender: 'USER',
    content,
    displayContent: content,
    timestamp: Date.now(),
    role: 'USER',
    status: 'complete',
  })

  setMessages((prev) => [...prev, userMessage])
  setInputText('')
  setIsLoading(true)

  try {
    socket.emit('start_project', { goal: content })
  } catch (error) {
    console.error('Error:', error)
    setIsLoading(false)
  }
}
