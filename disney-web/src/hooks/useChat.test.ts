import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useChat } from './useChat'
import * as ragApi from '../services/ragApi'

vi.mock('../services/ragApi')

function mockStreamImmediateDone() {
  vi.spyOn(ragApi, 'queryRagStream').mockImplementation((_q, callbacks) => {
    callbacks.onToken('mock')
    callbacks.onToken(' answer')
    callbacks.onDone([{ type: 'text', label: 'test' }], 1)
    return Promise.resolve()
  })
}

function mockStreamWithDelay() {
  vi.spyOn(ragApi, 'queryRagStream').mockImplementation(async (_q, callbacks) => {
    await new Promise((r) => setTimeout(r, 50))
    callbacks.onToken('delayed')
    callbacks.onDone([], 0)
  })
}

describe('useChat', () => {
  beforeEach(() => {
    mockStreamImmediateDone()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('starts with empty messages', () => {
    const { result } = renderHook(() => useChat())
    expect(result.current.messages).toEqual([])
    expect(result.current.isTyping).toBe(false)
    expect(result.current.isLoading).toBe(false)
  })

  it('adds user message and bot response on send', async () => {
    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.sendMessage('hello')
    })

    await waitFor(() => {
      expect(result.current.messages.length).toBe(2)
    })

    expect(result.current.messages[0].role).toBe('user')
    expect(result.current.messages[0].content).toBe('hello')
    expect(result.current.messages[1].role).toBe('bot')
    expect(result.current.messages[1].content).toContain('mock answer')
    expect(result.current.isLoading).toBe(false)
  })

  it('does not send empty messages', () => {
    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.sendMessage('   ')
    })

    expect(result.current.messages).toEqual([])
  })

  it('does not send while loading', async () => {
    mockStreamWithDelay()
    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.sendMessage('first')
    })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(true)
    })

    act(() => {
      result.current.sendMessage('second')
    })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.messages).toHaveLength(2)
  })

  it('clears all messages', async () => {
    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.sendMessage('test')
    })

    await waitFor(() => {
      expect(result.current.messages.length).toBeGreaterThan(0)
    })

    act(() => {
      result.current.clearMessages()
    })

    expect(result.current.messages).toEqual([])
    expect(result.current.isTyping).toBe(false)
  })
})
