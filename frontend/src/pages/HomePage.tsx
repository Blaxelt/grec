import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'

import {
    searchGamesGamesSearchGetOptions,
    getRecommendationsRecommendGetOptions,
} from '../client/@tanstack/react-query.gen'
import { SearchBox } from '../components/SearchBox'
import { RecommendationList } from '../components/RecommendationList'
import { Filter } from '../components/Filter'

export default function HomePage() {
    const [query, setQuery] = useState('')
    const [debouncedQuery, setDebouncedQuery] = useState('')
    const [selectedGame, setSelectedGame] = useState('')
    const [topN, setTopN] = useState(10)
    const [qualityPower, setQualityPower] = useState(1.0)
    const [isFilterOpen, setIsFilterOpen] = useState(false)

    useEffect(() => {
        const id = setTimeout(() => setDebouncedQuery(query), 300)
        return () => clearTimeout(id)
    }, [query])

    const { data: suggestions = [] } = useQuery({
        ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0 && query !== selectedGame,
    })

    const { data: recData, isLoading, isError } = useQuery({
        ...getRecommendationsRecommendGetOptions({ query: { game: selectedGame, top_n: topN, quality_power: qualityPower } }),
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

            <div className="search-row">
                <SearchBox
                    query={query}
                    onQueryChange={setQuery}
                    suggestions={suggestions}
                    showSuggestions={query !== selectedGame}
                    onSelectGame={selectGame}
                />
                <button className="filter-toggle" onClick={() => setIsFilterOpen(true)} title="Filters">
                    ⚙
                </button>
            </div>

            <Filter
                topN={topN}
                qualityPower={qualityPower}
                isOpen={isFilterOpen}
                onTopNChange={setTopN}
                onQualityPowerChange={setQualityPower}
                onClose={() => setIsFilterOpen(false)}
            />

            <RecommendationList isLoading={isLoading} isError={isError} data={recData} />
        </div>
    )
}
