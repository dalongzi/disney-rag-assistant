import './ChatHeader.css'

export interface ChatHeaderProps {
  onClear?: () => void
}

export function ChatHeader({ onClear }: ChatHeaderProps) {
  return (
    <div className="chat-header">
      <div className="chat-header-left">
        <div className="chat-header-avatar">
          <span className="mini-castle">✦</span>
          <span className="online-dot" />
        </div>
        <div className="chat-header-info">
          <h2>迪士尼魔法客服助手</h2>
          <p>基于 346 条知识库记录 · 支持文本/图片/视频检索</p>
        </div>
      </div>
      <div className="chat-header-actions">
        <button className="chat-header-btn" title="清除对话" onClick={onClear}>
          ＋
        </button>
        <button className="chat-header-btn" title="设置">
          ⚙
        </button>
      </div>
    </div>
  )
}
