import type { GameSearchResult } from '../client'

type Props = {
    query: string
    onQueryChange: (value: string) => void
    suggestions: GameSearchResult[]
    showSuggestions: boolean
    onSelectGame: (game: GameSearchResult) => void
}

export function SearchBox({ query, onQueryChange, suggestions, showSuggestions, onSelectGame }: Props) {
    return (
        <div className="relative w-full">
            <input
                type="text"
                placeholder="Search for a game..."
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                className="bg-surface w-full border border-border rounded-lg p-2.5 outline-none focus:border-accent hover:border-accent
                placeholder:text-text-dim"
            />

            {showSuggestions && suggestions.length > 0 && (
                <ul className="absolute left-0 right-0 top-[calc(100%+4px)] bg-surface border border-border rounded-lg z-10 overflow-hidden"
                    data-testid="suggestions">
                    {suggestions.map((g) => (
                        <li key={g.game_name}>
                            <button onClick={() => onSelectGame(g)} className="cursor-pointer w-full text-left hover:bg-accent p-2.5">
                                {g.game_name}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
