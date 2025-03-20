import React, { useState, useEffect, useRef } from 'react'
import { useAgentWebSocket } from '../lib/websocket'
import { ChatBubbleLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import axios from 'axios'
import { io, Socket } from 'socket.io-client'
import MessageBubble from '../components/MessageBubble'
import MagIcon from '../components/MagIcon'
import { CSSTransition, TransitionGroup } from 'react-transition-group'
import { Message } from '../types/message.types'

type RoleType = 'user' | 'pm' | 'developer'

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  // 使用 useRef 创建 EndRef
  const EndRef = useRef<HTMLDivElement>(null)
  const typingSpeed = 20 // 打字速度（毫秒/字符）

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
    })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 流式处理函数
  const streamMessage = (messageId: number, fullText: string) => {
    let currentIndex = 0
    const message = messages[messageId]

    const typingInterval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        const newContent = fullText.slice(0, currentIndex)
        setMessages((prev) =>
          prev.map((msg, index) =>
            index === messageId ? { ...msg, displayContent: newContent } : msg
          )
        )
        currentIndex++
        scrollToBottom()
      } else {
        clearInterval(typingInterval)
        setMessages((prev) =>
          prev.map((msg, index) =>
            index === messageId ? { ...msg, status: 'complete' } : msg
          )
        )
      }
    }, typingSpeed)
  }

  // 初始化WebSocket连接
  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      path: '/socket.io/', // 明确指定路径
      transports: ['websocket'],
    })
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket')
    })
    newSocket.on('processing', () => {
      setMessages((prev) => [
        ...prev,
        {
          sender: '系统',
          content: '正在处理中...',
          displayContent: '正在处理中...',
          timestamp: Date.now(),
          status: 'complete',
        },
      ])
    })
    newSocket.on('message', (msg: string) => {
      const data = JSON.parse(msg)
      const newMessage = {
        ...data,
        displayContent: '',
        status: 'streaming' as const,
      }
      setMessages((prev) => {
        const newMessages = [...prev, newMessage]
        setTimeout(() => {
          streamMessage(newMessages.length - 1, data.content)
        }, 300)
        return newMessages
      })
    })
    setSocket(newSocket)
    return () => {
      newSocket.disconnect()
    }
  }, [])

  // 发送消息处理
  const handleSend = async () => {
    if (!inputText.trim()) return

    // 用户消息
    const userMessage: Message = {
      sender: 'user',
      content: inputText,
      displayContent: inputText,
      timestamp: Date.now(),
      role: 'user',
      status: 'streaming',
    }

    setMessages((prev) => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      await startProject()
    } finally {
      setIsLoading(false)
    }
  }

  // 启动项目流程
  const startProject = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/start-project',
        { goal: inputText },
        {
          headers: {
            'Content-Type': 'application/json', // 明确指定JSON格式
          },
        }
      )

      // 显示产品经理需求
      setMessages((prev) => [
        ...prev,
        {
          sender: '产品经理',
          content: response.data.pm,
          displayContent: '',
          timestamp: Date.now(),
          role: 'pm',
          status: 'streaming',
        },
      ])

      // 显示开发者响应
      setMessages((prev) => [
        ...prev,
        {
          sender: '后端工程师',
          content: response.data.dev,
          displayContent: '',
          timestamp: Date.now(),
          role: 'developer',
          status: 'streaming',
        },
      ])
    } catch (error) {
      console.error('启动失败:', error)
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
          {messages.map((msg, i) => (
            <CSSTransition
              key={i}
              timeout={300}
              classNames="message"
              unmountOnExit>
              <MessageBubble
                key={msg.timestamp + msg.sender}
                message={msg}
              />
            </CSSTransition>
          ))}
        </TransitionGroup>
        <div ref={EndRef} />
      </div>

      {/* 输入控制区 */}
      <div className="flex gap-2">
        <div className=" mx-auto flex gap-3">
          <textarea
            ref={inputRef}
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
