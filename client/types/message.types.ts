// types.ts（推荐单独的类型文件）
export type MessageStatus = 'streaming' | 'complete'
export type RoleType = 'user' | 'pm' | 'developer'

export interface Message {
  id: number
  sender: string
  content: string
  displayContent: string
  timestamp: number
  role: RoleType
  status: MessageStatus
}
