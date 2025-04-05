export type MessageStatus = 'streaming' | 'complete'
export type RoleType = 'USER' | 'PM' | 'SDE' | 'SYS'

export interface Message {
  id: number
  sender: string
  content: string
  displayContent: string
  timestamp: number
  role: RoleType
  status: MessageStatus
  conversationId: string
}
