import Avatar from './Avatar'
import { Message } from '../types/message.types'
import { PlayIcon } from '@heroicons/react/24/outline'

interface MessageBubbleProps {
  message: Message
  onRunCode?: () => void
}

export default function MessageBubble({
  message,
  onRunCode,
}: MessageBubbleProps) {
  const isUser = message.role === 'USER'

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-4 mb-4`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <Avatar
            role={message.role}
            className="w-10 h-10 mr-4 rounded-full"
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
        {/* {message.status === 'streaming' && (
          <div className="absolute -top-2 right-2">
            <ArrowPathIcon className="w-4 h-4 animate-spin text-gray-500" />
          </div>
        )} */}
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

        {/* 在SDE消息底部添加运行按钮 */}
        {message.role === 'SDE' && onRunCode && (
          <div className="mt-2 flex justify-end">
            <button
              onClick={onRunCode}
              className="flex items-center gap-1 px-3 py-1 bg-green-600 text-white text-sm rounded-full hover:bg-green-500">
              <PlayIcon className="w-3 h-3" />
              运行代码
            </button>
          </div>
        )}
      </div>

      {isUser && (
        <Avatar
          role="USER"
          className="ml-2 rounded-full"
        />
      )}
    </div>
  )
}
