import Avatar from './Avatar'
import { Message } from '../types/message.types'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user'
  const roleMap = {
    产品经理: 'pm',
    后端工程师: 'developer',
    UI设计师: 'ui_designer',
    user: 'user',
    系统: 'system',
  } as const

  // 头像颜色映射
  const avatarColors = {
    pm: 'bg-blue-500',
    developer: 'bg-green-500',
    ui_designer: 'bg-purple-500',
    system: 'bg-red-500',
    user: 'bg-gray-500',
  }

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-4 mb-4`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <Avatar
            role={roleMap[message.sender as keyof typeof roleMap] || 'user'}
            className="w-10 h-10 mr-4"
          />
        </div>
      )}

      <div
        className={`max-w-[75%] rounded-lg p-4 relative
          ${
            isUser
              ? 'bg-rose-100'
              : message.sender === '产品经理'
              ? 'bg-blue-100'
              : message.sender === '后端工程师'
              ? 'bg-green-100'
              : message.sender === 'UI设计师'
              ? 'bg-purple-100'
              : 'bg-red-100'
          }
        ${message.status === 'streaming' ? 'animate-pulse' : ''}
        `}>
        {/* 流式传输指示器 */}
        {message.status === 'streaming' && (
          <div className="absolute -bottom-2 right-0 flex items-center">
            <span className="text-xs text-gray-500 mr-1">思考中</span>
            <ArrowPathIcon className="w-3 h-3 animate-spin text-gray-500" />
          </div>
        )}
        <div className="font-semibold text-sm mb-1">{message.sender}</div>
        <pre className="whitespace-pre-wrap break-words font-sans">
          {message.status === 'streaming'
            ? message.displayContent
            : message.content}
        </pre>
        <div
          className={`text-xs mt-2 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>

      <Avatar
        role={
          message.sender in roleMap
            ? roleMap[message.sender as keyof typeof roleMap]
            : 'user'
        }
        className="w-10 h-10 mr-4"
      />
    </div>
  )
}
