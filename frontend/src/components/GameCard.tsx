import { Link } from 'react-router-dom'

type Props = {
    appId: number
    gameName: string
    headerImage?: string | null
    score?: number
    variant?: 'row' | 'image-only'
}

export function GameCard({ appId, gameName, headerImage, score, variant = 'row' }: Props) {
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
            className="flex items-center gap-3 border p-3 rounded-lg bg-surface border-border hover:border-accent transition-all duration-200"
        >
            <img
                src={headerImage ?? undefined}
                alt={gameName}
                className="w-40 h-20 object-cover shrink-0 rounded-lg"
            />
            <span className="ml-1.5 truncate flex-1">{gameName}</span>
            {score !== undefined && (
                <span className="ml-auto mr-1.5 text-accent">{(score * 100).toFixed(1)}%</span>
            )}
        </Link>
    )
}
