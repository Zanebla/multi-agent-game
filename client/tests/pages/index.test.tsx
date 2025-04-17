import { render, screen } from '@testing-library/react' // 添加screen导入
import Index from '../../pages/index'
import { vi, beforeAll, describe, it, expect } from 'vitest'

describe('Index Page', () => {
  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = vi.fn(() => {})
    window.HTMLElement.prototype.scrollTo = vi.fn(() => {})
    window.HTMLElement.prototype.addEventListener = vi.fn()
    window.HTMLElement.prototype.removeEventListener = vi.fn()
  })

  it('should render without crashing', () => {
    const { container } = render(<Index />)
    expect(container).toBeInTheDocument()
  })

  it('should render input field', () => {
    render(<Index />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('should render submit button', () => {
    render(<Index />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
})
