import type { ApiResponse, ResourceTag } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export interface StreamCallbacks {
  onToken: (token: string) => void
  onDone: (tags: ResourceTag[], sourceCount: number) => void
  onError: (error: Error) => void
}

export async function queryRagStream(question: string, callbacks: StreamCallbacks): Promise<void> {
  try {
    const resp = await fetch(`${API_BASE_URL}/api/ask/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })

    if (!resp.ok) {
      throw new Error(`API error: ${resp.status} ${resp.statusText}`)
    }

    const reader = resp.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let tags: ResourceTag[] = []
    let sourceCount = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const payload = JSON.parse(line.slice(6))
          if (payload.tags) {
            tags = payload.tags
            sourceCount = payload.sourceCount ?? 0
          }
          if (payload.token) {
            callbacks.onToken(payload.token)
          }
          if (payload.done) {
            callbacks.onDone(tags, sourceCount)
            return
          }
        } catch {
          // ignore malformed SSE data
        }
      }
    }
  } catch (err) {
    callbacks.onError(err instanceof Error ? err : new Error(String(err)))
  }
}

export async function queryRag(question: string): Promise<ApiResponse> {
  return new Promise<ApiResponse>((resolve, reject) => {
    let content = ''
    queryRagStream(question, {
      onToken: (token) => {
        content += token
      },
      onDone: (tags, sourceCount) => {
        resolve({ answer: content, tags, sourceCount })
      },
      onError: (error) => {
        reject(error)
      },
    })
  })
}
