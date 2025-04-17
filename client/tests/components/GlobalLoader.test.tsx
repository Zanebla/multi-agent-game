import { render, screen } from '@testing-library/react'
import GlobalLoader from '../../components/GlobalLoader'

describe('GlobalLoader', () => {
  it('should not render when not loading', () => {
    render(<GlobalLoader isLoading={false} />)
    expect(screen.queryByTestId('loader')).toBeNull()
  })

  it('should render when loading', () => {
    render(<GlobalLoader isLoading={true} />)
    const loader = screen.getByTestId('loader')
    expect(loader).toBeInTheDocument()
  })
})
