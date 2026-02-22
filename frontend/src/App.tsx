import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import './index.css'

import {
  searchGamesGamesSearchGetOptions,
  getRecommendationsRecommendGetOptions,
} from './client/@tanstack/react-query.gen'

function App() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [selectedGame, setSelectedGame] = useState('')

  // Debounce the raw input
  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(id)
  }, [query])

  // Search suggestions
  const { data: suggestions = [] } = useQuery({
    ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
    enabled: debouncedQuery.length > 0 && query !== selectedGame,
  })

  // Recommendations
  const { data: recData, isLoading } = useQuery({
    ...getRecommendationsRecommendGetOptions({ query: { game: selectedGame } }),
    enabled: selectedGame.length > 0,
  })

  const selectGame = (name: string) => {
    setQuery(name)
    setSelectedGame(name)
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

        {suggestions.length > 0 && query !== selectedGame && (
          <ul className="suggestions">
            {suggestions.map((g) => (
              <li key={g.game_name}>
                <button
                  onClick={() => selectGame(g.game_name)}
                  className="suggestion-btn"
                >
                  {g.game_name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {isLoading && <p className="loading">Finding similar games...</p>}

      {recData && recData.recommendations.length > 0 && (
        <div className="results">
          <h2>Games similar to {recData.target_game}</h2>
          <div className="results-list">
            {recData.recommendations.map((rec, i) => (
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