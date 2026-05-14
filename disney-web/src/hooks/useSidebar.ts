import { useState, useMemo, useCallback } from 'react'
import type { Category } from '../types'

const CATEGORIES: Category[] = [
  { group: '园区服务', name: '园区门票', icon: '票', badge: 32, id: 'tickets' },
  { group: '园区服务', name: '酒店住宿', icon: '宿', badge: 18, id: 'hotels' },
  { group: '园区服务', name: '餐饮美食', icon: '餐', badge: 24, id: 'dining' },
  { group: '园区服务', name: '巡游演出', icon: '演', badge: 45, id: 'events' },
  { group: '实用信息', name: '快速通行证', icon: '快', badge: 12, id: 'fastpass' },
  { group: '实用信息', name: '季节活动', icon: '节', badge: 38, id: 'seasonal' },
  { group: '实用信息', name: '交通指南', icon: '行', badge: 15, id: 'transport' },
  { group: '实用信息', name: '购物推荐', icon: '购', badge: 21, id: 'shopping' },
  { group: '实用信息', name: '游客服务', icon: '务', badge: 28, id: 'services' },
]

export interface UseSidebarState {
  categories: Category[]
  activeId: string
}

export interface UseSidebarActions {
  selectCategory: (id: string) => void
  setSearch: (query: string) => void
}

export function useSidebar(): UseSidebarState & UseSidebarActions {
  const [activeId, setActiveId] = useState('tickets')
  const [search, setSearch] = useState('')

  const categories = useMemo(() => {
    if (!search) return CATEGORIES
    const q = search.toLowerCase()
    return CATEGORIES.filter(
      (c) => c.name.toLowerCase().includes(q) || c.icon.includes(q)
    )
  }, [search])

  const selectCategory = useCallback((id: string) => {
    setActiveId(id)
  }, [])

  return { categories, activeId, selectCategory, setSearch }
}
