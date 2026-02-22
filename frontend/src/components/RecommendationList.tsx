import type { RecommendationResponse } from '../client'

type Props = {
    isLoading: boolean
    isError: boolean
    data: RecommendationResponse | undefined
}

export function RecommendationList({ isLoading, isError, data }: Props) {
    if (isLoading) return <p className="loading">Finding similar games...</p>

    if (isError) return <p className="error">Could not load recommendations.</p>

    if (!data || data.recommendations.length === 0) return null

    return (
        <div className="results">
            <h2>Games similar to {data.target_game}</h2>
            <div className="results-list">
                {data.recommendations.map((rec, i) => (
                    <div key={i} className="result-card">
                        <img
                            src={rec.header_image}
                            alt={rec.game_name}
                            className="result-image"
                        />
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
    )
}
