import { useState, useCallback } from 'react'
import type {
  Message,
  StreamingMessage,
  SystemMessage,
} from '../types/message.types'

export function useMessages() {
  const [messages, setMessages] = useState<Message[]>([])
  const generateId = () =>
    `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`

  const createBaseMessage = useCallback(
    (params: Omit<Message, 'id'>): Message =>
      ({
        id: generateId(),
        displayContent: params.content || '',
        timestamp: Date.now(),
        isChunk: false,
        ...params,
      } as Message),
    []
  )

  const handleStreamingMessage = useCallback(
    (msg: StreamingMessage) => {
      setMessages((prev) => {
        const isStreamingMessage = (m: Message): m is StreamingMessage =>
          'streamId' in m && m.isChunk === true

        const existingMsgIndex = prev.findIndex(
          (m) =>
            isStreamingMessage(m) &&
            m.streamId === msg.streamId &&
            m.status === 'streaming'
        )

        // 更新现有流式消息
        if (existingMsgIndex >= 0) {
          const updated = [...prev]
          const existing = updated[existingMsgIndex]

          updated[existingMsgIndex] = {
            ...existing,
            content: existing.content + msg.content,
            displayContent: (existing.displayContent || '') + msg.content,
            status: msg.isLastChunk ? 'complete' : 'streaming',
          }
          return updated
        }

        // 新建流式消息
        return [
          ...prev,
          createBaseMessage({
            ...msg,
            status: 'streaming',
          }),
        ]
      })
    },
    [createBaseMessage]
  )

  // 处理系统消息
  const handleSystemMessage = useCallback(
    (msg: SystemMessage) => {
      setMessages((prev) => [
        ...prev,
        createBaseMessage({
          ...msg,
          status: 'complete',
        }),
      ])
    },
    [createBaseMessage]
  )

  // 统一消息处理器
  const handleIncomingMessage = useCallback(
    (data: unknown) => {
      const msg = typeof data === 'string' ? JSON.parse(data) : data

      if (msg.type === 'system_status') {
        handleSystemMessage(msg as SystemMessage)
      } else if (msg.isChunk) {
        handleStreamingMessage(msg as StreamingMessage)
      } else {
        setMessages((prev) => [
          ...prev,
          createBaseMessage({
            ...msg,
            status: 'complete',
          }),
        ])
      }
    },
    [handleSystemMessage, handleStreamingMessage, createBaseMessage]
  )

  // 添加新消息（公开方法）
  const addMessage = useCallback(
    (msg: Omit<Message, 'id'>) => {
      setMessages((prev) => [...prev, createBaseMessage(msg)])
    },
    [createBaseMessage]
  )

  // 更新指定消息（公开方法）
  const updateMessage = useCallback((id: string, update: Partial<Message>) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id
          ? ({
              ...m,
              ...update,
              // 确保合并后的对象符合Message类型
              status: update.status ?? m.status,
              role: update.role ?? m.role,
            } as Message)
          : m
      )
    )
  }, [])

  // 清空消息历史（公开方法）
  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  // 获取最后N条消息（示例）
  const getLastMessages = useCallback(
    (count: number) => {
      return messages.slice(-count)
    },
    [messages]
  )

  return {
    messages,
    handleIncomingMessage,
    addMessage, // 新增
    updateMessage, // 新增
    clearMessages, // 新增
    getLastMessages, // 新增
  }
}
