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
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
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
        // const lastMsg = prev[prev.length - 1]
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

    .on('error', (err) => {
      console.error('Socket error:', err)
      setMessages((prev) => [
        ...prev,
        createMessage({
          sender: '系统',
          content: `错误: ${err.message}`,
          displayContent: '',
          role: 'system',
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
    sender: 'user',
    content,
    displayContent: content,
    timestamp: Date.now(),
    role: 'user',
    status: 'complete',
  })

  setMessages((prev) => [...prev, userMessage])
  setInputText('')
  setIsLoading(true)

  try {
    socket.emit('start_project', { goal: content })
  } catch (error) {
    console.error('Error:', error)
  } finally {
    setIsLoading(false)
  }
}
