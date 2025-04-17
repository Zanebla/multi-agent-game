import Avatar from './Avatar'
import { Message } from '../types/message.types'
import ReactMarkdown from 'react-markdown'

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
            className="w-10 h-10 mr-4 rounded-full border-2 border-blue-500"
          />
        </div>
      )}

      <div
        data-testid="message-bubble"
        className={`max-w-[75%] rounded-lg p-4 relative
          ${
            isUser
              ? 'bg-blue-500 text-white ml-auto'
              : message.role === 'PM'
              ? 'bg-gold'
              : message.role === 'SDE'
              ? 'bg-pink'
              : 'bg-gray-100'
          }
        ${message.status === 'streaming' ? 'animate-pulse' : ''}
        `}>
        <div className="font-semibold text-sm mb-1">{message.sender}</div>
        <div className="whitespace-pre-wrap break-words font-sans">
          {message.status === 'streaming' ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : (
            message.content
          )}
        </div>
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
          className="ml-2 rounded-full border-2 border-blue-500"
        />
      )}
    </div>
  )
}
