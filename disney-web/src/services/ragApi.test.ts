import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { queryRagStream, queryRag } from './ragApi'

function createMockReadableStream(events: string[]): ReadableStream {
  const encoder = new TextEncoder()
  const fullText = events.map((e) => `data: ${e}\n\n`).join('')
  let sent = false

  return new ReadableStream({
    pull(controller) {
      if (sent) {
        controller.close()
        return
      }
      controller.enqueue(encoder.encode(fullText))
      sent = true
    },
  })
}

describe('queryRagStream', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('receives tokens via onToken callback and calls onDone', async () => {
    const meta = JSON.stringify({ tags: [{ type: 'text', label: 'test' }], sourceCount: 1 })
    const events = [
      meta,
      JSON.stringify({ token: '你好' }),
      JSON.stringify({ token: '，迪士尼' }),
      JSON.stringify({ done: true }),
    ]

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      body: createMockReadableStream(events),
    } as Response)

    const tokens: string[] = []
    let doneTags: any[] = []
    let doneCount = 0

    await queryRagStream('test', {
      onToken: (t) => tokens.push(t),
      onDone: (tags, count) => {
        doneTags = tags
        doneCount = count
      },
      onError: () => {},
    })

    expect(tokens).toEqual(['你好', '，迪士尼'])
    expect(doneTags).toEqual([{ type: 'text', label: 'test' }])
    expect(doneCount).toBe(1)
  })

  it('calls onError on API failure', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
    } as Response)

    let caughtError: Error | null = null
    await queryRagStream('test', {
      onToken: () => {},
      onDone: () => {},
      onError: (err) => {
        caughtError = err
      },
    })

    expect(caughtError).toBeInstanceOf(Error)
    expect(caughtError?.message).toContain('500')
  })
})

describe('queryRag (wrapper)', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('accumulates tokens and returns full response', async () => {
    const meta = JSON.stringify({ tags: [{ type: 'text', label: 'match' }], sourceCount: 3 })
    const events = [
      meta,
      JSON.stringify({ token: '答' }),
      JSON.stringify({ token: '案' }),
      JSON.stringify({ done: true }),
    ]

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      body: createMockReadableStream(events),
    } as Response)

    const result = await queryRag('question')
    expect(result.answer).toBe('答案')
    expect(result.tags).toEqual([{ type: 'text', label: 'match' }])
    expect(result.sourceCount).toBe(3)
  })
})
