import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TypingIndicator } from './TypingIndicator'

describe('TypingIndicator', () => {
  it('renders three dots', () => {
    const { container } = render(<TypingIndicator />)
    const spans = container.querySelectorAll('.typing-indicator span')
    expect(spans).toHaveLength(3)
  })
})
