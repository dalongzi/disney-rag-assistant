import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MessageBubble } from './MessageBubble'

// Mock the resource API
vi.mock('../../services/resourceApi', () => ({
  getResourceDetail: vi.fn(),
}))

describe('MessageBubble', () => {
  it('renders user message with correct label', () => {
    render(<MessageBubble message={{ id: '1', role: 'user', content: 'hello', timestamp: 1 }} />)
    expect(screen.getByText('你')).toBeInTheDocument()
    expect(screen.getByText('hello')).toBeInTheDocument()
  })

  it('renders bot message with avatar and resource tags', () => {
    render(
      <MessageBubble
        message={{
          id: '2',
          role: 'bot',
          content: 'answer',
          tags: [{ type: 'text', label: 'guide · 3条' }],
          timestamp: 2,
        }}
      />
    )
    expect(screen.getByText('迪士尼助手')).toBeInTheDocument()
    expect(screen.getByText('文')).toBeInTheDocument()
    expect(screen.getByText('guide · 3条')).toBeInTheDocument()
  })

  it('renders bot message without tags when empty', () => {
    render(<MessageBubble message={{ id: '3', role: 'bot', content: 'no tags', timestamp: 3 }} />)
    expect(screen.getByText('no tags')).toBeInTheDocument()
    expect(screen.queryByText('文')).not.toBeInTheDocument()
  })

  it('expands resource detail when tag is clicked', async () => {
    const { getResourceDetail } = await import('../../services/resourceApi')
    vi.mocked(getResourceDetail).mockResolvedValue({
      items: [{ content: 'test content', source: 'test.txt' }],
    })

    render(
      <MessageBubble
        message={{
          id: '4',
          role: 'bot',
          content: 'answer',
          tags: [{ type: 'text', label: '匹配 3 条相关记录' }],
          timestamp: 4,
        }}
      />
    )

    const tag = screen.getByText('匹配 3 条相关记录')
    await userEvent.click(tag)
    expect(await screen.findByText('test content')).toBeInTheDocument()
  })
})
