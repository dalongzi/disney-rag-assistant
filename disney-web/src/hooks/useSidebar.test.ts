import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSidebar } from './useSidebar'

describe('useSidebar', () => {
  it('starts with default active category', () => {
    const { result } = renderHook(() => useSidebar())
    expect(result.current.activeId).toBe('tickets')
    expect(result.current.categories).toHaveLength(9)
  })

  it('filters categories by search', () => {
    const { result } = renderHook(() => useSidebar())

    act(() => {
      result.current.setSearch('票')
    })

    expect(result.current.categories).toHaveLength(1)
    expect(result.current.categories[0].id).toBe('tickets')
  })

  it('selects a category', () => {
    const { result } = renderHook(() => useSidebar())

    act(() => {
      result.current.selectCategory('events')
    })

    expect(result.current.activeId).toBe('events')
  })

  it('returns all categories when search is cleared', () => {
    const { result } = renderHook(() => useSidebar())

    act(() => {
      result.current.setSearch('test')
    })
    act(() => {
      result.current.setSearch('')
    })

    expect(result.current.categories).toHaveLength(9)
  })
})
