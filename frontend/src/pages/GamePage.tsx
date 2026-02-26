import { useParams } from 'react-router-dom'
import { getGameGamesGameIdGetOptions } from '../client/@tanstack/react-query.gen'
import { useQuery } from '@tanstack/react-query'

export default function GamePage() {
    const { id } = useParams<{ id: string }>()

    const { data: game, isLoading, isError } = useQuery({
        ...getGameGamesGameIdGetOptions({ path: { game_id: Number(id) } }),
        enabled: !!id,
    })

    if (isLoading) return <p>Loading...</p>
    if (isError || !game) return <p>Game not found.</p>

    return (
        <div className="game-page">
            <h1>{game.game_name}</h1>
            <div className="game-info">
                <img className="game-header-image" src={game.header_image} alt='No header image available' />

                <div className="game-details">
                    <p className="game-description">{game.short_description}</p>

                    <div className="game-meta">
                        <p><strong>Genres:</strong> {game.genres.join(', ')}</p>
                    </div>

                    <div className="game-meta">
                        <p><strong>Tags:</strong> {game.tags.join(', ')}</p>
                    </div>
                </div>
            </div>

            {game.screenshots.length > 0 && (
                <div className="screenshots-section">
                    <h2>Screenshots</h2>
                    <div className="screenshots-grid">
                        {game.screenshots.map((url, i) => (
                            <img
                                key={i}
                                className="screenshot-img"
                                src={url}
                                alt={`${game.game_name} screenshot ${i + 1} no available`}
                                loading="lazy"
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
