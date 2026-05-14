import { useState } from 'react'
import type { Message, ResourceTag } from '../../types'
import { ResourceTag as ResourceTagComponent } from '../ResourceTag/ResourceTag'
import { ResourceDetail } from '../ResourceDetail/ResourceDetail'
import './MessageBubble.css'

export interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const avatarContent = isUser ? '游' : '✦'
  const senderLabel = isUser ? '你' : '迪士尼助手'
  const [expandedTag, setExpandedTag] = useState<ResourceTag | null>(null)

  const handleTagClick = (tag: ResourceTag) => {
    setExpandedTag((prev) => (prev?.label === tag.label ? null : tag))
  }

  return (
    <div className={`message ${message.role}`}>
      <div className="message-avatar">{avatarContent}</div>
      <div className="message-bubble">
        <div className="sender">{senderLabel}</div>
        <div className="text">
          {message.content}
          {message.streaming && <span className="streaming-cursor" />}
        </div>
        {!isUser && message.tags && message.tags.length > 0 && !message.streaming && (
          <div className="message-tags">
            {message.tags.map((tag, i) => (
              <ResourceTagComponent key={i} tag={tag} onClick={() => handleTagClick(tag)} />
            ))}
          </div>
        )}
        {expandedTag && (
          <ResourceDetail
            tag={expandedTag}
            isOpen={true}
            onClose={() => setExpandedTag(null)}
          />
        )}
      </div>
    </div>
  )
}
