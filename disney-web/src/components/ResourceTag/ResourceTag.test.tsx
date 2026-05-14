import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ResourceTag } from './ResourceTag'

describe('ResourceTag', () => {
  it('renders image tag with correct icon', () => {
    render(<ResourceTag tag={{ type: 'image', label: 'test.jpg' }} />)
    expect(screen.getByText('图')).toBeInTheDocument()
    expect(screen.getByText('test.jpg')).toBeInTheDocument()
  })

  it('renders text tag with correct icon', () => {
    render(<ResourceTag tag={{ type: 'text', label: '指南 · 12条' }} />)
    expect(screen.getByText('文')).toBeInTheDocument()
  })

  it('renders video tag with correct icon', () => {
    render(<ResourceTag tag={{ type: 'video', label: 'demo.mp4' }} />)
    expect(screen.getByText('视')).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn()
    const tag = { type: 'text', label: '匹配 3 条相关记录' }
    render(<ResourceTag tag={tag} onClick={handleClick} />)
    await userEvent.click(screen.getByText('匹配 3 条相关记录'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('adds clickable class when onClick is provided', () => {
    const { container } = render(<ResourceTag tag={{ type: 'text', label: 'test' }} onClick={vi.fn()} />)
    const el = container.querySelector('.resource-tag')
    expect(el?.classList.contains('resource-tag--clickable')).toBe(true)
  })
})
