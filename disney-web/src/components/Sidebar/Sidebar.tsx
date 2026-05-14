import { useSidebar } from '../../hooks/useSidebar'
import './Sidebar.css'

export interface SidebarProps {
  onCategorySelect?: (id: string) => void
}

export function Sidebar({ onCategorySelect }: SidebarProps) {
  const { categories, activeId, selectCategory, setSearch } = useSidebar()

  const groups = categories.reduce<Record<string, typeof categories>>((acc, cat) => {
    if (!acc[cat.group]) acc[cat.group] = []
    acc[cat.group].push(cat)
    return acc
  }, {})

  const handleClick = (id: string) => {
    selectCategory(id)
    onCategorySelect?.(id)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>
          <span className="icon" /> 知识分类
        </h3>
      </div>

      <div className="sidebar-search">
        <div className="sidebar-search-wrapper">
          <input
            type="text"
            placeholder="搜索分类..."
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="sidebar-list">
        {Object.entries(groups).map(([groupName, items]) => (
          <div key={groupName}>
            <div className="sidebar-group-label">{groupName}</div>
            {items.map((cat) => (
              <div
                key={cat.id}
                className={`sidebar-item ${activeId === cat.id ? 'active' : ''}`}
                onClick={() => handleClick(cat.id)}
              >
                <span className="item-icon">{cat.icon}</span>
                {cat.name}
                <span className="item-badge">{cat.badge}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <span className="status-dot" />
        知识库已更新 · 346 条记录
      </div>
    </aside>
  )
}
