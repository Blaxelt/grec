import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import HomePage from './pages/HomePage'
import GamePage from './pages/GamePage'
import SearchGame from './pages/SearchGame'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/games/:id" element={<GamePage />} />
        <Route path="/search" element={<SearchGame />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App