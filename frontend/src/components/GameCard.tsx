import { Link } from 'react-router-dom'

type Props = {
    appId: number
    gameName: string
    headerImage?: string | null
    score?: number
    tags?: string[]
    variant?: 'row' | 'image-only'
}

export function GameCard({ appId, gameName, headerImage, score, tags, variant = 'row' }: Props) {
    if (variant === 'image-only') {
        return (
            <Link to={`/games/${appId}`}>
                <img
                    className="rounded-lg shadow-md shadow-black/30"
                    src={headerImage ?? undefined}
                    alt={`${gameName} not available`}
                    loading="lazy"
                />
            </Link>
        )
    }

    return (
        <Link
            to={`/games/${appId}`}
            data-testid="result-card"
            className="flex items-center gap-3 border p-3 rounded-lg bg-surface border-border hover:border-accent transition-all duration-200"
        >
            <img
                src={headerImage ?? undefined}
                alt={gameName}
                className="w-40 h-20 object-cover shrink-0 rounded-lg"
            />
            <div className="flex flex-col gap-1.5 flex-1 min-w-0">
                <span className="truncate">{gameName}</span>
                {tags && tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                        {tags.slice(0, 6).map((tag) => (
                            <span
                                key={tag}
                                className={`text-xs px-2 py-0.5 rounded-full border bg-white/5 border-border text-text`}
                            >
                                {tag}
                            </span>
                        ))}
                        {tags.length > 6 && (
                            <span className="text-xs text-text px-1">...</span>
                        )}
                    </div>
                )}
            </div>
            {score !== undefined && (
                <span className="ml-auto mr-1.5 text-accent shrink-0">{(score * 100).toFixed(1)}%</span>
            )}
        </Link>
    )
}
