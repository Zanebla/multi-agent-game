// external modules
import React, { useState, useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import { CSSTransition, TransitionGroup } from 'react-transition-group'

// internal modules
import GlobalLoader from '../components/GlobalLoader'
import { ChatBubbleLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import MessageBubble from '../components/MessageBubble'
import MagIcon from '../components/MagIcon'
import { Message } from '../types/message.types'
import { initWebSocket, sendMessage } from '../services/websocketService'

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [fullCode, setFullCode] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [waitingForResponse, setWaitingForResponse] = useState(false)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const socket = initWebSocket((prevMessages: Message[]) => {
      return (msg: Message) => {
        // 添加msg参数
        const newMessages = [...prevMessages, msg]
        if (msg.role === 'SYS') {
          setWaitingForResponse(false)
        }
        return newMessages
      }
    }, setFullCode)
    setSocket(socket)
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [])

  const runCode = useCallback(() => {
    if (!fullCode) return

    // 去除代码块标记
    let cleanCode = fullCode
      .replace(/```html/g, '') // 去除开始标记
      .replace(/```/g, '') // 去除结束标记
      .trim() // 去除前后空格

    const newWindow = window.open('', '_blank')
    newWindow?.document.write(cleanCode)
    newWindow?.document.close()
  }, [fullCode])

  const handleSend = useCallback(async () => {
    setWaitingForResponse(true)
    try {
      await sendMessage(
        socket,
        inputText,
        setMessages,
        setInputText,
        setIsLoading
      )
    } catch (error) {
      console.error('发送消息失败:', error)
    } finally {
      setWaitingForResponse(false)
    }
  }, [socket, inputText])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="container mx-auto p-4">
      <GlobalLoader isLoading={waitingForResponse} />
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

      {/* 新增运行按钮 */}
      {fullCode && (
        <div className="flex justify-center mt-4">
          <button
            onClick={runCode}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500">
            运行代码
          </button>
        </div>
      )}

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
