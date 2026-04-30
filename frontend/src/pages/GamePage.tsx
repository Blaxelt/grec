import { useParams } from 'react-router-dom'
import { getGameGamesAppIdGetOptions } from '../client/@tanstack/react-query.gen'
import { useQuery } from '@tanstack/react-query'
import { NavigationBar } from '../components/NavigationBar'
import { GameCard } from '../components/GameCard'
import { useProfileGames } from '../hooks/useProfileGames'

export default function GamePage() {
    const { id } = useParams<{ id: string }>()
    const { addGame, hasGame } = useProfileGames()

    const { data: game, isLoading, isError } = useQuery({
        ...getGameGamesAppIdGetOptions({ path: { app_id: Number(id) } }),
        enabled: !!id,
    })

    if (isLoading) return <p className="text-text-dim mt-8 text-center">Loading...</p>
    if (isError || !game) return <p className="text-text-dim mt-8 text-center">Game not found.</p>

    const alreadySaved = hasGame(game.app_id)

    return (
        <>
            <NavigationBar />
            <div className="flex flex-col p-10" >
                <h1 className="text-3xl font-semibold">{game.game_name}</h1>
                <div className="flex flex-col md:flex-row gap-6 mt-6 h-52">
                    <img className="rounded-xl shadow-lg shadow-black/50" src={game.header_image ?? undefined} alt='No header image available' />

                    <div className="flex flex-col gap-4 overflow-y-auto pr-2" data-testid="game-desc">
                        <p>{game.short_description}</p>

                        <div>
                            <p><strong>Genres:</strong> {game.genres.join(', ')}</p>
                        </div>

                        <div>
                            <p><strong>Tags:</strong> {game.tags.join(', ')}</p>
                        </div>
                    </div>

                </div>

                <div className="mt-9">
                    <button
                        onClick={() => addGame({ app_id: game.app_id, game_name: game.game_name, header_image: game.header_image })}
                        disabled={alreadySaved}
                        className={`px-3 py-2 rounded-lg font-medium transition-all cursor-pointer
                            ${alreadySaved
                                ? 'bg-surface border border-border text-text-dim cursor-default'
                                : 'bg-accent text-white hover:brightness-110'}`}
                    >
                        {alreadySaved ? '✓ In library' : 'Add to library'}
                    </button>
                </div>

                {(game.screenshots ?? []).length > 0 && (
                    <div className="mt-9">
                        <h2 className="mb-3 font-semibold text-xl">Screenshots</h2>
                        <div className="grid grid-cols-screenshots gap-3">
                            {(game.screenshots ?? []).map((url, i) => (
                                <img
                                    key={i}
                                    className="rounded-lg shadow-md shadow-black/30"
                                    src={url}
                                    alt={`${game.game_name} screenshot ${i + 1} not available`}
                                    loading="lazy"
                                />
                            ))}
                        </div>
                    </div>
                )}

                {(game.other_players_also_played ?? []).length > 0 && (
                    <div className="mt-9" data-testid="recommendations">
                        <h2 className="mb-3 font-semibold text-xl">Other players also played</h2>
                        <div className="grid grid-cols-screenshots gap-3">
                            {(game.other_players_also_played ?? []).map((rec) => (
                                <GameCard
                                    key={rec.app_id}
                                    appId={rec.app_id}
                                    gameName={rec.game_name}
                                    headerImage={rec.header_image}
                                    variant="image-only"
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}
