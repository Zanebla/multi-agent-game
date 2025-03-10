import React from 'react'
import { useAgentWebSocket } from '../lib/websocket'
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { io, Socket } from 'socket.io-client'

interface Message {
  sender: string
  content: string
  timestamp: number
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
        },
      ])

      // 显示开发者响应
      setMessages((prev) => [
        ...prev,
        {
          sender: '后端工程师',
          content: response.data.dev,
          timestamp: Date.now(),
        },
      ])
    } catch (error) {
      console.error('启动失败:', error)
    }
  }

  return (
    <div className="container mx-auto p-4">
      {/* 消息展示区 */}
      <div className="h-96 border rounded-lg p-4 mb-4 overflow-y-auto">
        {messages.map((msg, i) => (
          <div
            key={i}
            className="mb-3 p-2 bg-gray-50 rounded">
            <div className="font-bold text-blue-600">{msg.sender}</div>
            <pre className="whitespace-pre-wrap">{msg.content}</pre>
            <div className="text-sm text-gray-500">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>

      {/* 输入控制区 */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="输入游戏目标，例如：开发一个猜数字小游戏"
          className="flex-1 p-2 border rounded"
        />
        <button
          onClick={startProject}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
          启动项目
        </button>
      </div>
    </div>
  )
}
