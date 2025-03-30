import { useState, useEffect, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import type {
  Message,
  StreamingMessage,
  SystemMessage,
} from '../types/message.types'

interface SocketConfig {
  url?: string
  path?: string
  transports?: string[]
}

export function useSocket(config?: SocketConfig) {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)

  // 初始化Socket连接
  useEffect(() => {
    const socketInstance = io(config?.url || 'http://localhost:8000', {
      path: config?.path || '/socket.io/',
      transports: config?.transports || ['websocket'],
      extraHeaders: {
        'X-Session-ID': localStorage.getItem('sessionId') || '',
      },
      autoConnect: true,
    })

    setSocket(socketInstance)

    return () => {
      socketInstance.disconnect()
    }
  }, [config?.url, config?.path, config?.transports])

  // 连接状态管理
  const connect = useCallback(() => {
    if (!socket) return

    socket.connect()
    socket.on('connect', () => {
      setIsConnected(true)
      console.log('Socket连接成功:', socket.id)
    })

    socket.on('disconnect', () => {
      setIsConnected(false)
      console.log('Socket断开连接')
    })

    socket.on('connect_error', (err) => {
      console.error('Socket连接错误:', err.message)
    })

    // 会话管理事件
    socket.on('session_ready', (data: { session_id: string }) => {
      setSessionId(data.session_id)
      localStorage.setItem('sessionId', data.session_id)
    })
  }, [socket])

  // 断开连接
  const disconnect = useCallback(() => {
    if (socket) {
      socket.disconnect()
    }
  }, [socket])

  // 发送消息
  const sendMessage = useCallback(
    (event: string, payload: unknown, callback?: (response: any) => void) => {
      if (!socket || !isConnected) {
        console.error('Socket未连接')
        return
      }

      // 自动附加会话ID
      const messageWithSession = {
        ...(typeof payload === 'object' ? payload : {}),
        meta: {
          socket_id: socket.id,
          session_id: sessionId,
        },
      }

      socket.emit(event, messageWithSession, callback)
    },
    [socket, isConnected, sessionId]
  )

  // 注册消息处理器
  const registerHandler = useCallback(
    (event: string, handler: (data: unknown) => void) => {
      if (!socket) return

      socket.on(event, (data) => {
        try {
          const parsedData = typeof data === 'string' ? JSON.parse(data) : data
          handler(parsedData)
        } catch (err) {
          console.error(`处理${event}消息错误:`, err)
        }
      })

      return () => {
        socket.off(event)
      }
    },
    [socket]
  )

  return {
    socket,
    isConnected,
    sessionId,
    connect,
    disconnect,
    sendMessage,
    registerHandler,
  }
}
