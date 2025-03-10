import React, { useState, useEffect } from 'react'
import { useAgentWebSocket } from '../lib/websocket'
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import axios from 'axios'
import { io, Socket } from 'socket.io-client'
import MessageBubble from '../components/MessageBubble'

type RoleType = 'user' | 'pm' | 'developer'

interface Message {
  sender: string
  content: string
  timestamp: number
  role?: RoleType
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)

  // 初始化WebSocket连接
  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      path: '/socket.io/', // 明确指定路径
      transports: ['websocket'],
    })
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket')
    })
    newSocket.on('message', (msg: string) => {
      const data = JSON.parse(msg)
      setMessages((prev) => [...prev, data])
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
    const userMessage = {
      sender: 'user',
      content: inputText,
      timestamp: Date.now(),
      role: 'user' as RoleType,
    }

    setMessages((prev) => [...prev, userMessage])
    setInputText('')

    // 调用启动项目函数
    await startProject()
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
          timestamp: Date.now(),
          role: 'pm',
        },
      ])

      // 显示开发者响应
      setMessages((prev) => [
        ...prev,
        {
          sender: '后端工程师',
          content: response.data.dev,
          timestamp: Date.now(),
          role: 'developer',
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
      {/* 消息展示区 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {messages.map((msg, i) => (
            <MessageBubble
              key={i}
              message={msg}
            />
          ))}
        </div>
      </div>

      {/* 输入控制区 */}
      <div className="flex gap-2">
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="输入游戏目标，例如：开发一个猜数字小游戏"
            className="flex-1 p-2 border rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <button
            onClick={handleSend}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
            <ChatBubbleLeftIcon className="w-5 h-5" />
            发送
          </button>
        </div>
      </div>
    </div>
  )
}
