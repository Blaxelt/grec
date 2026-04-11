import { useParams } from 'react-router-dom'
import { getGameGamesAppIdGetOptions } from '../client/@tanstack/react-query.gen'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

export default function GamePage() {
    const { id } = useParams<{ id: string }>()

    const { data: game, isLoading, isError } = useQuery({
        ...getGameGamesAppIdGetOptions({ path: { app_id: Number(id) } }),
        enabled: !!id,
    })

    if (isLoading) return <p className="text-text-dim mt-8 text-center">Loading...</p>
    if (isError || !game) return <p className="text-text-dim mt-8 text-center">Game not found.</p>

    return (
        <div className="flex flex-col p-10" >
            <h1 className="text-3xl font-semibold">{game.game_name}</h1>
            <div className="flex flex-col md:flex-row gap-6 mt-6 h-52">
                <img className="rounded-xl shadow-lg shadow-black/50" src={game.header_image ?? undefined} alt='No header image available' />

                <div className="flex flex-col gap-4 overflow-y-auto pr-2" data-testid="game-desc">
                    <p className="l">{game.short_description}</p>

                    <div>
                        <p><strong>Genres:</strong> {game.genres.join(', ')}</p>
                    </div>

                    <div>
                        <p><strong>Tags:</strong> {game.tags.join(', ')}</p>
                    </div>
                </div>

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
                                alt={`${game.game_name} screenshot ${i + 1} no available`}
                                loading="lazy"
                            />
                        ))}
                    </div>
                </div>
            )}

            {(game.other_players_also_played ?? []).length > 0 && (
                <div className="mt-9">
                    <h2 className="mb-3 font-semibold text-xl">Other players also played</h2>
                    <div className="grid grid-cols-screenshots gap-3">
                        {(game.other_players_also_played ?? []).map((rec, i) => (
                            <Link key={rec.app_id} to={`/games/${rec.app_id}`}>
                                <img
                                    key={i}
                                    className="rounded-lg shadow-md shadow-black/30"
                                    src={rec.header_image ?? undefined}
                                    alt={`${rec.game_name} no available`}
                                    loading="lazy"
                                />
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
