import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ChatLayout } from './components/ChatLayout/ChatLayout'
import { ChatPage } from './pages/ChatPage/ChatPage'
import { KnowledgePage } from './pages/KnowledgePage/KnowledgePage'
import { GuidePage } from './pages/GuidePage/GuidePage'
import { HelpPage } from './pages/HelpPage/HelpPage'

import './styles/tokens.css'
import './styles/animations.css'
import './styles/global.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<ChatLayout />}>
          <Route path="/" element={<ChatPage />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="/guide" element={<GuidePage />} />
          <Route path="/help" element={<HelpPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
