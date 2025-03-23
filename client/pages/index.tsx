import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useAgentWebSocket } from '../lib/websocket'
import { ChatBubbleLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import axios from 'axios'
import { io, Socket } from 'socket.io-client'
import MessageBubble from '../components/MessageBubble'
import MagIcon from '../components/MagIcon'
import { CSSTransition, TransitionGroup } from 'react-transition-group'
import { Message } from '../types/message.types'

type RoleType = 'user' | 'pm' | 'developer'

// 自增ID生成器
let messageId = 0
const createMessage = (msg: Omit<Message, 'id'>): Message => ({
  id: messageId++,
  ...msg,
  displayContent: msg.displayContent || '',
  // status: msg.status || 'complete',
  status: 'streaming',
})

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 流式消息处理
  // const streamMessage = useCallback((targetId: number, fullText: string) => {
  //   let currentIndex = 0
  //   const interval = setInterval(() => {
  //     setMessages((prev) =>
  //       prev.map((msg) =>
  //         msg.id === targetId
  //           ? {
  //               ...msg,
  //               displayContent: fullText.slice(0, currentIndex),
  //               status:
  //                 currentIndex >= fullText.length ? 'complete' : 'streaming',
  //             }
  //           : msg
  //       )
  //     )

  //     if (currentIndex++ >= fullText.length) {
  //       clearInterval(interval)
  //     }
  //   }, 20)
  // }, [])

  // 初始化WebSocket连接
  // useEffect(() => {
  //   const newSocket = io('http://localhost:8000', {
  //     path: '/socket.io/', // 明确指定路径
  //     transports: ['websocket'],
  //   })
  //   newSocket.on('connect', () => {
  //     console.log('Connected to WebSocket')
  //   })

  //   newSocket
  //     .on('message', (data: any) => {
  //       const message = typeof data === 'string' ? JSON.parse(data) : data

  //       setMessages((prev) => {
  //         const lastMsg = prev[prev.length - 1]

  //         // 处理分块消息
  //         if (message.isChunk && lastMsg?.status === 'streaming') {
  //           return prev.map((msg) => ({
  //             ...msg,
  //             content: msg.content + message.content,
  //             displayContent: msg.displayContent + message.content,
  //           }))
  //         }

  //         // 创建新消息
  //         const newMessage = createMessage({
  //           sender: message.sender,
  //           content: message.content,
  //           displayContent: message.isChunk ? '' : message.content,
  //           timestamp: message.timestamp || Date.now(),
  //           role: message.role,
  //           status: message.isChunk ? 'streaming' : 'complete',
  //         })

  //         if (message.isChunk) {
  //           streamMessage(newMessage.id, message.content)
  //         }

  //         return [...prev, newMessage]
  //       })
  //     })
  //     .on('error', (err) => console.error('Socket error:', err))

  //   setSocket(newSocket)
  //   return () => {
  //     newSocket.disconnect()
  //   }
  // }, [streamMessage])

  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      path: '/socket.io/',
      transports: ['websocket'],
    })

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket')
    })

    newSocket.on('message', (data: any) => {
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
                    status: message.isLastChunk ? 'complete' : 'streaming', // 关键修改
                  }
                : m
            )
          } else {
            const newMsg = createMessage({
              sender: message.sender,
              content: message.content,
              displayContent: '',
              role: message.role,
              timestamp: message.timestamp || Date.now(),
              status: 'streaming',
            })
            return [...prev, newMsg]
          }
        } else {
          const newMsg = createMessage({
            sender: message.sender,
            content: message.content,
            displayContent: message.content,
            role: message.role,
            status: 'complete',
            timestamp: message.timestamp || Date.now(),
          })
          return [...prev, newMsg]
        }
      })
    })

    newSocket.on('status', (statusData) => {
      if (statusData.status === 'completed') {
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.sender === statusData.sender) {
              return {
                ...msg,
                status: 'complete',
              }
            }
            return msg
          })
        )
      }
    })

    newSocket.on('error', (err) => {
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

    setSocket(newSocket)
    return () => {
      newSocket.disconnect()
    }
  }, [])

  // 发送消息处理
  const handleSend = async () => {
    if (!inputText.trim() || !socket) return

    // 用户消息
    const userMessage = createMessage({
      sender: 'user',
      content: inputText,
      displayContent: inputText,
      timestamp: Date.now(),
      role: 'user',
      status: 'complete',
    })

    setMessages((prev) => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      // 使用socket.io发送请求
      socket.emit('start_project', { goal: inputText })
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // 输入框键盘事件
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="container mx-auto p-4">
      {/* 页面顶部标题 */}
      <header className="mb-5">
        <div className="flex perspective-1000 justify-center items-center gap-2">
          <MagIcon />
          <a
            href="https://github.com/Zanebla"
            target="_blank"
            rel="noopener noreferrer"
            className="text-4xl font-bold italic tracking-wide text-amber-400 hover:text-amber-600 transition-colors duration-200">
            Zanebla
          </a>
          <span className="text-4xl font-bold text-gray-600">/</span>
          <a
            href="https://github.com/Zanebla/multi-agent-game/tree/dev"
            target="_blank"
            rel="noopener noreferrer"
            className="text-4xl font-bold italic tracking-wide text-rose-400 hover:text-rose-600 transition-colors duration-200">
            MAG
          </a>
        </div>
      </header>

      {/* 消息展示区 */}
      <div
        style={{ height: '72vh' }}
        className="flex-1 overflow-y-auto p-6 bg-slate-800 rounded-lg mb-5">
        {/* {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
          />
        ))} */}
        <TransitionGroup component={null}>
          {messages.map((msg) => (
            <CSSTransition
              key={msg.id}
              timeout={300}
              classNames="message"
              unmountOnExit>
              <MessageBubble message={msg} />
            </CSSTransition>
          ))}
        </TransitionGroup>
        <div
          ref={messagesEndRef}
          style={{ height: 0 }}
        />
      </div>

      {/* 输入控制区 */}
      <div className="flex gap-2">
        <div className=" mx-auto flex gap-3">
          <textarea
            // ref={inputRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Paint your dreams, my boss"
            className="w-96 flex-1 p-2 border rounded resize-none focus:outline-none focus:ring-2 focus:ring-rose-900"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="w-24 px-4 py-2 flex justify-center items-center bg-rose-600 text-white rounded hover:bg-rose-400">
            {isLoading ? (
              <ArrowPathIcon className="w-5 h-5 animate-spin" />
            ) : (
              <span>
                <ChatBubbleLeftIcon className="w-5 h-5" /> Send
              </span>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
