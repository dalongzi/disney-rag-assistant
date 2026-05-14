import { useState, useCallback, useRef } from 'react'
import type { Message, ResourceTag } from '../types'
import { queryRagStream } from '../services/ragApi'

let idCounter = 0
const genId = () => `msg-${++idCounter}`

export interface UseChatState {
  messages: Message[]
  isTyping: boolean
  isLoading: boolean
}

export interface UseChatActions {
  sendMessage: (content: string) => void
  clearMessages: () => void
}

/** 缓存最后一次回答实际用到的 text 背景知识 */
let cachedContextItems: Array<{ metadata: { source: string; content: string } }> | null = null

export function getContextCache() {
  return cachedContextItems
}

export function useChat(): UseChatState & UseChatActions {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef(false)

  const sendMessage = useCallback((content: string) => {
    if (isLoading) return
    const trimmed = content.trim()
    if (!trimmed) return

    abortRef.current = false

    const userMsg: Message = {
      id: genId(),
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsTyping(true)
    setIsLoading(true)

    const botId = genId()
    setMessages((prev) => [...prev, {
      id: botId,
      role: 'bot',
      content: '',
      timestamp: Date.now(),
      tags: [],
      streaming: true,
    }])

    queryRagStream(trimmed, {
      onToken: (token) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId ? { ...m, content: m.content + token } : m
          )
        )
      },
      onContextItems: (items) => {
        cachedContextItems = items
      },
      onDone: (tags, sourceCount) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId ? { ...m, tags, streaming: false } : m
          )
        )
        setIsTyping(false)
        setIsLoading(false)
      },
      onError: (error) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId ? { ...m, content: `回答出错: ${error.message}`, streaming: false } : m
          )
        )
        setIsTyping(false)
        setIsLoading(false)
      },
    })
  }, [isLoading])

  const clearMessages = useCallback(() => {
    setMessages([])
    setIsTyping(false)
    setIsLoading(false)
    abortRef.current = true
    cachedContextItems = null
  }, [])

  return { messages, isTyping, isLoading, sendMessage, clearMessages }
}
