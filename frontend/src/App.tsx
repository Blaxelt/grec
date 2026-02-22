import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import './index.css'

import {
  searchGamesGamesSearchGetOptions,
  getRecommendationsRecommendGetOptions,
} from './client/@tanstack/react-query.gen'
import { SearchBox } from './components/SearchBox'
import { RecommendationList } from './components/RecommendationList'

function App() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [selectedGame, setSelectedGame] = useState('')

  useEffect(() => {
    const id = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(id)
  }, [query])

  const { data: suggestions = [] } = useQuery({
    ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
    enabled: debouncedQuery.length > 0 && query !== selectedGame,
  })

  const { data: recData, isLoading, isError } = useQuery({
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
      <p className="subtitle"><br />Game Recommendation Engine (Similarity Based Content)</p>

      <SearchBox
        query={query}
        onQueryChange={setQuery}
        suggestions={suggestions}
        showSuggestions={query !== selectedGame}
        onSelectGame={selectGame}
      />

      <RecommendationList isLoading={isLoading} isError={isError} data={recData} />
    </div>
  )
}

export default App