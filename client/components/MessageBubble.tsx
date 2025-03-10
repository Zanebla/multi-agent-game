import Avatar from './Avatar'
// import { Message } from '../types'

interface MessageBubbleProps {
  message: {
    sender: string
    content: string
    timestamp: number
    role?: 'user' | 'pm' | 'developer'
  }
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user'
  const roleMap: { [key: string]: 'user' | 'pm' | 'developer' } = {
    产品经理: 'pm',
    后端工程师: 'developer',
    user: 'user',
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {/* {!isUser && (
        <Avatar
          role={roleType}
          className="mr-2"
        />
      )} */}
      <div className="flex-shrink-0">
        <Avatar
          role={roleMap[message.sender as keyof typeof roleMap] || 'user'}
          className="w-10 h-10"
        />
      </div>

      <div
        className={`max-w-[70%] rounded-lg p-4 ${
          isUser
            ? 'bg-blue-500 text-white ml-auto'
            : message.sender === '产品经理'
            ? 'bg-green-100'
            : 'bg-purple-100'
        }`}>
        <div className="font-semibold text-sm mb-1">{message.sender}</div>
        <pre className="whitespace-pre-wrap break-words font-sans">
          {message.content}
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
          role="user"
          className="ml-2"
        />
      )}
    </div>
  )
}
