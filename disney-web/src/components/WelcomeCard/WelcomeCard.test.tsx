import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { WelcomeCard } from './WelcomeCard'

describe('WelcomeCard', () => {
  it('renders welcome title and 4 suggestions', () => {
    const onSelect = vi.fn()
    render(<WelcomeCard onSelect={onSelect} />)
    expect(screen.getByText('欢迎来到迪士尼魔法世界')).toBeInTheDocument()
    expect(screen.getAllByRole('button')).toHaveLength(4)
  })

  it('calls onSelect with correct value when suggestion clicked', async () => {
    const onSelect = vi.fn()
    render(<WelcomeCard onSelect={onSelect} />)

    const btn = screen.getByRole('button', { name: '万圣节有什么活动？' })
    await btn.click()

    expect(onSelect).toHaveBeenCalledWith('万圣节有什么特别活动？')
  })
})
