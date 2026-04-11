import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'

import {
    searchGamesGamesSearchGetOptions,
    getRecommendationsRecommendGetOptions,
} from '../client/@tanstack/react-query.gen'
import { SearchBox } from '../components/SearchBox'
import { RecommendationList } from '../components/RecommendationList'
import { Filter } from '../components/Filter'
import { NavigationBar } from '../components/NavigationBar'

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
        <>
            <NavigationBar />
            <div className="flex flex-col items-center h-screen pt-20">
                <h1 className='font-press text-8xl tracking-wider'>GREC</h1>
                <p className="pt-5 mb-10 tracking-normal">Game Recommendation System</p>

                <div className="flex items-center gap-2 w-full max-w-2xl">
                    <SearchBox
                        query={query}
                        onQueryChange={setQuery}
                        suggestions={suggestions}
                        showSuggestions={query !== selectedGame}
                        onSelectGame={selectGame}
                    />
                    <button className="w-12 h-11.5 bg-surface border border-border rounded-lg hover:border-accent cursor-pointer
                    hover:text-accent shrink-0 flex items-center justify-center" onClick={() => setIsFilterOpen(true)} title="Filters">
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
        </>
    )
}
