export interface Message {
  id: string
  role: 'user' | 'bot'
  content: string
  tags?: ResourceTag[]
  timestamp: number
  streaming?: boolean
}

export interface ResourceTag {
  type: 'text' | 'image' | 'video'
  label: string
}

export interface Category {
  group: string
  name: string
  icon: string
  badge: number
  id: string
}

export interface ApiResponse {
  answer: string
  tags: ResourceTag[]
  sourceCount: number
}
