import type { ResourceTag as TagType } from '../../types'
import './ResourceTag.css'

export interface ResourceTagProps {
  tag: TagType
  onClick?: () => void
}

export function ResourceTag({ tag, onClick }: ResourceTagProps) {
  const iconLabel = tag.type === 'image' ? '图' : tag.type === 'video' ? '视' : '文'
  const isClickable = !!onClick

  return (
    <span
      className={`resource-tag ${isClickable ? 'resource-tag--clickable' : ''}`}
      onClick={onClick}
    >
      <span className="tag-icon">{iconLabel}</span>
      {tag.label}
    </span>
  )
}
