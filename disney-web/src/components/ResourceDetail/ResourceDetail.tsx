import { useEffect, useState } from 'react'
import type { ResourceTag } from '../../types'
import { getResourceDetail } from '../../services/resourceApi'
import type { DetailItem } from '../../services/resourceApi'
import { getContextCache } from '../../hooks/useChat'
import './ResourceDetail.css'

export interface ResourceDetailProps {
  tag: ResourceTag
  isOpen: boolean
  onClose: () => void
}

function renderItem(item: DetailItem, type: string) {
  if (type === 'text') {
    const textItem = item as { content: string; source: string }
    return (
      <div className="resource-detail-item" key={textItem.source}>
        <div className="resource-detail-source">{textItem.source}</div>
        <div className="resource-detail-content">{textItem.content}</div>
      </div>
    )
  }

  if (type === 'image') {
    const imgItem = item as { url: string; path: string; content: string }
    return (
      <div className="resource-detail-item" key={imgItem.path}>
        <img className="resource-detail-image" src={imgItem.url} alt={imgItem.content} />
      </div>
    )
  }

  if (type === 'video') {
    const videoItem = item as { url: string; description: string; content: string }
    return (
      <div className="resource-detail-item" key={videoItem.url}>
        <video className="resource-detail-video" controls>
          <source src={videoItem.url} />
        </video>
        <div className="resource-detail-content">{videoItem.description}</div>
      </div>
    )
  }

  return null
}

export function ResourceDetail({ tag, isOpen, onClose }: ResourceDetailProps) {
  const [items, setItems] = useState<DetailItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isOpen) return

    setLoading(true)
    setError(null)
    setItems([])

    // text 类型优先使用缓存的背景知识（与提示词中使用的完全一致）
    if (tag.type === 'text') {
      const cache = getContextCache()
      if (cache && cache.length > 0) {
        setItems(cache.map((r) => ({ content: r.metadata.content, source: r.metadata.source })))
        setLoading(false)
        return
      }
    }

    getResourceDetail(tag.type, tag.label)
      .then((data) => {
        setItems(data.items)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [tag.type, tag.label, isOpen])

  if (!isOpen) return null

  return (
    <div className="resource-detail">
      <div className="resource-detail-header">
        <span className="resource-detail-title">
          {tag.type === 'text' ? '相关记录' : tag.type === 'image' ? '相关图片' : '相关视频'}
        </span>
        <button className="resource-detail-close" onClick={onClose} aria-label="关闭">✕</button>
      </div>

      {loading && <div className="resource-detail-loading">加载中...</div>}
      {error && <div className="resource-detail-error">加载失败: {error}</div>}
      {!loading && !error && (
        <div className="resource-detail-list">
          {items.map((item) => renderItem(item, tag.type))}
        </div>
      )}
    </div>
  )
}
