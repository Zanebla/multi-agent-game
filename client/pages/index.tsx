import React, { useState, useRef, useEffect } from 'react'
import { CSSTransition, TransitionGroup } from 'react-transition-group'
import { ChatBubbleLeftIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import MessageBubble from '../components/MessageBubble'
import MagIcon from '../components/MagIcon'
import { useMessages } from '../hooks/useMessages'
import { useSocket } from '../hooks/useSocket'
import type { Message } from '../types/message.types'
/**
 * 主聊天界面组件
 * 负责：
 * 1. 管理用户输入和消息发送
 * 2. 显示聊天消息列表
 * 3. 处理WebSocket连接和消息接收
 */
export default function Chat() {
  // 用户输入状态
  const [inputText, setInputText] = useState('')
  // 加载状态（发送消息时显示加载动画）
  const [isLoading, setIsLoading] = useState(false)
  // 用于自动滚动到消息底部的引用
  const messagesEndRef = useRef<HTMLDivElement>(null)

  /*
   * 使用自定义Hook管理消息状态
   * messages: 当前消息列表
   * handleIncomingMessage: 处理接收到的消息
   * addMessage: 添加新消息
   */
  const { messages, handleIncomingMessage, addMessage } = useMessages()

  /*
   * 使用自定义Hook管理WebSocket连接
   * socket: Socket.io实例
   * isConnected: 连接状态
   * sessionId: 当前会话ID
   * sendMessage: 发送消息方法
   */
  const { socket, isConnected, sessionId, sendMessage } = useSocket()

  // 当消息列表变化时自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
    })
  }, [messages])

  // 注册WebSocket事件监听器
  useEffect(() => {
    if (!socket) return

    const handleSocketMessage = (data: unknown) => {
      try {
        // 确保data是对象类型
        const messageData = typeof data === 'string' ? JSON.parse(data) : data
        if (messageData && typeof messageData === 'object') {
          handleIncomingMessage(messageData)
        } else {
          throw new Error('无效的消息格式')
        }
        setIsLoading(false)
      } catch (err: unknown) {
        console.error('消息处理错误:', err)
        addMessage({
          sender: '系统',
          content: `消息处理错误: ${
            err instanceof Error ? err.message : '未知错误'
          }`,
          role: 'system',
          status: 'complete',
          timestamp: Date.now(),
          id: Date.now().toString(), // 确保有id字段
          displayContent: '', // 确保有displayContent字段
        } as Message) // 添加类型断言
      }
    }

    // 修改错误处理函数
    const handleSocketError = (err: Error | string) => {
      console.error('WebSocket错误:', err)
      const errorMessage = typeof err === 'string' ? err : err.message
      addMessage({
        sender: '系统',
        content: `连接错误: ${errorMessage}`,
        role: 'system',
        status: 'complete',
        timestamp: Date.now(),
        id: Date.now().toString(),
        displayContent: '',
      } as Message)
      setIsLoading(false)
    }

    // 注册事件监听
    socket.on('message', handleSocketMessage)
    socket.on('error', handleSocketError)

    // 组件卸载时清理
    return () => {
      socket.off('message', handleSocketMessage)
      socket.off('error', handleSocketError)
    }
  }, [socket, handleIncomingMessage, addMessage])

  /**
   * 发送消息处理函数
   */
  const handleSend = async () => {
    if (!sessionId) {
      console.log('正在获取会话ID...')
      return
    }
    if (!inputText.trim() || !isConnected) return

    setIsLoading(true)

    // 添加用户消息到列表
    addMessage({
      sender: '用户',
      content: inputText,
      role: 'user',
      status: 'complete',
      timestamp: Date.now(),
      id: Date.now().toString(),
      displayContent: inputText,
    } as Message)

    // 清空输入框
    setInputText('')

    try {
      // 通过WebSocket发送消息
      await sendMessage('start_project', {
        goal: inputText,
        meta: {
          session_id: sessionId,
          timestamp: Date.now(),
        },
      })
    } catch (error) {
      // 错误处理
      console.error('发送消息失败:', error)
      addMessage({
        sender: '系统',
        content: `发送失败: ${
          error instanceof Error ? error.message : String(error)
        }`,
        role: 'system',
        status: 'complete',
        timestamp: Date.now(),
        id: Date.now().toString(),
        displayContent: '',
      } as Message)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * 处理键盘事件（按Enter发送消息）
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      {/* 头部标题和Logo */}
      <header className="mb-5">
        <div className="flex perspective-1000 justify-center items-center gap-2">
          <MagIcon />
          <h1 className="text-4xl font-bold italic tracking-wide text-amber-400">
            多智能体协作系统
          </h1>
        </div>
      </header>

      {/* 连接状态提示 */}
      {!isConnected && (
        <div className="mb-2 text-center text-yellow-500">
          正在连接服务器，请稍候...
        </div>
      )}

      {/* 消息列表容器 */}
      <div
        className="flex-1 overflow-y-auto p-6 bg-slate-800 rounded-lg mb-5"
        style={{ height: '70vh' }}>
        <TransitionGroup component="div">
          {messages.map((msg) => (
            <CSSTransition
              key={msg.id}
              timeout={300}
              classNames="message"
              nodeRef={messagesEndRef}
              unmountOnExit>
              <MessageBubble message={msg} />
            </CSSTransition>
          ))}
        </TransitionGroup>
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="flex gap-2">
        <div className="mx-auto flex gap-3 w-full">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="请输入您的需求..."
            className="flex-1 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!isConnected || isLoading}
            className="w-24 px-4 py-3 flex justify-center items-center bg-blue-600 text-white rounded-lg hover:bg-blue-500 disabled:bg-gray-400 transition-colors">
            {isLoading ? (
              <ArrowPathIcon className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <ChatBubbleLeftIcon className="w-5 h-5 mr-1" />
                发送
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
