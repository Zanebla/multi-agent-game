import { render, screen } from '@testing-library/react'
import Avatar from '../../components/Avatar'

describe('Avatar', () => {
  it('should render with default props', () => {
    render(<Avatar role="USER" />)
    expect(screen.getByRole('img')).toBeInTheDocument()
  })

  it('should apply custom className', () => {
    render(
      <Avatar
        role="PM"
        className="test-class"
      />
    )
    expect(screen.getByRole('img')).toHaveClass('test-class')
  })
})
