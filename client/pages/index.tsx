// external modules
import React, { useState, useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import { CSSTransition, TransitionGroup } from 'react-transition-group'

// 单元测试
// 用户体验
// 打分维度，对比openai和deepseek，请3到5位用户测试。。。
// 生成内容，演示，两个系统的效果

// internal modules
import {
  ChatBubbleLeftIcon,
  ArrowPathIcon,
  PlayIcon,
} from '@heroicons/react/24/outline'
import MessageBubble from '../components/MessageBubble'
import { Message } from '../types/message.types'
import { initWebSocket, sendMessage } from '../services/websocketService'
import GlobalLoader from '../components/GlobalLoader'

export default function Chat() {
  const [fullCode, setFullCode] = useState<string>('')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedModel, setSelectedModel] = useState<'gpt-4o' | 'deepseek-v3'>(
    'gpt-4o'
  )

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const socket = initWebSocket(
      setMessages,
      (code) => {
        setFullCode(code)
      },
      setIsLoading
    )
    setSocket(socket)
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [])

  const handleSend = useCallback(() => {
    sendMessage(
      socket,
      inputText,
      setMessages,
      setInputText,
      setIsLoading,
      selectedModel
    )
  }, [socket, inputText, selectedModel])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="container mx-auto p-4">
      <GlobalLoader isLoading={isLoading} />
      {/* 页面顶部标题 */}
      <header className="mb-5">
        <div className="flex perspective-1000 justify-center items-center gap-2">
          <a
            href="https://github.com/Zanebla"
            target="_blank"
            rel="noopener noreferrer"
            className="text-4xl font-bold tracking-wide text-white hover:shadow-xl hover:bg-gold transition duration-300 ease-in-out }>">
            Zanebla's
          </a>
          <a
            href="https://github.com/Zanebla/multi-agent-game/tree/dev"
            target="_blank"
            rel="noopener noreferrer"
            className="text-4xl font-bold  tracking-wide text-white hover:shadow-xl hover:bg-pink transition duration-300 ease-in-out">
            Multi-Agent-Game(MAG)
          </a>
        </div>
      </header>

      {/* 消息展示区 */}
      <div
        style={{ height: '72vh' }}
        className="flex-1 overflow-y-auto p-6 bg-main rounded-lg mb-5 border-4 border-black">
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
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value as any)}
            className="w-32 px-4 py-2 bg-gray-700 text-white rounded">
            <option value="gpt-4o">GPT-4o</option>
            <option value="deepseek-v3">DeepSeek V3</option>
          </select>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Just enter your fantasy about the game..."
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
          {fullCode && (
            <button
              onClick={() => {
                const gameWindow = window.open('', '_blank')
                if (gameWindow) {
                  // 提取 HTML 内容部分
                  const htmlContent = fullCode.replace(/```html|```/g, '')
                  gameWindow.document.write(htmlContent)
                  gameWindow.document.close()
                }
              }}
              className="w-36 px-4 py-2 flex justify-center items-center bg-green-600 text-white rounded hover:bg-green-500">
              <PlayIcon className="w-5 h-10 animate-spin mx-0.5" />
              Start Game
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
