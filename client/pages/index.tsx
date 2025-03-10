import React from 'react'
import { useAgentWebSocket } from '../lib/websocket'
import { ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'

export default function ChatRoom() {
  const { messageHistory, sendAgentMessage } = useAgentWebSocket()
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (input.trim()) {
      sendAgentMessage(
        JSON.stringify({
          type: 'USER_INPUT',
          content: input,
        })
      )
      setInput('')
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="border rounded-lg p-4 mb-4 bg-white shadow-sm">
        {messageHistory.map((msg) => (
          <div
            key={msg.timestamp}
            className="mb-4 flex items-start gap-3">
            <ChatBubbleLeftIcon className="w-6 h-6 text-blue-500 mt-1" />
            <div>
              <div className="font-medium text-gray-700">{msg.sender}</div>
              <p className="text-gray-900">{msg.content}</p>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          className="flex-1 p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="输入任务目标..."
        />
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          发送
        </button>
      </div>
    </div>
  )
}
