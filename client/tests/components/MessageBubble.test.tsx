import { render, screen } from '@testing-library/react'
import MessageBubble from '../../components/MessageBubble'
import { Message, RoleType } from '../../types/message.types'

describe('MessageBubble', () => {
  const mockMessage: Message = {
    id: 1,
    sender: 'Test User',
    content: 'Test content',
    displayContent: 'Test content',
    timestamp: Date.now(),
    role: 'USER' as RoleType,
    status: 'complete',
    conversationId: '123',
  }

  it('should render message content', () => {
    render(<MessageBubble message={mockMessage} />)
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('should show different style for PM role', () => {
    const pmMessage = { ...mockMessage, role: 'PM' as RoleType }
    render(<MessageBubble message={pmMessage} />)
    expect(screen.getByTestId('message-bubble')).toHaveClass('bg-gold')
  })
})
