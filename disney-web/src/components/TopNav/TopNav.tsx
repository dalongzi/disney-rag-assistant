import { NavLink } from 'react-router-dom'
import './TopNav.css'

const NAV_LINKS = [
  { to: '/', label: '智能问答' },
  { to: '/knowledge', label: '知识库' },
  { to: '/guide', label: '游园指南' },
  { to: '/help', label: '帮助中心' },
]

export function TopNav() {
  return (
    <nav className="top-nav">
      <div className="logo">
        <div className="logo-castle">
          <div className="tower" />
          <div className="tower" />
          <div className="tower" />
          <div className="tower" />
          <div className="tower" />
          <div className="wall" />
          <div className="flag" />
        </div>
        <div className="logo-text">
          <span className="brand">迪士尼魔法助手</span>
          <span className="subtitle">RAG Knowledge Assistant</span>
        </div>
      </div>

      <ul className="nav-links">
        {NAV_LINKS.map((link) => (
          <li key={link.to}>
            <NavLink to={link.to} className={({ isActive }) => (isActive ? 'active' : '')}>
              {link.label}
            </NavLink>
          </li>
        ))}
      </ul>

      <div className="nav-user">
        <div className="notification">
          <div className="bell" />
          <div className="badge" />
        </div>
        <div className="avatar">游</div>
      </div>
    </nav>
  )
}
