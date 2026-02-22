import { useState, useEffect } from 'react'
import './index.css'

import { searchGamesGamesSearchGet, getRecommendationsRecommendGet } from './client'
import type { GameRecommendation } from './client'

function App() {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [recommendations, setRecommendations] = useState<GameRecommendation[]>([])
  const [targetGame, setTargetGame] = useState('')
  const [loading, setLoading] = useState(false)

  // Debounced search
  useEffect(() => {
    if (query.length < 1 || query === targetGame) {
      setSuggestions([])
      return
    }

    const timerId = setTimeout(async () => {
      const { data } = await searchGamesGamesSearchGet({ query: { q: query } })
      setSuggestions((data ?? []).map((g) => g.game_name))
    }, 300)

    return () => clearTimeout(timerId)
  }, [query, targetGame])

  // Select a game → fetch recommendations
  const selectGame = async (name: string) => {
    setQuery(name)
    setSuggestions([])
    setLoading(true)

    try {
      const { data } = await getRecommendationsRecommendGet({ query: { game: name } })
      if (!data) throw new Error('Not found')
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
              <li key={name}>
                <button
                  onClick={() => selectGame(name)}
                  className="suggestion-btn"
                >
                  {name}
                </button>
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