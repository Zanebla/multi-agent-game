export type MessageStatus = 'streaming' | 'complete' | 'error'
export type MessageRole = 'user' | 'pm' | 'developer' | 'ui_designer' | 'system'

export interface BaseMessage {
  id: string
  sender: string
  content: string
  displayContent: string
  role: MessageRole
  status: MessageStatus
  timestamp: number
}

export interface SystemMessage extends BaseMessage {
  type: 'system_status'
  role: 'system'
  isChunk?: never
  isLastChunk?: never
}

export interface StreamingMessage extends BaseMessage {
  isChunk: true
  isLastChunk?: boolean
  streamId: string
}

export interface NormalMessage extends BaseMessage {
  isChunk?: false
  isLastChunk?: never
  streamId?: never
}

export type Message = SystemMessage | StreamingMessage | NormalMessage
