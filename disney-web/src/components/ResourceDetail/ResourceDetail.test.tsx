import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ResourceDetail } from './ResourceDetail'

// Mock the API service
vi.mock('../../services/resourceApi', () => ({
  getResourceDetail: vi.fn(),
}))

import { getResourceDetail } from '../../services/resourceApi'

const mockGetResourceDetail = vi.mocked(getResourceDetail)

describe('ResourceDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    mockGetResourceDetail.mockReturnValue(new Promise(() => {}))
    render(<ResourceDetail tag={{ type: 'text', label: '匹配 3 条' }} isOpen={true} onClose={vi.fn()} />)
    expect(screen.getByText(/加载中/)).toBeInTheDocument()
  })

  it('renders text items with content and source', async () => {
    const items = [
      { content: '迪士尼门票 399 元', source: 'test.txt' },
      { content: '快速通行证使用方法', source: 'guide.txt' },
    ]
    mockGetResourceDetail.mockResolvedValue({ items })

    render(<ResourceDetail tag={{ type: 'text', label: '匹配 3 条' }} isOpen={true} onClose={vi.fn()} />)
    expect(await screen.findByText('迪士尼门票 399 元')).toBeInTheDocument()
    expect(screen.getByText('guide.txt')).toBeInTheDocument()
  })

  it('renders image items with img tag', async () => {
    const items = [
      { url: '/static/images/test.jpeg', path: 'images/test.jpeg', content: '[图片] 测试' },
    ]
    mockGetResourceDetail.mockResolvedValue({ items })

    render(<ResourceDetail tag={{ type: 'image', label: 'test.jpeg' }} isOpen={true} onClose={vi.fn()} />)
    const img = await screen.findByRole('img') as HTMLImageElement
    expect(img.src).toContain('test.jpeg')
  })

  it('renders video items with video tag', async () => {
    const items = [
      { url: 'https://example.com/video.mp4', description: '测试视频', content: '[视频] 测试' },
    ]
    mockGetResourceDetail.mockResolvedValue({ items })

    render(<ResourceDetail tag={{ type: 'video', label: 'https://example.com/video.mp4' }} isOpen={true} onClose={vi.fn()} />)
    expect(await screen.findByText('测试视频')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const handleClose = vi.fn()
    mockGetResourceDetail.mockResolvedValue({ items: [{ content: 'test', source: 'a.txt' }] })

    render(<ResourceDetail tag={{ type: 'text', label: 'test' }} isOpen={true} onClose={handleClose} />)
    const closeBtn = await screen.findByRole('button')
    await userEvent.click(closeBtn)
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  it('does not fetch when isOpen is false', () => {
    render(<ResourceDetail tag={{ type: 'text', label: 'test' }} isOpen={false} onClose={vi.fn()} />)
    expect(mockGetResourceDetail).not.toHaveBeenCalled()
  })

  it('shows error state on API failure', async () => {
    mockGetResourceDetail.mockRejectedValue(new Error('Network error'))

    render(<ResourceDetail tag={{ type: 'text', label: 'test' }} isOpen={true} onClose={vi.fn()} />)
    expect(await screen.findByText(/加载失败/)).toBeInTheDocument()
  })
})
