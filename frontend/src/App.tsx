import { useState, useEffect } from 'react'
import './index.css'

const API = 'http://localhost:8000'

type Recommendation = {
  game_name: string
  similarity: number
  wilson_score: number
  hybrid_score: number
}

function App() {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [targetGame, setTargetGame] = useState('')
  const [loading, setLoading] = useState(false)

  // Debounced search
  useEffect(() => {
    if (query.length < 1 || query === targetGame) {
      setSuggestions([])
      return
    }

    const timerId = setTimeout(async () => {
      const res = await fetch(`${API}/games/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      setSuggestions(data.map((g: { game_name: string }) => g.game_name))
    }, 300)

    return () => clearTimeout(timerId)
  }, [query, targetGame])

  // Select a game → fetch recommendations
  const selectGame = async (name: string) => {
    setQuery(name)
    setSuggestions([])
    setLoading(true)

    try {
      const res = await fetch(`${API}/recommend?game=${encodeURIComponent(name)}`)
      if (!res.ok) throw new Error('Not found')
      const data = await res.json()
      setTargetGame(data.target_game)
      setRecommendations(data.recommendations)
    } catch {
      setTargetGame('')
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>GREC</h1>
      <p className="subtitle">Game Recommendation Engine (Similarity Based Content)</p>

      <div className="search-wrapper">
        <input
          type="text"
          placeholder="Search for a game..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />

        {suggestions.length > 0 && (
          <ul className="suggestions">
            {suggestions.map((name) => (
              <li key={name} onClick={() => selectGame(name)}>
                {name}
              </li>
            ))}
          </ul>
        )}
      </div>

      {loading && <p className="loading">Finding similar games...</p>}

      {targetGame && recommendations.length > 0 && (
        <div className="results">
          <h2>Games similar to {targetGame}</h2>
          <div className="results-list">
            {recommendations.map((rec, i) => (
              <div key={i} className="result-card">
                <span className="rank">{i + 1}</span>
                <div className="result-info">
                  <span className="game-name">{rec.game_name}</span>
                  <span className="scores">
                    similarity {(rec.similarity * 100).toFixed(1)}% · quality {(rec.wilson_score * 100).toFixed(1)}%
                  </span>
                </div>
                <span className="hybrid">{(rec.hybrid_score * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App