const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export interface TextDetailItem {
  content: string
  source: string
}

export interface ImageDetailItem {
  url: string
  path: string
  content: string
}

export interface VideoDetailItem {
  url: string
  description: string
  content: string
}

export type DetailItem = TextDetailItem | ImageDetailItem | VideoDetailItem

export interface ResourceDetailResponse {
  items: DetailItem[]
}

export async function getResourceDetail(type: string, label: string): Promise<ResourceDetailResponse> {
  const resp = await fetch(`${API_BASE_URL}/api/resource/detail`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, label }),
  })

  if (!resp.ok) {
    throw new Error(`API error: ${resp.status}`)
  }

  return resp.json()
}
