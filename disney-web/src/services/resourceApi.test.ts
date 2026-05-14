import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getResourceDetail } from './resourceApi'

describe('resourceApi', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls /api/resource/detail with correct payload', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [{ content: 'test', source: 'a.txt' }] }),
    } as Response)

    const result = await getResourceDetail('text', '匹配 3 条')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:5000/api/resource/detail',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'text', label: '匹配 3 条' }),
      }
    )
    expect(result.items).toHaveLength(1)
  })

  it('throws on non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 404,
    } as Response)

    await expect(getResourceDetail('image', 'missing.jpeg')).rejects.toThrow('API error: 404')
  })
})
