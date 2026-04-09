import { Link } from 'react-router-dom'
import type { RecommendationResponse } from '../client'

type Props = {
    isLoading: boolean
    isError: boolean
    data: RecommendationResponse | undefined
}

export function RecommendationList({ isLoading, isError, data }: Props) {
    if (isLoading) return <p className="text-text-dim mt-8 text-center">Finding similar games...</p>

    if (isError) return <p className="text-text-dim mt-8 text-center">Could not load recommendations.</p>

    if (!data || data.recommendations.length === 0) return null

    return (
        <div className="mt-10 max-w-2xl w-full">
            <h2 className="text-text-dim mb-3 text-sm">Games you might also like based on {data.target_game}</h2>
            <div className="flex flex-col gap-2" data-testid="results-list">
                {data.recommendations.map((rec) => (
                    <Link key={rec.app_id} to={`/games/${rec.app_id}`} className="flex items-center gap-3
                    border p-3 rounded-lg bg-surface border-border hover:border-accent transition-all duration-200">
                        <img
                            src={rec.header_image ?? undefined}
                            alt={rec.game_name}
                            className="w-40 h-20 object-cover shrink-0 rounded-lg"
                        />
                        <span className="ml-1.5 truncate flex-1">{rec.game_name}</span>
                        <span className="ml-auto mr-1.5 text-accent">{(rec.hybrid_score * 100).toFixed(1)}%</span>
                    </Link>
                ))}
            </div>
        </div>
    )
}
