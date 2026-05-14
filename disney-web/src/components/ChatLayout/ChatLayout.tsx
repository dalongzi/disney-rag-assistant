import { Outlet } from 'react-router-dom'
import { TopNav } from '../TopNav/TopNav'
import './ChatLayout.css'

export function ChatLayout() {
  return (
    <div className="chat-layout-root">
      <TopNav />
      <Outlet />
    </div>
  )
}
