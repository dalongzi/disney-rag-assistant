import { useEffect, useRef } from 'react'
import type { Message } from '../../types'
import { MessageBubble } from '../MessageBubble/MessageBubble'
import { WelcomeCard } from '../WelcomeCard/WelcomeCard'
import { TypingIndicator } from '../TypingIndicator/TypingIndicator'
import './MessageList.css'

export interface MessageListProps {
  messages: Message[]
  isTyping: boolean
  onSuggestionClick: (text: string) => void
}

export function MessageList({ messages, isTyping, onSuggestionClick }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  const hasMessages = messages.length > 0

  return (
    <div className="messages" ref={containerRef}>
      {!hasMessages && <WelcomeCard onSelect={onSuggestionClick} />}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isTyping && (
        <div className="message bot">
          <div className="message-avatar">✦</div>
          <div className="message-bubble">
            <TypingIndicator />
          </div>
        </div>
      )}
    </div>
  )
}
