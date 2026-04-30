import { useMutation, useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { NavigationBar } from "../components/NavigationBar"
import { SearchBox } from "../components/SearchBox"
import { GameCard } from "../components/GameCard"
import { searchGamesGamesSearchGetOptions, getProfileRecommendationsRecommendProfilePostMutation } from "../client/@tanstack/react-query.gen"
import type { GameSearchResult, GameRecommendation } from "../client"
import { useProfileGames } from "../hooks/useProfileGames"
import { useDebouncedQuery } from "../hooks/useDebouncedQuery"

export default function Profile() {
    const { savedGames, addGame: addToProfile, removeGame: removeFromProfile, updateHours } = useProfileGames()

    const { query, setQuery, debouncedQuery } = useDebouncedQuery()

    const { data: suggestions = [] } = useQuery({
        ...searchGamesGamesSearchGetOptions({ query: { q: debouncedQuery } }),
        enabled: debouncedQuery.length > 0,
    })

    // Filter out games already in the list
    const filteredSuggestions = suggestions.filter(
        (s) => !savedGames.some((g) => g.app_id === s.app_id)
    )

    const addGame = (game: GameSearchResult) => {
        addToProfile(game)
        setQuery("")
    }

    const removeGame = (app_id: number) => {
        removeFromProfile(app_id)
        reset()
    }

    // ── Recommendations ──
    const { mutate, reset, data: recData, isPending, isError } = useMutation(
        getProfileRecommendationsRecommendProfilePostMutation()
    )

    const fetchRecommendations = () => {
        if (savedGames.length === 0) return
        mutate({
            body: {
                app_ids: savedGames.map((g) => g.app_id),
                hours_played: savedGames.map((g) => g.hours),
                top_n: 10,
            },
        })
    }

    const recommendations: GameRecommendation[] = recData?.recommendations ?? []

    return (
        <>
            <NavigationBar />
            <div className="flex flex-col p-10 max-w-4xl mx-auto">
                <h1 className="text-3xl font-semibold mb-12">My Game Profile</h1>
                <div className="mb-8">
                    <SearchBox
                        query={query}
                        onQueryChange={setQuery}
                        suggestions={filteredSuggestions}
                        showSuggestions={query.length > 0}
                        onSelectGame={addGame}
                    />
                </div>

                {savedGames.length > 0 && (
                    <div className="mb-8">
                        <h2 className="text-lg font-medium text-text-dim mb-3">Games played</h2>
                        <div className="flex flex-col gap-2">
                            {savedGames.map((game) => (
                                <div
                                    key={game.app_id}
                                    className="flex items-center gap-3 border p-3 rounded-lg bg-surface border-border"
                                >
                                    <Link to={`/games/${game.app_id}`} className="truncate flex-1 hover:text-accent transition-colors">
                                        {game.game_name}
                                    </Link>

                                    <label className="flex items-center gap-1.5 text-sm text-text-dim shrink-0">
                                        Hours
                                        <input
                                            type="number"
                                            min={0}
                                            value={game.hours}
                                            onChange={(e) => updateHours(game.app_id, Math.max(0, Number(e.target.value)))}
                                            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none
                                            w-20 bg-bg border border-border rounded px-2 py-1 text-text outline-none focus:border-accent"
                                        />
                                    </label>

                                    <button
                                        onClick={() => removeGame(game.app_id)}
                                        className="text-text-dim hover:text-red-400 transition-colors text-xl leading-none cursor-pointer"
                                        aria-label={`Remove ${game.game_name}`}
                                    >
                                        ✕
                                    </button>
                                </div>
                            ))}
                        </div>

                        <button
                            onClick={fetchRecommendations}
                            disabled={isPending}
                            className="mt-4 px-6 py-2.5 bg-accent text-white rounded-lg font-medium
                                       hover:brightness-110 disabled:opacity-50 transition-all cursor-pointer"
                        >
                            {isPending ? "Loading…" : "Get Recommendations"}
                        </button>
                    </div>
                )}

                {savedGames.length === 0 && (
                    <p className="text-text-dim text-center mt-10">Search and add games above to build your profile.
                        <br />Some games won't get recommendations because they are not in the CF dataset.</p>
                )}

                {isError && (
                    <p className="text-red-400 mt-4">Could not load recommendations. Please try again.</p>
                )}

                {recommendations.length > 0 && (
                    <div className="mt-2">
                        <h2 className="text-lg font-medium text-text-dim mb-3">Recommended for you</h2>
                        <div className="flex flex-col gap-2">
                            {recommendations.map((rec) => (
                                <GameCard
                                    key={rec.app_id}
                                    appId={rec.app_id}
                                    gameName={rec.game_name}
                                    headerImage={rec.header_image}
                                    score={rec.hybrid_score}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}