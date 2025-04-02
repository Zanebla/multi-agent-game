import Avatar from './Avatar'
import { Message } from '../types/message.types'
import { ArrowPathIcon } from '@heroicons/react/24/outline'

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'USER'

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-4 mb-4`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <Avatar
            role={message.role}
            className="w-10 h-10 mr-4"
          />
        </div>
      )}

      <div
        className={`max-w-[75%] rounded-lg p-4 relative
          ${
            isUser
              ? 'bg-blue-500 text-white ml-auto'
              : message.role === 'PM'
              ? 'bg-green-100'
              : message.role === 'SDE'
              ? 'bg-purple-100'
              : 'bg-gray-100'
          }
        ${message.status === 'streaming' ? 'animate-pulse' : ''}
        `}>
        {/* 流式传输指示器 */}
        {message.status === 'streaming' && (
          <div className="absolute -top-2 right-2">
            <ArrowPathIcon className="w-4 h-4 animate-spin text-gray-500" />
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

      {isUser && (
        <Avatar
          role="USER"
          className="ml-2"
        />
      )}
    </div>
  )
}
