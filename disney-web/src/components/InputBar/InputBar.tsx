import { useRef, useCallback } from 'react'
import './InputBar.css'

export interface InputBarProps {
  onSend: (text: string) => void
  disabled?: boolean
}

export function InputBar({ onSend, disabled }: InputBarProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = useCallback(() => {
    const el = textareaRef.current
    if (!el || disabled) return
    const text = el.value.trim()
    if (!text) return
    onSend(text)
    el.value = ''
    el.style.height = 'auto'
  }, [onSend, disabled])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 80)}px`
  }

  return (
    <div className="input-bar">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          id="chatInput"
          rows={1}
          placeholder="描述您的问题..."
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          disabled={disabled}
        />
        <div className="input-tools">
          <button className="input-tool" title="上传图片">
            ▤
          </button>
          <button className="input-tool" title="语音输入">
            ◉
          </button>
        </div>
        <button className="send-btn" id="sendBtn" title="发送" onClick={handleSend} disabled={disabled}>
          ➤
        </button>
      </div>
      <div className="input-footer">
        <span className="shortcut-hint">
          <kbd>Enter</kbd> 发送 · <kbd>Shift+Enter</kbd> 换行
        </span>
        <span>知识库索引 v2.1</span>
      </div>
    </div>
  )
}
