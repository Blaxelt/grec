import { useState } from "react";
import { SearchBox } from "../components/SearchBox";
import { TagSearchBox } from "../components/TagSearchBox";
import { NavigationBar } from "../components/NavigationBar";
import { GameCard } from "../components/GameCard";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { searchGamesGamesSearchGetOptions, searchGamesByTagsGamesByTagsGetOptions } from '../client/@tanstack/react-query.gen';
import type { GameSearchResult, GameTagResult } from '../client';
import { useDebouncedQuery } from '../hooks/useDebouncedQuery';

const PAGE_SIZE = 10;

export default function SearchGame() {
    const { query, setQuery, debouncedQuery } = useDebouncedQuery()
    const navigate = useNavigate();

    const { data: suggestions = [] } = useQuery({
        ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0,
    })

    const selectGame = (game: GameSearchResult) => {
        navigate(`/games/${game.app_id}`)
    }

    const [selectedTags, setSelectedTags] = useState<string[]>([])
    const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)

    const addTag = (tag: string) => {
        setSelectedTags((prev) => [...prev, tag])
        setVisibleCount(PAGE_SIZE)
    }

    const removeTag = (tag: string) => {
        setSelectedTags((prev) => prev.filter((t) => t !== tag))
        setVisibleCount(PAGE_SIZE)
    }

    const { data: tagResults = [], isFetching: isTagFetching } = useQuery({
        ...searchGamesByTagsGamesByTagsGetOptions({
            query: { tags: selectedTags, limit: visibleCount },
        }),
        enabled: selectedTags.length > 0,
    })

    const hasMore = tagResults.length === visibleCount

    return (
        <>
            <NavigationBar />
            <div className="flex flex-col gap-4 pt-24 w-full max-w-3xl mx-auto px-4 pb-16">
                <section>
                    <h1 className="font-press text-3xl tracking-wider text-center mb-8">Search</h1>
                    <SearchBox
                        query={query}
                        onQueryChange={setQuery}
                        suggestions={suggestions}
                        showSuggestions={query.length > 0}
                        onSelectGame={selectGame}
                    />
                </section>

                <div className="flex items-center gap-4 my-4">
                    <div className="flex-1 h-px bg-border" />
                    <span className="text-text text-sm font-press">or browse by tags</span>
                    <div className="flex-1 h-px bg-border" />
                </div>

                <section>
                    <TagSearchBox
                        selectedTags={selectedTags}
                        onAddTag={addTag}
                        onRemoveTag={removeTag}
                    />

                    {selectedTags.length > 0 && (
                        <div className="mt-6">
                            {tagResults.length === 0 && !isTagFetching && (
                                <p className="text-text-dim text-center py-8">
                                    No games found with {selectedTags.length === 1 ? 'this tag' : 'all these tags'}.
                                </p>
                            )}

                            {tagResults.length > 0 && (
                                <>
                                    <p className="text-text-dim text-sm mb-3">
                                        Showing {tagResults.length} game{tagResults.length !== 1 && 's'}
                                    </p>
                                    <div className="flex flex-col gap-2">
                                        {tagResults.map((game: GameTagResult) => (
                                            <GameCard
                                                key={game.app_id}
                                                appId={game.app_id}
                                                gameName={game.game_name}
                                                headerImage={game.header_image}
                                                tags={game.tags}
                                            />
                                        ))}
                                    </div>

                                    {hasMore && (
                                        <button
                                            onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
                                            disabled={isTagFetching}
                                            className="mt-4 w-full py-2.5 rounded-lg border border-border bg-surface
                                                hover:border-accent hover:text-accent transition-all cursor-pointer
                                                disabled:opacity-50 disabled:cursor-wait font-medium"
                                        >
                                            {isTagFetching ? 'Loading…' : 'Load more'}
                                        </button>
                                    )}
                                </>
                            )}

                            {isTagFetching && tagResults.length === 0 && (
                                <p className="text-text-dim text-center py-8">Searching…</p>
                            )}
                        </div>
                    )}
                </section>
            </div>
        </>
    );
}