import { useCallback } from 'react'
import { useChat } from '../../hooks/useChat'
import { ChatHeader } from '../../components/ChatHeader/ChatHeader'
import { MessageList } from '../../components/MessageList/MessageList'
import { InputBar } from '../../components/InputBar/InputBar'
import './ChatPage.css'

export function ChatPage() {
  const { messages, isTyping, isLoading, sendMessage, clearMessages } = useChat()

  const handleSend = useCallback(
    (text: string) => {
      sendMessage(text)
    },
    [sendMessage]
  )

  const handleClear = useCallback(() => {
    clearMessages()
  }, [clearMessages])

  return (
    <main className="chat-area">
      <ChatHeader onClear={handleClear} />
      <MessageList messages={messages} isTyping={isTyping} onSuggestionClick={handleSend} />
      <InputBar onSend={handleSend} disabled={isLoading} />
    </main>
  )
}
