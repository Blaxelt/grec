import type { RecommendationResponse } from '../client'
import { GameCard } from './GameCard'

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
    )
}
