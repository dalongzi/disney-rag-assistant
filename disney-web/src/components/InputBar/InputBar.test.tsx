import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { InputBar } from './InputBar'

describe('InputBar', () => {
  it('renders textarea and send button', () => {
    render(<InputBar onSend={vi.fn()} />)
    expect(screen.getByPlaceholderText('描述您的问题...')).toBeInTheDocument()
    expect(screen.getByTitle('发送')).toBeInTheDocument()
  })

  it('calls onSend with trimmed text when send clicked', async () => {
    const onSend = vi.fn()
    render(<InputBar onSend={onSend} />)

    const textarea = screen.getByPlaceholderText('描述您的问题...')
    const user = userEvent.setup()
    await user.type(textarea, '  hello  ')
    await user.click(screen.getByTitle('发送'))

    expect(onSend).toHaveBeenCalledWith('hello')
  })

  it('calls onSend when Enter pressed', async () => {
    const onSend = vi.fn()
    render(<InputBar onSend={onSend} />)

    const textarea = screen.getByPlaceholderText('描述您的问题...')
    const user = userEvent.setup()
    await user.type(textarea, 'test{Enter}')

    expect(onSend).toHaveBeenCalledWith('test')
  })

  it('does not call onSend for empty input', async () => {
    const onSend = vi.fn()
    render(<InputBar onSend={onSend} />)

    const user = userEvent.setup()
    await user.click(screen.getByTitle('发送'))

    expect(onSend).not.toHaveBeenCalled()
  })
})
